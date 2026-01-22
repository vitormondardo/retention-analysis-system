from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Video, RetentionMetric
import pandas as pd
from django.utils import timezone
from django.db import transaction # <--- IMPORTANTE: Nova importação

@login_required
def upload_view(request):
    if request.method == 'POST':
        arquivo = request.FILES.get('arquivo_csv')
        
        if arquivo:
            try:
                print("1. Iniciando leitura do arquivo...") # Log no terminal
                
                if arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                print(f"2. Arquivo lido. Total de linhas: {len(df)}") # Log
                
                mapa_colunas = {
                    'Hashtags': 'titulo',
                    'Video Topic': 'topico',
                    'Date Published': 'data_upload',
                    'Duration (s)': 'duracao',
                    'Average Watch Time (s)': 'tempo_medio',
                    'Avg. % Watched': 'retencao_perc',
                    'GMV': 'vendas'
                }
                
                df.rename(columns=mapa_colunas, inplace=True)
                
                registros_salvos = 0
                linhas_ignoradas = 0
                
                # --- O SEGREDO DA VELOCIDADE ESTÁ AQUI ---
                # O 'atomic' segura as gravações na memória RAM e só salva no final.
                with transaction.atomic():
                    for index, row in df.iterrows():
                        # Imprime progresso a cada 50 linhas para você ver que não travou
                        if index % 50 == 0:
                            print(f"Processando linha {index}...")

                        try:
                            # --- Título e Tópico ---
                            titulo_raw = str(row.get('titulo', ''))
                            if titulo_raw == 'nan' or not titulo_raw.strip():
                                titulo_raw = f"Vídeo {index} (Sem legenda)"
                            
                            topico = str(row.get('topico', 'Geral'))
                            if topico == 'nan': topico = 'Geral'

                            # --- Duração ---
                            duracao = float(row.get('duracao', 0))
                            
                            # --- Data ---
                            data_pub = timezone.now()
                            if 'data_upload' in row and pd.notna(row['data_upload']):
                                try:
                                    data_pub = pd.to_datetime(row['data_upload'], errors='coerce')
                                    if pd.isna(data_pub): data_pub = timezone.now()
                                except: pass

                            # --- Vendas ---
                            vendeu = False
                            if 'vendas' in row and pd.notna(row['vendas']):
                                try:
                                    valor = float(row['vendas'])
                                    if valor > 0: vendeu = True
                                except: pass
                            
                            # --- SALVAR VÍDEO ---
                            video_obj, created = Video.objects.get_or_create(
                                title=titulo_raw[:200],
                                defaults={
                                    'platform': 'tiktok',
                                    'duration_seconds': int(duracao),
                                    'upload_date': data_pub,
                                    'description': f"Tópico: {topico}"
                                }
                            )
                            
                            # --- SALVAR MÉTRICA ---
                            RetentionMetric.objects.create(
                                video=video_obj,
                                avg_watch_time=float(row.get('tempo_medio', 0)),
                                retention_score=float(row.get('retencao_perc', 0)),
                                converted=vendeu
                            )
                            registros_salvos += 1
                            
                        except Exception as e_linha:
                            print(f"Erro na linha {index}: {e_linha}")
                            linhas_ignoradas += 1
                            continue
                
                print("3. Processo finalizado com sucesso!")
                return render(request, 'core/upload.html', {
                    'mensagens': f'Concluído! ✅ {registros_salvos} vídeos importados. (Ignorados: {linhas_ignoradas})'
                })
                
            except Exception as e:
                print(f"ERRO CRÍTICO: {e}")
                return render(request, 'core/upload.html', {
                    'mensagens': f'Erro crítico ao ler arquivo: {str(e)}'
                })
    
    return render(request, 'core/upload.html')
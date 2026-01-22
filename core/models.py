from django.db import models
# Create your models here.
#CLASSE VÍDEO
class Video(models.Model):
    #OPÇÕES PARA O CAMPO PLATAFORMA - INTEGRIDADE DE DADOS
    PLATFORM_CHOICES = [
        ('tiktok', 'TikTok'),
        ('reels', 'Instagram Reels'),
        ('shorts', 'YouTube Shorts'),
    ]
    #CAMPOS DA TABELA VÍDEO
    title = models.CharField(max_length=200, verbose_name="Título")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name="Plataforma")
    duration_seconds = models.IntegerField(verbose_name="Duração (segundos)") #verbose_name é o nome que aparece no admin
    upload_date = models.DateField(auto_now_add=True, verbose_name="Data de Uplodad") #auto_now_add automação data atual
    description = models.TextField(blank=True, null=True, verbose_name="Descriçãp/Notas") #blank e null permitem campo vazio

    #MÉTODO PARA REPRESENTAÇÃO EM STRING DO OBJETO
    def __str__(self):
        return f"{self.title} - {self.platform}"
    #META INFORMAÇÕES DA TABELA
    class Meta:
        verbose_name = "Vídeo"
        verbose_name_plural = "Vídeos"
        ordering = ['-upload_date']  # Orde nar por data de upload decrescente
        

#CLASSE RETENÇÃO
class RetentionMetric(models.Model):
    #DADOS FRIOS DOS VÍDEOS 
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="metrics")

    avg_watch_time = models.FloatField(verbose_name="Tempo Médio de Visualização (segundos)")
    retention_score = models.FloatField(verbose_name="Pontuação de Retenção (%)")
    #conversão de vendas
    converted = models.BooleanField(default=False, verbose_name="Gerou Conversão/Venda?") #default valor padrão
    # Espaço para a IA salvar a previsão dela no futuro
    ai_prediction = models.TextField(blank=True, null=True, verbose_name="Previsão da IA")

    def __str__(self):
        return f"Métrica do vídeo: {self.video.title}"
    
    class Meta:
        verbose_name = 'Métrica de Retenção'
        verbose_name_plural = 'Métricas de Retenção'
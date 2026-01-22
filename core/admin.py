from django.contrib import admin
from .models import Video, RetentionMetric

#   VISUALIZAÇÃO BONITA DO VIDEO
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'duration_seconds', 'upload_date') #campos que aparecem na lista
    list_filter = ('platform',) #filtros laterais
    search_fields = ('title',) #barra de pesquisa

@admin.register(RetentionMetric)
class RetentionMetricAdmin(admin.ModelAdmin):
    list_display = ('video', 'retention_score', 'converted', 'avg_watch_time')
    list_filter = ('converted',)
from django.contrib import admin
from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'cluster',
        'get_cluster_name',
        'nombre_classes_2009',
        'total_students',
        'latitude',
        'longitude',
        'created_at'
    ]
    list_filter = ['cluster', 'created_at']
    search_fields = ['name', 'id']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name',)
        }),
        ('Features', {
            'fields': (
                'nombre_classes_2009',
                'eleves_premier',
                'eleves_superieur',
                'latitude',
                'longitude'
            )
        }),
        ('Cluster Assignment', {
            'fields': ('cluster',)
        }),
    )
 

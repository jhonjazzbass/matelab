from django.contrib import admin
from .models import Biblioteca

@admin.register(Biblioteca)
class BibliotecaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('titulo', 'descripcion')
    list_editable = ('activo',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'activo')
        }),
        ('Auditoría', {
            'fields': ('usuario',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Solo para nuevos objetos
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

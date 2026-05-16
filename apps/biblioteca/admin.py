from django.contrib import admin
from .models import Biblioteca, PolyaBiblioteca, Sumandos_Biblioteca

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


@admin.register(PolyaBiblioteca)
class PolyaBibliotecaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'biblioteca', 'identificacion_operacion', 'created_at', 'updated_at')
    list_filter = ('identificacion_operacion', 'created_at')
    search_fields = ('usuario__nombre_usuario', 'biblioteca__titulo')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Relaciones', {
            'fields': ('usuario', 'biblioteca')
        }),
        ('Paso 1: Comprender el problema', {
            'fields': ('identificacion_operacion', 'por_que_esa_operacion', 'que_se_pide', 
                      'datos_conocidos', 'incognitas', 'representacion')
        }),
        ('Paso 2: Planificar la estrategia', {
            'fields': ('estrategia_principal',)
        }),
        ('Paso 3: Ejecutar el plan', {
            'fields': ('desarrollo', 'resultados_intermedios')
        }),
        ('Paso 4: Verificar y revisar', {
            'fields': ('revision_verificacion', 'comprobacion_otro_metodo', 
                      'conclusion_final', 'confianza')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Sumandos_Biblioteca)
class SumandosBibliotecaAdmin(admin.ModelAdmin):
    list_display = ('sumando_id', 'polya_biblioteca', 'sumando')
    list_filter = ('polya_biblioteca',)
    search_fields = ('sumando',)

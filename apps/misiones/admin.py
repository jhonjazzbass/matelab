from django.contrib import admin
from .models import Habilidad, Mision, IntentoMision, ProgresoHabilidad, PolyaTrabajoUM

@admin.register(Habilidad)
class HabilidadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Mision)
class MisionAdmin(admin.ModelAdmin):
    # Añadimos nivel_dificultad para gestionar la progresión
    list_display = ('titulo', 'habilidad', 'tipo_operacion', 'nivel_dificultad', 'activa')
    list_filter = ('nivel_dificultad', 'habilidad', 'tipo_operacion', 'activa')
    search_fields = ('titulo', 'descripcion')
    date_hierarchy = 'fecha_creacion'

@admin.register(IntentoMision)
class IntentoMisionAdmin(admin.ModelAdmin):
    # Aquí visualizas el rendimiento bruto: tiempo y errores
    list_display = ('usuario', 'mision', 'estado', 'tiempo_total_segundos', 'intentos_fallidos', 'fecha_intento')
    list_filter = ('estado', 'fecha_intento', 'mision__nivel_dificultad')
    search_fields = ('usuario__nombre_usuario', 'mision__titulo')
    date_hierarchy = 'fecha_intento'

@admin.register(PolyaTrabajoUM)
class PolyaTrabajoUMAdmin(admin.ModelAdmin):
    # Esta es la vista clave para la tesis: el desglose por fases de Pólya
    list_display = ('usuario', 'mision', 'tiempo_fase_1_segundos', 'tiempo_fase_2_segundos', 'tiempo_fase_3_segundos', 'tiempo_fase_4_segundos', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('usuario__nombre_usuario', 'mision__titulo')

@admin.register(ProgresoHabilidad)
class ProgresoHabilidadAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'habilidad', 'porcentaje_avance', 'ultima_actualizacion')
    list_filter = ('habilidad', 'ultima_actualizacion')
    search_fields = ('usuario__nombre_usuario', 'habilidad__nombre')
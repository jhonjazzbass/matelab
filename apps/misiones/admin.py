from django.contrib import admin
from .models import Habilidad, Mision, IntentoMision, ProgresoHabilidad

@admin.register(Habilidad)
class HabilidadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Mision)
class MisionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'habilidad', 'fecha_creacion', 'activa')
    list_filter = ('habilidad', 'activa', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion')
    date_hierarchy = 'fecha_creacion'

@admin.register(IntentoMision)
class IntentoMisionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mision', 'estado', 'fecha_intento')
    list_filter = ('estado', 'fecha_intento')
    search_fields = ('usuario__username', 'mision__titulo')
    date_hierarchy = 'fecha_intento'

@admin.register(ProgresoHabilidad)
class ProgresoHabilidadAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'habilidad', 'porcentaje_avance', 'ultima_actualizacion')
    list_filter = ('habilidad', 'ultima_actualizacion')
    search_fields = ('usuario__username', 'habilidad__nombre')

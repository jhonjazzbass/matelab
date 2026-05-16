from django.urls import path
from . import views

app_name = 'misiones'

urlpatterns = [
    path('', views.lista_misiones, name='misiones'),
    path('api/misiones/<int:mision_id>/intentos/', views.obtener_intentos_mision, name='obtener_intentos_mision'),
    path('api/misiones/intentos/<int:intento_id>/', views.actualizar_estado_intento, name='actualizar_estado_intento'),
    path('api/misiones/<int:mision_id>/alternativas/', views.obtener_alternativas_mision, name='obtener_alternativas_mision'),
    path('guardar-intento/', views.guardar_intento_mision, name='guardar_intento'),
    path('api/polya/<int:mision_id>/', views.obtener_polya_um, name='obtener_polya_um'),
    path('api/polya/<int:mision_id>/guardar/', views.guardar_polya_um, name='guardar_polya_um'),
    path('api/polya/<int:mision_id>/estudiante/<int:usuario_id>/', views.obtener_polya_um_estudiante, name='obtener_polya_um_estudiante'),
]
from django.urls import path
from . import views
from .views import GestionBibliotecaView

app_name = 'biblioteca'

urlpatterns = [
    path('', GestionBibliotecaView.as_view(), name='listar'),
    path('crear_contenido/', views.crear_contenido, name='crear_contenido'),
    path('<int:pk>/detalle/', views.detalle_contenido, name='detalle'),
    path('juego_operaciones/', views.juego_operaciones, name='juego_operaciones'),
    path('practica/', views.practica, name='practica'),
    path('marcar_contenido_visto/', views.marcar_contenido_visto, name='marcar_contenido_visto'),
    path('polya/guardar/', views.guardar_polya_biblioteca, name='guardar_polya'),
    path('polya/cargar/', views.cargar_polya_biblioteca, name='cargar_polya'),
]

from django.urls import path
from .views import DashboardsView, MisionesView, MapaProgresoView, OpcionesAprendizajeView,ReporteEstudiantesView
from .user_views import GestionUsuariosView, editar_usuario, eliminar_usuario
from ..biblioteca.views import GestionBibliotecaView, actualizar_contenido, eliminar_contenido

urlpatterns = [
    path(
        "",
        DashboardsView.as_view(template_name="dashboard_student.html"),
        name="index",
    ),
    path(
        "gestion-usuarios/",
        GestionUsuariosView.as_view(),
        name="gestion-usuarios",
    ),
    path(
        "gestion-usuarios/editar/",
        editar_usuario,
        name="editar_usuario",
    ),
    path(
        "gestion-usuarios/eliminar/",
        eliminar_usuario,
        name="eliminar_usuario",
    ),
    path(
        "gestion-biblioteca/",
        GestionBibliotecaView.as_view(),
        name="gestion-biblioteca",
    ),
    path(
        "gestion-biblioteca/editar/",
        actualizar_contenido,
        name="editar_biblioteca",
    ),
    path(
        "gestion-biblioteca/eliminar/",
        eliminar_contenido,
        name="eliminar_biblioteca",
    ),
    path(
        "mapa-progreso/",
        MapaProgresoView.as_view(template_name="dashboards/mapa_progreso.html"),
        name="mapa_progreso",
    ),
    path(
        "aprendizaje/",
        OpcionesAprendizajeView.as_view(),
        name="opciones_aprendizaje",
    ),
    path(
        "reportes-estudiantes/",
        DashboardsView.as_view(template_name="reportes_estudiantes.html"),
        name="reportes-estudiantes",
    ),
      path(
        "reporte-estudiantes/",
        ReporteEstudiantesView.as_view(),
        name="reporte_estudiantes",
    ),
]

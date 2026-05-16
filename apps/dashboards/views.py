from django.views.generic import TemplateView, ListView, View
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render
from web_project import TemplateLayout
from apps.authentication.models import Usuarios, Rol
from apps.misiones.models import Mision, IntentoMision
from apps.misiones.models import Habilidad
from apps.biblioteca.models import Biblioteca, Biblioteca_Contenido
"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardsView(TemplateView):
    def get_template_names(self):
        # Check if user is authenticated
        if not self.request.user.is_authenticated:
            return ['dashboards/login.html']  # Or your login template
        if self.template_name=='reportes_estudiantes.html':
            return ['reportes_estudiantes.html']
            
        # Get user role
        user_role = getattr(self.request.user.rol, 'tipo', '').lower() if hasattr(self.request.user, 'rol') else ''
        
        # Return template based on role
        if user_role == 'estudiante':
            return ['dashboard_student.html']
        elif user_role == 'profesor':
            return ['welcome_profesor.html']
        elif user_role == 'admin' or user_role == 'administrador':
            return ['welcome_admin.html'] 

    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Obtener el usuario actual
        user = self.request.user
        
        # Obtener estadísticas de misiones
        from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
        from django.utils import timezone
        from datetime import timedelta
        
        # Fechas para el cálculo semanal
        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        semana_pasada_inicio = inicio_semana - timedelta(weeks=1)
        semana_pasada_fin = fin_semana - timedelta(weeks=1)
        
        # Obtener todas las misiones
        misiones = Mision.objects.all()
        
        # Obtener intentos del usuario
        intentos_usuario = IntentoMision.objects.filter(usuario=user)
        
        # Calcular estadísticas generales
        total_misiones = misiones.count()
        misiones_completadas = intentos_usuario.filter(estado='completado').values('mision').distinct().count()
        misiones_en_progreso = intentos_usuario.filter(estado='en_progreso').values('mision').distinct().count()
        misiones_pendientes = max(total_misiones - misiones_completadas - misiones_en_progreso, 0)
        total_habilidades = Habilidad.objects.count()
        
        # Calcular tasa de éxito (éxitos / total de intentos)
        total_intentos = intentos_usuario.count()
        exitos = intentos_usuario.filter(estado='completado').count()
        tasa_exito = round((exitos / total_intentos * 100), 1) if total_intentos > 0 else 0

        # Calcular porcentajes de misiones por estado
        if total_misiones > 0:
            porcentaje_completadas = round((misiones_completadas / total_misiones * 100), 1)
            porcentaje_en_progreso = round((misiones_en_progreso / total_misiones * 100), 1)
            porcentaje_pendientes = round((misiones_pendientes / total_misiones * 100), 1)
        else:
            porcentaje_completadas = 0
            porcentaje_en_progreso = 0
            porcentaje_pendientes = 0
        
        # Calcular progreso semanal
        misiones_semana_actual = intentos_usuario.filter(
            estado='completado',
            fecha_intento__date__range=[inicio_semana, fin_semana]
        ).count()
        
        misiones_semana_anterior = intentos_usuario.filter(
            estado='completado',
            fecha_intento__date__range=[semana_pasada_inicio, semana_pasada_fin]
        ).count()
        
        # Calcular tendencia
        if misiones_semana_anterior > 0:
            diferencia = misiones_semana_actual - misiones_semana_anterior
            misiones_tendencia_porcentaje = abs(round((diferencia / misiones_semana_anterior) * 100))
            misiones_tendencia_texto = 'aumento' if diferencia >= 0 else 'disminución'
            misiones_tendencia_clase = 'success' if diferencia >= 0 else 'danger'
        else:
            misiones_tendencia_porcentaje = 0
            misiones_tendencia_texto = 'sin cambios'
            misiones_tendencia_clase = 'secondary'
        
        # Obtener todas las habilidades y verificar si el usuario las tiene
        from apps.misiones.models import ProgresoHabilidad
        
        # Obtener todas las habilidades con el progreso del usuario
        habilidades = []
        for habilidad in Habilidad.objects.all():
            progreso = ProgresoHabilidad.objects.filter(
                usuario=user,
                habilidad=habilidad
            ).first()
            
            habilidades.append({
                'nombre': habilidad.nombre,
                'tiene_habilidad': progreso is not None and progreso.porcentaje_avance > 0,
                'porcentaje_avance': progreso.porcentaje_avance if progreso else 0
            })
        
        # Agregar datos al contexto
        context.update({
            'misiones_totales': total_misiones,
            'misiones_completadas': misiones_completadas,
            'misiones_en_progreso': misiones_en_progreso,
            'misiones_pendientes': misiones_pendientes,
            'total_habilidades': total_habilidades,
            'tasa_exito': tasa_exito,
            'porcentaje_completado': round((misiones_completadas / total_misiones * 100), 1) if total_misiones > 0 else 0,
            'porcentaje_completadas': porcentaje_completadas,
            'porcentaje_en_progreso': porcentaje_en_progreso,
            'porcentaje_pendientes': porcentaje_pendientes,
            'misiones_semana_actual': misiones_semana_actual,
            'misiones_semana_anterior': misiones_semana_anterior,
            'misiones_tendencia_porcentaje': misiones_tendencia_porcentaje,
            'misiones_tendencia_texto': misiones_tendencia_texto,
            'misiones_tendencia_clase': misiones_tendencia_clase,
            'habilidades_usuario': habilidades,
        })
        
        return context


class MisionesView(TemplateView):
    template_name = 'dashboards/misiones.html'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Aquí puedes agregar datos adicionales al contexto si es necesario
        return context


class MapaProgresoView(TemplateView):
    template_name = 'dashboards/mapa_progreso.html'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Get the logged-in user
        user = self.request.user
        
        # Get all missions with their attempts
        misiones = Mision.objects.prefetch_related(
            'intentomision_set'
        ).all().order_by('fecha_creacion')
        
        # Calculate progress
        total_misiones = misiones.count()
        misiones_completadas = 0
        misiones_con_estado = []
        
        for mision in misiones:
            # Get all attempts for this mission and user
            intentos = mision.intentomision_set.filter(usuario=user).order_by('-fecha_intento')
            ultimo_intento = intentos.first() if intentos.exists() else None
            
            # Determine mission status
            if intentos.filter(estado='completado').exists():
                estado = 'completado'
                misiones_completadas += 1
            elif intentos.filter(estado='en_progreso').exists():
                estado = 'en_progreso'
            elif intentos.filter(estado='rechazado').exists():
                estado = 'rechazado'
            else:
                estado = 'no_iniciada'
            
            # Add status to mission object
            mision.estado = estado
            mision.ultimo_intento = ultimo_intento
            misiones_con_estado.append(mision)
        
        # Calculate overall progress
        porcentaje_total = int((misiones_completadas / total_misiones * 100)) if total_misiones > 0 else 0
        
        # Add data to context
        context.update({
            'misiones': misiones_con_estado,
            'porcentaje_total': porcentaje_total,
            'total_misiones': total_misiones,
            'misiones_completadas': misiones_completadas,
        })
        
        return context


class OpcionesAprendizajeView(TemplateView):
    template_name = 'dashboards/biblioteca.html'
    
    def get_context_data(self, **kwargs):
        
        
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Get all active biblioteca items
        contenidos = Biblioteca.objects.filter(activo=True).order_by('tipo', 'titulo')
        contenidos_con_detalle = (
            contenidos
            .filter(tipo='Contenido')
            .select_related('detalle_contenido')
        )
        # Group by type
        contenidos_por_tipo = {
            'Contenido': contenidos_con_detalle,
            'Juego': contenidos.filter(tipo='Juego'),
            'Practica': contenidos.filter(tipo='Practica')
        }
        
        context.update({
            'contenidos_por_tipo': contenidos_por_tipo, 
            'total_contenidos': contenidos.count()
        })
        
        return context


class ReporteEstudiantesView(TemplateView):
    template_name = 'reportes_estudiantes.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Get all active students with related data
        estudiantes = Usuarios.objects.filter(
            rol__tipo='Estudiante', 
            estado=True
        ).select_related('rol').prefetch_related(
            'intentomision_set',
            'progresohabilidad'
        )
        
        # Get search parameters
        query = self.request.GET.get('q', '')
        
        # Apply filters
        if query:
            estudiantes = estudiantes.filter(
                Q(nombre_usuario__icontains=query) |
                Q(usuario_id__icontains=query)
            )
        
        estudiantes_data = []
        for estudiante in estudiantes:
            intentos = estudiante.intentomision_set.all()
            
            misiones_completadas = intentos.filter(estado='completado').count()
            
            total_misiones = intentos.values('mision').distinct().count()
            
            progreso = (misiones_completadas / total_misiones * 100) if total_misiones > 0 else 0
            
            promedio = misiones_completadas / total_misiones * 10 if total_misiones > 0 else 0
            
            try:
                progreso_habilidad = getattr(estudiante, 'progresohabilidad', None)

                if progreso_habilidad is not None:
                    habilidades_data = [{
                        'nombre': progreso_habilidad.habilidad.nombre,
                        'porcentaje': progreso_habilidad.porcentaje_avance
                    }]
                else:
                    habilidades_data = []

            except ProgresoHabilidad.DoesNotExist:
                habilidades_data = []
            
            estudiantes_data.append({
                'estudiante': estudiante,
                'misiones_completadas': misiones_completadas,
                'total_misiones': total_misiones,
                'progreso': round(progreso, 1),
                'promedio': round(promedio, 1),
                'ultima_actividad': intentos.order_by('-fecha_intento').first(),
                'habilidades': habilidades_data
            })
        
        context['estudiantes_data'] = estudiantes_data
        context['query'] = query
        
        # Get all mission attempts for the table
        intentos_estudiantes = IntentoMision.objects.select_related(
            'usuario', 'mision'
        ).order_by('-fecha_intento')
        context['intentos_estudiantes'] = intentos_estudiantes
        
        return context
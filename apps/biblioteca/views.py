from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from web_project import TemplateLayout
from .models import Biblioteca
import random

class GestionBibliotecaView(TemplateView):
    template_name = 'gestion_biblioteca.html'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Get search parameters
        search_query = self.request.GET.get('buscar', '')
        tipo_filter = self.request.GET.get('tipo', '')
        activo_filter = self.request.GET.get('activo')
        
        # Get all biblioteca items with user information
        contenidos = Biblioteca.objects.select_related('usuario').all()
        
        # Apply filters
        if search_query:
            contenidos = contenidos.filter(
                Q(titulo__icontains=search_query) |
                Q(descripcion__icontains=search_query)
            )
            
        if tipo_filter:
            contenidos = contenidos.filter(tipo=tipo_filter)
            
        # Apply activo filter
        if activo_filter is not None:
            contenidos = contenidos.filter(activo=(activo_filter.lower() == 'true'))
        
        # Prepare data for the template
        contenidos_data = []
        for contenido in contenidos:
            contenidos_data.append({
                'id': contenido.id,
                'titulo': contenido.titulo,
                'descripcion': contenido.descripcion,
                'tipo': contenido.tipo,
                'activo': contenido.activo,
                'usuario': contenido.usuario.nombre_usuario if contenido.usuario else 'Sin usuario',
                })
        
        # Add data to context
        context.update({
            'contenidos': contenidos_data,
            'tipos': dict(Biblioteca.TIPO_CHOICES),
            'search_query': search_query,
            'selected_tipo': tipo_filter,
            'selected_activo': activo_filter if activo_filter is not None else ''
        })
        
        return context

 
@login_required
def crear_contenido(request):
    if request.method == 'POST':
        try:
            # Crear nuevo contenido
            contenido = Biblioteca.objects.create(
                titulo=request.POST.get('titulo'),
                descripcion=request.POST.get('descripcion'),
                tipo=request.POST.get('tipo'),
                activo=request.POST.get('activo', '1') == '1',
                usuario=request.user
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Contenido creado exitosamente',
                    'id': contenido.id
                })
            
            messages.success(request, 'Contenido creado exitosamente')
            return redirect('biblioteca:listar')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            
            messages.error(request, f'Error al crear el contenido: {str(e)}')
            return redirect('biblioteca:listar')
    
    return redirect('biblioteca:listar')

@login_required
def actualizar_contenido(request):
    try:
        data = request.POST
        user_id = data.get('id')
        
        if not user_id:
            return JsonResponse({'success': False, 'error': 'ID de usuario no proporcionado'}, status=400)
        
        try:
            biblioteca = Biblioteca.objects.get(id=user_id)
        except Biblioteca.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
        
        # Update user data
        biblioteca.titulo = data.get('titulo', biblioteca.titulo)
        biblioteca.descripcion = data.get('descripcion', biblioteca.descripcion)
        biblioteca.tipo = data.get('tipo', biblioteca.tipo)
        biblioteca.activo = data.get('activo', biblioteca.activo)
        
        biblioteca.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@login_required
def eliminar_contenido(request):
    try:
        data = request.POST
        user_id = data.get('id')
        
        if not user_id:
            return JsonResponse({'success': False, 'error': 'ID de usuario no proporcionado'}, status=400)
        
        try:
            biblioteca = Biblioteca.objects.get(id=user_id)
            biblioteca.delete()
            return JsonResponse({'success': True})
            
        except Biblioteca.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def detalle_contenido(request, pk):
    contenido = get_object_or_404(Biblioteca, pk=pk)
    
    data = {
        'id': contenido.id,
        'titulo': contenido.titulo,
        'descripcion': contenido.descripcion,
        'tipo': contenido.get_tipo_display(), 
        'activo': 'Sí' if contenido.activo else 'No',
        'fecha_creacion': contenido.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
        'usuario': contenido.usuario.get_full_name() if contenido.usuario else 'Anónimo'
    }
    
    return JsonResponse(data)


def juego_operaciones(request):
    titulo = request.GET.get('titulo', 'Juego de operaciones')
    descripcion = request.GET.get('descripcion')
    solucion = request.GET.get('solucion')
 
    solucion = int(solucion)
    
    if "suma" in descripcion.lower():
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        pregunta = descripcion
        respuesta_correcta = solucion
    elif "resta" in descripcion.lower():
        a = random.randint(10, 50)
        b = random.randint(1, a)
        pregunta = descripcion
        respuesta_correcta = solucion
    elif "multiplicación" in descripcion.lower() or "multiplicacion" in descripcion.lower():
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        pregunta = descripcion
        respuesta_correcta = solucion
    elif "división" in descripcion.lower() or "division" in descripcion.lower():
        b = random.randint(2, 10)
        respuesta_correcta = solucion
        a = b * respuesta_correcta
        pregunta = descripcion
    else: 
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        pregunta = descripcion
        respuesta_correcta = solucion
    
    opciones = [respuesta_correcta]
    while len(opciones) < 4:
        opcion = random.randint(max(1, respuesta_correcta - 10), respuesta_correcta + 10)
        if opcion not in opciones:
            opciones.append(opcion)
    
    random.shuffle(opciones)
    indice_correcto = opciones.index(respuesta_correcta)
    
    pregunta_data = {
        'pregunta': pregunta,
        'opciones': opciones,
        'respuesta_correcta': indice_correcto
    }
    
    context = {
        'titulo': titulo,
        'descripcion': descripcion,
        'solucion': solucion,
        'pregunta': pregunta_data
    }
    
    return render(request, 'juegos/operaciones_modal.html', context)


def practica(request):
    titulo = request.GET.get('titulo', 'Práctica de operaciones')
    descripcion = request.GET.get('descripcion')
    solucion = request.GET.get('solucion')
    
    solucion = int(solucion)

    context = {
        'titulo': titulo,
        'descripcion': descripcion,
        'solucion': solucion,
    }
    
    return render(request, 'practicas/practica.html', context)
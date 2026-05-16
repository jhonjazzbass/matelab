from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from web_project import TemplateLayout
from .models import Biblioteca, Biblioteca_Contenido, Biblioteca_Usuario, PolyaBiblioteca, Sumandos_Biblioteca
import random
import json

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
                'biblioteca_id': contenido.biblioteca_id,
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
            contenido_detalle_id = None
            if request.POST.get('tipo') == 'Contenido':
                teoria = request.POST.get('teoria', '')
                pasos_trucos = request.POST.get('pasos_trucos', '')
                ejemplo = request.POST.get('ejemplo', '')
                detalle = Biblioteca_Contenido.objects.create(
                    biblioteca=contenido,
                    teoria=teoria,
                    pasos_trucos=pasos_trucos,
                    ejemplo=ejemplo
                )
                contenido_detalle_id = detalle.biblioteca_contenido_id
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Contenido creado exitosamente',
                    'id': contenido.biblioteca_id,
                    'biblioteca_contenido_id': contenido_detalle_id
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
        biblioteca_id = data.get('biblioteca_id') or data.get('id')
        
        if not biblioteca_id:
            return JsonResponse({'success': False, 'error': 'ID de contenido no proporcionado'}, status=400)
        
        try:
            biblioteca = Biblioteca.objects.get(biblioteca_id=biblioteca_id)
        except Biblioteca.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Contenido no encontrado'}, status=404)
        
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
        biblioteca_id = data.get('biblioteca_id') or data.get('id')
        
        if not biblioteca_id:
            return JsonResponse({'success': False, 'error': 'ID de contenido no proporcionado'}, status=400)
        
        try:
            biblioteca = Biblioteca.objects.get(biblioteca_id=biblioteca_id)
            biblioteca.delete()
            return JsonResponse({'success': True})
            
        except Biblioteca.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Contenido no encontrado'}, status=404)
            
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


@login_required
@require_http_methods(["POST"])
def marcar_contenido_visto(request):
    try:
        biblioteca_id = request.POST.get('biblioteca_id') or request.GET.get('biblioteca_id')
        if not biblioteca_id:
            return JsonResponse({'success': False, 'message': 'biblioteca_id requerido'}, status=400)

        try:
            biblioteca = Biblioteca.objects.get(biblioteca_id=biblioteca_id)
        except Biblioteca.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Contenido de biblioteca no encontrado'}, status=404)

        obj, _created = Biblioteca_Usuario.objects.update_or_create(
            usuario=request.user,
            biblioteca=biblioteca,
            defaults={'estado': True}
        )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def guardar_polya_biblioteca(request):
    """Guarda o actualiza el trabajo de Pólya para un contenido de biblioteca"""
    try:
        biblioteca_id = request.POST.get('biblioteca_id')
        if not biblioteca_id:
            return JsonResponse({'success': False, 'message': 'biblioteca_id requerido'}, status=400)

        try:
            biblioteca = Biblioteca.objects.get(biblioteca_id=biblioteca_id)
        except Biblioteca.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Contenido de biblioteca no encontrado'}, status=404)

        # Obtener o crear el registro de Pólya
        polya, created = PolyaBiblioteca.objects.get_or_create(
            usuario=request.user,
            biblioteca=biblioteca
        )

        # Actualizar campos del método de Pólya
        polya.identificacion_operacion = request.POST.get('identificacion_operacion', '')
        polya.por_que_esa_operacion = request.POST.get('por_que_esa_operacion', '')
        polya.que_se_pide = request.POST.get('que_se_pide', '')
        polya.datos_conocidos = request.POST.get('datos_conocidos', '')
        polya.incognitas = request.POST.get('incognitas', '')
        polya.representacion = request.POST.get('representacion', '')
        polya.estrategia_principal = request.POST.get('estrategia_principal', '')
        polya.desarrollo = request.POST.get('desarrollo', '')
        polya.resultados_intermedios = request.POST.get('resultados_intermedios', '')
        polya.revision_verificacion = request.POST.get('revision_verificacion', '')
        polya.comprobacion_otro_metodo = request.POST.get('comprobacion_otro_metodo', '')
        polya.conclusion_final = request.POST.get('conclusion_final', '')
        
        confianza = request.POST.get('confianza')
        if confianza:
            try:
                polya.confianza = int(confianza)
            except ValueError:
                pass

        polya.save()

        # Guardar sumandos
        sumandos_json = request.POST.get('sumandos')
        if sumandos_json:
            try:
                sumandos_list = json.loads(sumandos_json)
                # Eliminar sumandos existentes
                Sumandos_Biblioteca.objects.filter(polya_biblioteca=polya).delete()
                # Crear nuevos sumandos
                for sumando_valor in sumandos_list:
                    if sumando_valor:  # Solo si no está vacío
                        Sumandos_Biblioteca.objects.create(
                            polya_biblioteca=polya,
                            sumando=str(sumando_valor)
                        )
            except json.JSONDecodeError:
                pass

        return JsonResponse({
            'success': True,
            'message': 'Método de Pólya guardado exitosamente',
            'polya_id': polya.id
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def cargar_polya_biblioteca(request):
    """Carga el trabajo de Pólya para un contenido de biblioteca"""
    try:
        biblioteca_id = request.GET.get('biblioteca_id')
        if not biblioteca_id:
            return JsonResponse({'success': False, 'message': 'biblioteca_id requerido'}, status=400)

        try:
            biblioteca = Biblioteca.objects.get(biblioteca_id=biblioteca_id)
        except Biblioteca.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Contenido de biblioteca no encontrado'}, status=404)

        # Buscar el registro de Pólya
        try:
            polya = PolyaBiblioteca.objects.get(
                usuario=request.user,
                biblioteca=biblioteca
            )
            
            # Obtener sumandos
            sumandos = Sumandos_Biblioteca.objects.filter(polya_biblioteca=polya).values_list('sumando', flat=True)
            
            data = {
                'success': True,
                'polya': {
                    'id': polya.id,
                    'identificacion_operacion': polya.identificacion_operacion or '',
                    'por_que_esa_operacion': polya.por_que_esa_operacion or '',
                    'que_se_pide': polya.que_se_pide or '',
                    'datos_conocidos': polya.datos_conocidos or '',
                    'incognitas': polya.incognitas or '',
                    'representacion': polya.representacion or '',
                    'estrategia_principal': polya.estrategia_principal or '',
                    'desarrollo': polya.desarrollo or '',
                    'resultados_intermedios': polya.resultados_intermedios or '',
                    'revision_verificacion': polya.revision_verificacion or '',
                    'comprobacion_otro_metodo': polya.comprobacion_otro_metodo or '',
                    'conclusion_final': polya.conclusion_final or '',
                    'confianza': polya.confianza,
                    'sumandos': list(sumandos),
                    'created_at': polya.created_at.isoformat() if polya.created_at else None,
                    'updated_at': polya.updated_at.isoformat() if polya.updated_at else None
                }
            }
            return JsonResponse(data)
            
        except PolyaBiblioteca.DoesNotExist:
            # No existe registro previo
            return JsonResponse({
                'success': True,
                'polya': None,
                'message': 'No hay datos guardados previamente'
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
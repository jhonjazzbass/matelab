from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import F
from .models import Mision, Habilidad, IntentoMision, PolyaTrabajoUM, Sumandos
import logging
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from apps.biblioteca.models import Biblioteca_Usuario, Biblioteca_Contenido

# Configurar el logger
logger = logging.getLogger(__name__)
 
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def guardar_intento_mision(request):
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        mision_id = data.get('mision_id')
        solucion = data.get('solucion', '')
        estado = data.get('estado', 'en_progreso')
        
        # --- NUEVO: Extraer variables de la lógica adaptativa ---
        tiempo_total_segundos = data.get('tiempo_total_segundos', 0)
        tiempo_fase_1_segundos = data.get('tiempo_fase_1_segundos', 0)
        tiempo_fase_2_segundos = data.get('tiempo_fase_2_segundos', 0)
        tiempo_fase_3_segundos = data.get('tiempo_fase_3_segundos', 0)
        tiempo_fase_4_segundos = data.get('tiempo_fase_4_segundos', 0)
        intentos_fallidos = data.get('intentos_fallidos', 0)

        # Validate that the mission exists
        mision = get_object_or_404(Mision, pk=mision_id)
        
        # --- NUEVO: Validación estricta de la respuesta (Auto-grading) ---
        solucion_limpia = str(solucion).strip().lower().replace(" ", "")
        correcta_limpia = str(mision.solucion_correcta).strip().lower().replace(" ", "")
        
        if solucion_limpia != correcta_limpia:
            intentos_fallidos += 1
            # Guardamos el intento como rechazado pero NO corremos el motor adaptativo todavía
            IntentoMision.objects.update_or_create(
                usuario=request.user,
                mision=mision,
                defaults={
                    'estado': 'rechazado',
                    'solucion_propuesta': solucion,
                    'fecha_intento': timezone.now(),
                    'tiempo_total_segundos': tiempo_total_segundos,
                    'intentos_fallidos': intentos_fallidos
                }
            )
            return JsonResponse({
                'status': 'wrong_answer',
                'message': '❌ Respuesta incorrecta. ¡Revisa tus cálculos e inténtalo de nuevo!',
                'intentos_fallidos': intentos_fallidos
            })

        # Si llegó aquí, la respuesta es CORRECTA
        estado = 'completado'
        
        # Create or update the mission attempt
        intento, created = IntentoMision.objects.update_or_create(
            usuario=request.user,
            mision=mision,
            defaults={
                'estado': estado,
                'solucion_propuesta': solucion,
                'fecha_intento': timezone.now(),
                # Guardar sensores en el intento
                'tiempo_total_segundos': tiempo_total_segundos,
                'intentos_fallidos': intentos_fallidos
            }
        )
        
        # Guardar sensores de las fases en PolyaTrabajoUM
        polya, _created_polya = PolyaTrabajoUM.objects.get_or_create(
            usuario=request.user,
            mision=mision
        )
        polya.tiempo_fase_1_segundos = tiempo_fase_1_segundos
        polya.tiempo_fase_2_segundos = tiempo_fase_2_segundos
        polya.tiempo_fase_3_segundos = tiempo_fase_3_segundos
        polya.tiempo_fase_4_segundos = tiempo_fase_4_segundos
        polya.save()
        
        # --- NUEVO: Lógica Adaptativa ---
        from apps.misiones.services import MotorAdaptabilidad
        from apps.misiones.models import ProgresoHabilidad
        siguiente_dificultad = MotorAdaptabilidad.determinar_siguiente_dificultad(intento)
        
        # Persistir el nivel adaptativo para la próxima vez
        progreso, _ = ProgresoHabilidad.objects.get_or_create(
            usuario=request.user,
            habilidad=mision.habilidad
        )
        progreso.nivel_actual = siguiente_dificultad
        progreso.save()
        
        # Imprimir en consola para validación
        print("\n=== [LOGICA ADAPTATIVA: MATELAB] ===")
        print(f"Estudiante: {request.user.nombre_usuario}")
        print(f"Misión: {mision.titulo} (Nivel {mision.nivel_dificultad})")
        print(f"Tiempo Total: {tiempo_total_segundos}s | Fallos: {intentos_fallidos}")
        print(f"-> Siguiente Dificultad Recomendada: Nivel {siguiente_dificultad}")
        print("======================================\n")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Intento de misión guardado correctamente',
            'intento_id': intento.intento_id,
            'estado': estado,
            'fecha': intento.fecha_intento.strftime('%Y-%m-%d %H:%M:%S'),
            'siguiente_dificultad': siguiente_dificultad
        })
        
    except json.JSONDecodeError:
        logger.error("Error al decodificar JSON en guardar_intento_mision")
        return JsonResponse(
            {'status': 'error', 'message': 'Formato JSON inválido'},
            status=400
        )
    except Mision.DoesNotExist:
        logger.error(f"Misión no encontrada: {mision_id}")
        return JsonResponse(
            {'status': 'error', 'message': 'La misión especificada no existe'},
            status=404
        )
    except Exception as e:
        logger.error(f"Error al guardar el intento de misión: {str(e)}")
        return JsonResponse(
            {'status': 'error', 'message': 'Error interno del servidor'},
            status=500
        )

@login_required
def lista_misiones(request):
    logger.info("Iniciando vista lista_misiones")
    
    # Obtener todas las misiones activas
    logger.info("Obteniendo misiones activas")
    try:
        misiones_qs = Mision.objects.filter(activa=True).select_related('habilidad')
        logger.info(f"Se encontraron {misiones_qs.count()} misiones activas")

        # Reordenar misiones por tipo_operacion, máximo 10 por tipo en orden definido
        tipos_en_orden = ['suma', 'resta', 'multiplicacion', 'division']
        misiones_ordenadas = []
        for tipo in tipos_en_orden:
            for m in misiones_qs.filter(tipo_operacion=tipo).order_by('fecha_creacion')[:10]:
                misiones_ordenadas.append(m)

        # Agregar cualquier misión de otros tipos (o sobrantes) al final, sin duplicar
        ids_ya_incluidos = {m.mision_id for m in misiones_ordenadas}
        for m in misiones_qs.exclude(mision_id__in=ids_ya_incluidos).order_by('fecha_creacion'):
            misiones_ordenadas.append(m)

        # Determinar tipos de misión desbloqueados por el usuario (por defecto bloqueadas)
        unlocked_types = set()
        try:
            rol_usuario = getattr(request.user.rol, 'tipo', '')
        except Exception:
            rol_usuario = ''

        if rol_usuario == 'Estudiante':
            try:
                biblioteca_ids = list(
                    Biblioteca_Usuario.objects.filter(usuario=request.user, estado=True)
                    .values_list('biblioteca_id', flat=True)
                )
                if biblioteca_ids:
                    tipos_contenido = Biblioteca_Contenido.objects.filter(
                        biblioteca_id__in=biblioteca_ids
                    ).values_list('tipo', flat=True)
                    for t in tipos_contenido:
                        s = (t or '').strip().lower()
                        # normalizar acentos comunes
                        s = (s
                             .replace('á', 'a')
                             .replace('é', 'e')
                             .replace('í', 'i')
                             .replace('ó', 'o')
                             .replace('ú', 'u'))
                        # mapear posibles variantes a los choices de Mision.tipo_operacion
                        if s in {'suma', 'resta', 'multiplicacion', 'division'}:
                            unlocked_types.add(s)
                        elif 'suma' in s:
                            unlocked_types.add('suma')
                        elif 'resta' in s:
                            unlocked_types.add('resta')
                        elif 'multiplic' in s:
                            unlocked_types.add('multiplicacion')
                        elif 'divis' in s:
                            unlocked_types.add('division')
            except Exception as e:
                logger.warning(f"No se pudieron obtener tipos desbloqueados: {e}")

        # Obtener el nivel actual del estudiante por habilidad (Motor Adaptativo)
        progreso_niveles = {}
        if rol_usuario == 'Estudiante':
            from apps.misiones.models import ProgresoHabilidad
            progresos = ProgresoHabilidad.objects.filter(usuario=request.user)
            for p in progresos:
                progreso_niveles[p.habilidad_id] = p.nivel_actual

        # Crear una lista para almacenar las misiones con su estado
        misiones_con_estado = []

        for mision in misiones_ordenadas:
            logger.info(f"Procesando misión ID: {mision.mision_id} - {mision.titulo}")
            # Obtener el último intento del usuario para esta misión
            try:
                intento = IntentoMision.objects.filter(
                    usuario=request.user,
                    mision=mision
                ).latest('fecha_intento')
                estado = intento.estado
                logger.info(f"  - Último intento: {estado}")
            except IntentoMision.DoesNotExist:
                estado = 'pendiente'
                logger.info("  - Sin intentos previos")
                
            # Agregar el estado como atributo a la misión
            mision.estado_actual = estado

            # Calcular si la misión está bloqueada para el usuario actual
            if rol_usuario == 'Profesor':
                mision.bloqueada = False
                misiones_con_estado.append(mision)
            else:
                mision.bloqueada = ((mision.tipo_operacion or '').strip().lower() not in unlocked_types)
                
                # FILTRO DEL MOTOR ADAPTATIVO:
                # Solo mostrar la misión si ya la completó, o si es del nivel que el algoritmo le asignó.
                nivel_permitido = progreso_niveles.get(mision.habilidad_id, '1')
                if estado == 'completado' or str(mision.nivel_dificultad) == str(nivel_permitido):
                    misiones_con_estado.append(mision)
        
        # Obtener todas las habilidades para los filtros
        try:
            habilidades = Habilidad.objects.all()
            logger.info(f"Se encontraron {habilidades.count()} habilidades")
        except Exception as e:
            logger.error(f"Error al obtener habilidades: {str(e)}")
            habilidades = []
         
        user_role = request.user.rol.tipo
        context = {
            'misiones': misiones_con_estado,
            'habilidades': habilidades, 
        }
        
        # Agregar datos de depuración al contexto
        context['debug'] = {
            'misiones_count': len(misiones_con_estado),
            'usuario': request.user.nombre_usuario,
        }
        
        logger.info(f"Contexto preparado con {len(misiones_con_estado)} misiones")
        
    except Exception as e:
        logger.error(f"Error en la vista lista_misiones: {str(e)}", exc_info=True)
        context = {
            'misiones': [],
            'habilidades': [],
            'error': str(e), 
        }
    
    # Agregar request al contexto para acceder al usuario en la plantilla
    context['request'] = request
    
    
    return render(request, 'dashboards/misiones.html', context)



@require_http_methods(["GET"])
def obtener_intentos_mision(request, mision_id):
    intentos = IntentoMision.objects.filter(
        mision_id=mision_id
    ).select_related('usuario').values(
            'intento_id',
            'estado',
            'fecha_intento',
            'solucion_propuesta',
        'usuario__usuario_id',  # Use double underscore for related field
        'usuario__nombre_usuario'    
    )
    return JsonResponse(list(intentos), safe=False)

@csrf_exempt
@require_http_methods(["PATCH"])
def actualizar_estado_intento(request, intento_id):
    try:
        data = json.loads(request.body)
        intento = IntentoMision.objects.get(intento_id=intento_id)
        intento.estado = data.get('estado', 'pendiente')
        intento.save()
        return JsonResponse({'status': 'success'})
    except IntentoMision.DoesNotExist:
        return JsonResponse({'error': 'Intento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"]) 
def obtener_polya_um(request, mision_id):
    try:
        mision = get_object_or_404(Mision, pk=mision_id)
        try:
            polya = PolyaTrabajoUM.objects.get(usuario=request.user, mision=mision)
            data = {
                'que_se_pide': polya.que_se_pide or '',
                'datos_conocidos': polya.datos_conocidos or '',
                'incognitas': polya.incognitas or '',
                'representacion': polya.representacion or '',
                'estrategia_principal': polya.estrategia_principal or '',
                'tactica_similar': bool(polya.tactica_similar),
                'tactica_descomponer': bool(polya.tactica_descomponer),
                'tactica_ecuaciones': bool(polya.tactica_ecuaciones),
                'tactica_formula': bool(polya.tactica_formula),
                'desarrollo': polya.desarrollo or '',
                'resultados_intermedios': polya.resultados_intermedios or '',
                'revision_verificacion': polya.revision_verificacion or '',
                'comprobacion_otro_metodo': polya.comprobacion_otro_metodo or '',
                'conclusion_final': polya.conclusion_final or '',
                'confianza': polya.confianza if polya.confianza is not None else None,
                'identificacion_operacion': getattr(polya, 'identificacion_operacion', '') or '',
                'por_que_esa_operacion': getattr(polya, 'por_que_esa_operacion', '') or '',
                'sumandos': list(Sumandos.objects.filter(polya_um_id=polya).values_list('sumando', flat=True)),
                'solucion_correcta': mision.solucion_correcta or '',
            }
            return JsonResponse({'status': 'success', 'data': data})
        except PolyaTrabajoUM.DoesNotExist:
            data = {
                'que_se_pide': '',
                'datos_conocidos': '',
                'incognitas': '',
                'representacion': '',
                'estrategia_principal': '',
                'tactica_similar': False,
                'tactica_descomponer': False,
                'tactica_ecuaciones': False,
                'tactica_formula': False,
                'desarrollo': '',
                'resultados_intermedios': '',
                'revision_verificacion': '',
                'comprobacion_otro_metodo': '',
                'conclusion_final': '',
                'confianza': None,
                'identificacion_operacion': '',
                'por_que_esa_operacion': '',
                'sumandos': [],
                'solucion_correcta': mision.solucion_correcta or '',
            }
            return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        logger.error(f"Error en obtener_polya_um: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Error interno del servidor'}, status=500)


@login_required
@require_http_methods(["GET"]) 
def obtener_alternativas_mision(request, mision_id):
    try:
        mision = get_object_or_404(Mision, pk=mision_id)
        alternativas = []
        for campo in ['alternativa1', 'alternativa2', 'alternativa3']:
            val = getattr(mision, campo, None)
            if isinstance(val, str) and val.strip():
                alternativas.append(val.strip())
        solucion_correcta = ''
        valc = getattr(mision, 'solucion_correcta', None)
        if isinstance(valc, str) and valc.strip():
            solucion_correcta = valc.strip()
        return JsonResponse({'status': 'success', 'alternativas': alternativas, 'solucion_correcta': solucion_correcta})
    except Exception as e:
        logger.error(f"Error en obtener_alternativas_mision: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Error interno del servidor'}, status=500)


@login_required
@require_http_methods(["POST"]) 
@csrf_exempt
def guardar_polya_um(request, mision_id):
    try:
        payload = json.loads(request.body)
        mision = get_object_or_404(Mision, pk=mision_id)

        # Validación Secuencial de Pólya (Backend)
        ident_op = payload.get('identificacion_operacion')
        
        # Datos de las fases posteriores
        fase2_presente = bool(payload.get('estrategia_principal')) or bool(payload.get('tactica_similar')) or bool(payload.get('tactica_descomponer')) or bool(payload.get('tactica_ecuaciones')) or bool(payload.get('tactica_formula'))
        fase3_presente = bool(payload.get('desarrollo')) or bool(payload.get('resultados_intermedios'))
        fase4_presente = bool(payload.get('revision_verificacion')) or bool(payload.get('comprobacion_otro_metodo')) or bool(payload.get('conclusion_final'))
        
        # Si la Fase 1 (identificacion_operacion) está vacía, no se permite información de fases posteriores
        if not ident_op and (fase2_presente or fase3_presente or fase4_presente):
            return JsonResponse({
                'status': 'error', 
                'message': 'Rúbrica Pólya: Debes completar la Fase 1 (Seleccionar la Operación) antes de poder enviar datos de fases más avanzadas.'
            }, status=400)

        polya, _created = PolyaTrabajoUM.objects.get_or_create(
            usuario=request.user,
            mision=mision
        )

        polya.que_se_pide = payload.get('que_se_pide')
        polya.datos_conocidos = payload.get('datos_conocidos')
        polya.incognitas = payload.get('incognitas')
        polya.representacion = payload.get('representacion')
        polya.estrategia_principal = payload.get('estrategia_principal')
        polya.tactica_similar = bool(payload.get('tactica_similar'))
        polya.tactica_descomponer = bool(payload.get('tactica_descomponer'))
        polya.tactica_ecuaciones = bool(payload.get('tactica_ecuaciones'))
        polya.tactica_formula = bool(payload.get('tactica_formula'))
        polya.desarrollo = payload.get('desarrollo')
        polya.resultados_intermedios = payload.get('resultados_intermedios')
        polya.revision_verificacion = payload.get('revision_verificacion')
        polya.comprobacion_otro_metodo = payload.get('comprobacion_otro_metodo')
        polya.conclusion_final = payload.get('conclusion_final')
        polya.identificacion_operacion = payload.get('identificacion_operacion')
        polya.por_que_esa_operacion = payload.get('por_que_esa_operacion')
        confianza_val = payload.get('confianza')
        try:
            polya.confianza = int(confianza_val) if confianza_val is not None else None
        except (TypeError, ValueError):
            polya.confianza = None
        polya.save()

        # Actualizar sumandos asociados
        try:
            sumandos_payload = payload.get('sumandos', []) or []
            if not isinstance(sumandos_payload, list):
                sumandos_payload = []
            Sumandos.objects.filter(polya_um_id=polya).delete()
            for s in sumandos_payload:
                if isinstance(s, str):
                    texto = s.strip()
                    if texto:
                        Sumandos.objects.create(polya_um_id=polya, sumando=texto)
        except Exception as e:
            logger.error(f"Error al actualizar sumandos en guardar_polya_um: {str(e)}", exc_info=True)

        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Formato JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Error en guardar_polya_um: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Error interno del servidor'}, status=500)


@login_required
@require_http_methods(["GET"]) 
def obtener_polya_um_estudiante(request, mision_id, usuario_id):
    try:
        try:
            es_profesor = getattr(request.user.rol, 'tipo', '') == 'Profesor'
        except Exception:
            es_profesor = False
        if not es_profesor:
            return JsonResponse({'status': 'forbidden', 'message': 'Solo profesores'}, status=403)

        mision = get_object_or_404(Mision, pk=mision_id)

        polya = PolyaTrabajoUM.objects.filter(usuario_id=usuario_id, mision=mision).first()
        data_polya = None
        if polya:
            data_polya = {
                'que_se_pide': polya.que_se_pide or '',
                'datos_conocidos': polya.datos_conocidos or '',
                'incognitas': polya.incognitas or '',
                'representacion': polya.representacion or '',
                'estrategia_principal': polya.estrategia_principal or '',
                'tactica_similar': bool(polya.tactica_similar),
                'tactica_descomponer': bool(polya.tactica_descomponer),
                'tactica_ecuaciones': bool(polya.tactica_ecuaciones),
                'tactica_formula': bool(polya.tactica_formula),
                'desarrollo': polya.desarrollo or '',
                'resultados_intermedios': polya.resultados_intermedios or '',
                'revision_verificacion': polya.revision_verificacion or '',
                'comprobacion_otro_metodo': polya.comprobacion_otro_metodo or '',
                'conclusion_final': polya.conclusion_final or '',
                'confianza': polya.confianza if polya.confianza is not None else None,
            }

        intento = IntentoMision.objects.filter(usuario_id=usuario_id, mision_id=mision_id).order_by('-fecha_intento').first()
        data_intento = None
        if intento:
            data_intento = {
                'solucion_propuesta': intento.solucion_propuesta or '',
                'estado': intento.estado,
                'fecha_intento': intento.fecha_intento.isoformat() if intento.fecha_intento else None,
                'intento_id': intento.intento_id,
            }

        return JsonResponse({'status': 'success', 'polya': data_polya, 'intento': data_intento})
    except Exception as e:
        logger.error(f"Error en obtener_polya_um_estudiante: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Error interno del servidor'}, status=500)
# apps/misiones/services.py
from .models import IntentoMision, Mision

class MotorAdaptabilidad:
    """
    Capa de servicio para calcular el rendimiento del estudiante 
    y determinar la dificultad de su próxima misión.
    """
    
    # Tiempos ideales estimados (en segundos) según la dificultad
    TIEMPO_IDEAL = {
        '1': 120, # Fácil: 2 minutos
        '2': 240, # Medio: 4 minutos
        '3': 420  # Difícil: 7 minutos
    }

    @staticmethod
    def calcular_rendimiento(intento: IntentoMision) -> float:
        """
        Calcula una puntuación de 0 a 100 basada en el tiempo y los intentos fallidos.
        """
        nivel = intento.mision.nivel_dificultad
        tiempo_ideal = MotorAdaptabilidad.TIEMPO_IDEAL.get(nivel, 240)
        
        # Penalización por tiempo excedido
        tiempo_real = intento.tiempo_total_segundos
        ratio_tiempo = tiempo_ideal / tiempo_real if tiempo_real > 0 else 1
        
        # Si lo hizo más rápido del ideal, no le damos más de 100% en esta métrica
        score_tiempo = min(ratio_tiempo * 100, 100) 
        
        # Penalización por intentos fallidos (restamos 15 puntos por cada error)
        penalizacion_errores = intento.intentos_fallidos * 15
        
        score_final = score_tiempo - penalizacion_errores
        
        # Aseguramos que el score no sea negativo
        return max(score_final, 0)

    @staticmethod
    def determinar_siguiente_dificultad(intento: IntentoMision) -> str:
        """
        Devuelve el nivel ('1', '2' o '3') para la siguiente misión.
        """
        score = MotorAdaptabilidad.calcular_rendimiento(intento)
        nivel_actual = int(intento.mision.nivel_dificultad)

        if score >= 85:
            # Excelente rendimiento, subir dificultad (máximo 3)
            nuevo_nivel = min(nivel_actual + 1, 3)
        elif score < 50:
            # Bajo rendimiento, bajar dificultad (mínimo 1)
            nuevo_nivel = max(nivel_actual - 1, 1)
        else:
            # Rendimiento promedio, mantener dificultad
            nuevo_nivel = nivel_actual

        return str(nuevo_nivel)
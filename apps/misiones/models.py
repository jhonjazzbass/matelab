from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model 
from apps.authentication.models import Usuarios

# Use the custom user model
User = get_user_model()
TIPO_OPERACION_CHOICES = [
    ('suma', 'Suma'),
    ('resta', 'Resta'),
    ('multiplicacion', 'Multiplicación'),
    ('division', 'División'),
]

# --- NUEVO: Opciones para la lógica adaptativa ---
NIVEL_DIFICULTAD_CHOICES = [
    ('1', 'Fácil'),
    ('2', 'Medio'),
    ('3', 'Difícil'),
]

class Habilidad(models.Model):
    habilidad_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    icono = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = 'Habilidad'
        verbose_name_plural = 'Habilidades'

    def __str__(self):
        return self.nombre

class Mision(models.Model):
    mision_id = models.AutoField(primary_key=True)
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE, db_column='habilidad_id')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    instrucciones_polya = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    tipo_operacion = models.CharField(max_length=20, choices=TIPO_OPERACION_CHOICES)
    
    # --- NUEVO: Campo para saber el peso base del ejercicio ---
    nivel_dificultad = models.CharField(max_length=10, choices=NIVEL_DIFICULTAD_CHOICES, default='1')

    alternativa1 = models.CharField('Alternativa 1', max_length=50, db_column='alternativa1')
    alternativa2 = models.CharField('Alternativa 2', max_length=50, db_column='alternativa2')
    alternativa3 = models.CharField('Alternativa 3', max_length=50, db_column='alternativa3')
    solucion_correcta = models.CharField('Solución Correcta', max_length=50, db_column='solucion_correcta')

    class Meta:
        db_table = 'Mision'
        verbose_name_plural = 'Misiones'
        ordering = ['fecha_creacion']

    def __str__(self):
        return self.titulo

class IntentoMision(models.Model):
    ESTADO_CHOICES = [
        ('completado', 'Completado'),
        ('rechazado', 'Incorrecto'),
        ('en_progreso', 'En Progreso'),
    ]
    
    intento_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id')
    mision = models.ForeignKey(Mision, on_delete=models.CASCADE, db_column='mision_id')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    solucion_propuesta = models.TextField(null=True, blank=True)
    fecha_intento = models.DateTimeField(auto_now_add=True)

    # --- NUEVO: Variables de la ecuación adaptativa ---
    intentos_fallidos = models.IntegerField(default=0, help_text="Cantidad de veces que el alumno envió una respuesta incorrecta antes de acertar.")
    tiempo_total_segundos = models.IntegerField(default=0, help_text="Tiempo total invertido en la misión entera.")

    class Meta:
        db_table = 'Intento_Mision'
        verbose_name_plural = 'Intentos de Misiones'
        ordering = ['-fecha_intento']

    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.mision.titulo} ({self.estado})"

class ProgresoHabilidad(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id')
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE, db_column='habilidad_id')
    porcentaje_avance = models.IntegerField(default=0)
    nivel_actual = models.CharField(max_length=10, choices=NIVEL_DIFICULTAD_CHOICES, default='1')
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Progreso_Habilidad'
        verbose_name_plural = 'Progreso de Habilidades'
        unique_together = (('usuario', 'habilidad'),)

    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.habilidad.nombre}: {self.porcentaje_avance}%"

class PolyaTrabajoUM(models.Model):
    id = models.AutoField(primary_key=True, db_column='polya_um_id')
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id')
    mision = models.ForeignKey(Mision, on_delete=models.CASCADE, db_column='mision_id')

    # Paso 1: Comprender el problema
    que_se_pide = models.TextField(null=True, blank=True)
    datos_conocidos = models.TextField(null=True, blank=True)
    incognitas = models.TextField(null=True, blank=True)
    representacion = models.CharField(max_length=500, null=True, blank=True)
    tiempo_fase_1_segundos = models.IntegerField(default=0) # NUEVO

    # Paso 2: Planificar la estrategia
    estrategia_principal = models.TextField(null=True, blank=True)
    tactica_similar = models.BooleanField(default=False)
    tactica_descomponer = models.BooleanField(default=False)
    tactica_ecuaciones = models.BooleanField(default=False)
    tactica_formula = models.BooleanField(default=False)
    tiempo_fase_2_segundos = models.IntegerField(default=0) # NUEVO

    # Paso 3: Ejecutar el plan
    desarrollo = models.TextField(null=True, blank=True)
    resultados_intermedios = models.TextField(null=True, blank=True)
    tiempo_fase_3_segundos = models.IntegerField(default=0) # NUEVO

    # Paso 4: Revisar y verificar
    revision_verificacion = models.TextField(null=True, blank=True)
    comprobacion_otro_metodo = models.TextField(null=True, blank=True)
    conclusion_final = models.TextField(null=True, blank=True)
    confianza = models.IntegerField(null=True, blank=True)
    tiempo_fase_4_segundos = models.IntegerField(default=0) # NUEVO

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    identificacion_operacion = models.TextField(null=True, blank=True)
    por_que_esa_operacion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'Polya_Trabajo_UM'
        verbose_name_plural = 'Trabajos Polya (Usuario-Misión)'
        unique_together = (('usuario', 'mision'),)

    def __str__(self):
        return f"Polya UM - {self.usuario.nombre_usuario} / {self.mision.titulo}"

class Sumandos(models.Model):
    sumando_id = models.AutoField(primary_key=True)
    polya_um_id =  models.ForeignKey(PolyaTrabajoUM, on_delete=models.CASCADE, db_column='polya_um_id')
    sumando = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'Sumandos'
        verbose_name_plural = 'Sumandos'

    def __str__(self):
        return f"Sumando {self.sumando_id}"

class Trofeo(models.Model):
    trofeo_id = models.AutoField(primary_key=True)
    nombre_trofeo = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    icono_trofeo = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = 'Trofeo'
        verbose_name_plural = 'Trofeos'

    def __str__(self):
        return self.nombre_trofeo

class TrofeoEstudiante(models.Model):
    id = models.AutoField(primary_key=True)
    trofeo = models.ForeignKey(Trofeo, on_delete=models.CASCADE, db_column='trofeo_id')
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id')

    class Meta:
        db_table = 'Trofeo_Estudiante'
        verbose_name_plural = 'Trofeos de Estudiantes'
        unique_together = (('trofeo', 'usuario'),)

    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.trofeo.nombre_trofeo}"
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

    class Meta:
        db_table = 'Intento_Mision'
        verbose_name_plural = 'Intentos de Misiones'
        ordering = ['-fecha_intento']

    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.mision.titulo} ({self.estado})"

class ProgresoHabilidad(models.Model):
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE, db_column='usuario_id', primary_key=True)
    habilidad = models.OneToOneField(Habilidad, on_delete=models.CASCADE, db_column='habilidad_id')
    porcentaje_avance = models.IntegerField(default=0)
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

    # Paso 2: Planificar la estrategia
    estrategia_principal = models.TextField(null=True, blank=True)
    tactica_similar = models.BooleanField(default=False)
    tactica_descomponer = models.BooleanField(default=False)
    tactica_ecuaciones = models.BooleanField(default=False)
    tactica_formula = models.BooleanField(default=False)

    # Paso 3: Ejecutar el plan
    desarrollo = models.TextField(null=True, blank=True)
    resultados_intermedios = models.TextField(null=True, blank=True)

    revision_verificacion = models.TextField(null=True, blank=True)
    comprobacion_otro_metodo = models.TextField(null=True, blank=True)
    conclusion_final = models.TextField(null=True, blank=True)
    confianza = models.IntegerField(null=True, blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Polya_Trabajo_UM'
        verbose_name_plural = 'Trabajos Polya (Usuario-Misión)'
        unique_together = (('usuario', 'mision'),)

    def __str__(self):
        return f"Polya UM - {self.usuario.nombre_usuario} / {self.mision.titulo}"

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
    trofeo = models.OneToOneField(Trofeo, on_delete=models.CASCADE, db_column='trofeo_id', primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id')

    class Meta:
        db_table = 'Trofeo_Estudiante'
        verbose_name_plural = 'Trofeos de Estudiantes'
        unique_together = (('trofeo', 'usuario'),)

    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.trofeo.nombre_trofeo}"
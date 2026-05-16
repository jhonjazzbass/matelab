from django.db import models
from django.contrib.auth import get_user_model
from ..authentication.models import Usuarios

class Biblioteca(models.Model):
    TIPO_CHOICES = [
        ('Practica', 'Practica'),
        ('Juego', 'Juego'),
        ('Contenido', 'Contenido'),
    ]
    
    biblioteca_id = models.AutoField(primary_key=True)
    titulo = models.CharField('Título', max_length=255, db_column='Titulo')
    descripcion = models.TextField('Descripción', db_column='Descripcion')
    solucion = models.TextField('Solución', db_column='Solucion')
    tipo = models.CharField('Tipo', max_length=50, choices=TIPO_CHOICES, db_column='tipo')
    activo = models.BooleanField('Activo', default=True, db_column='activo')
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id')

    class Meta:
        db_table = 'Biblioteca'   
        managed = True  
        verbose_name = 'Contenido de Biblioteca'
        verbose_name_plural = 'Contenidos de Biblioteca' 

    def __str__(self):
        # CORREGIDO: titulo en minúscula
        return self.titulo


class Biblioteca_Usuario(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id', primary_key=True)
    biblioteca = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, db_column='biblioteca_id')
    estado = models.BooleanField('Estado', default=True, db_column='estado')
   
    class Meta:
        db_table = 'Biblioteca_Usuario'   
        managed = True  
        verbose_name = 'Estado de Biblioteca'
        verbose_name_plural = 'Estados de Biblioteca' 
        unique_together = (('usuario', 'biblioteca'),)

    def __str__(self):
        # CORREGIDO: Devolver una cadena de texto representativa en lugar del booleano
        return f"{self.usuario.nombre_usuario} - {self.biblioteca.titulo}"

class Biblioteca_Contenido(models.Model):
    biblioteca_contenido_id = models.AutoField(primary_key=True)
    biblioteca = models.OneToOneField(
        Biblioteca,
        on_delete=models.CASCADE,
        related_name='detalle_contenido'
    )
    teoria = models.TextField('Teoria', db_column='teoria')
    pasos_trucos = models.TextField('Pasos y Trucos', db_column='pasos_trucos')
    ejemplo = models.TextField('Ejemplo', db_column='ejemplo')
    tipo = models.TextField('Tipo', db_column='tipo')
    class Meta:
        db_table = 'Biblioteca_Contenido'   
        managed = True  
        verbose_name = 'Contenido de Biblioteca'
        verbose_name_plural = 'Contenidos de Biblioteca' 
 
    def __str__(self):
        # CORREGIDO: teoria en minúscula
        return self.teoria


class PolyaBiblioteca(models.Model):
    id = models.AutoField(primary_key=True, db_column='polya_biblioteca_id')
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, db_column='usuario_id')
    biblioteca = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, db_column='biblioteca_id')

    # Paso 1: Comprender el problema
    identificacion_operacion = models.CharField(max_length=100, null=True, blank=True)
    por_que_esa_operacion = models.CharField(max_length=300, null=True, blank=True)
    que_se_pide = models.TextField(null=True, blank=True)
    datos_conocidos = models.TextField(null=True, blank=True)
    incognitas = models.TextField(null=True, blank=True)
    representacion = models.CharField(max_length=500, null=True, blank=True)

    # Paso 2: Planificar la estrategia
    estrategia_principal = models.TextField(null=True, blank=True)

    # Paso 3: Ejecutar el plan
    desarrollo = models.TextField(null=True, blank=True)
    resultados_intermedios = models.TextField(null=True, blank=True)

    # Paso 4: Verificar y revisar
    revision_verificacion = models.TextField(null=True, blank=True)
    comprobacion_otro_metodo = models.TextField(null=True, blank=True)
    conclusion_final = models.TextField(null=True, blank=True)
    confianza = models.IntegerField(null=True, blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Polya_Biblioteca'
        managed = True
        verbose_name = 'Trabajo Polya (Biblioteca)'
        verbose_name_plural = 'Trabajos Polya (Biblioteca)'
        unique_together = (('usuario', 'biblioteca'),)

    def __str__(self):
        return f"Polya Biblioteca - {self.usuario.nombre_usuario} / {self.biblioteca.titulo}"


class Sumandos_Biblioteca(models.Model):
    sumando_id = models.AutoField(primary_key=True)
    polya_biblioteca = models.ForeignKey(PolyaBiblioteca, on_delete=models.CASCADE, db_column='polya_biblioteca_id')
    sumando = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'Sumandos_Biblioteca'
        managed = True
        verbose_name = 'Sumando (Biblioteca)'
        verbose_name_plural = 'Sumandos (Biblioteca)'

    def __str__(self):
        return f"Sumando {self.sumando_id} - Biblioteca"
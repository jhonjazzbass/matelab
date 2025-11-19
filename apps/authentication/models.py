# apps/authentication/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password as django_check_password

class CustomUserManager(BaseUserManager):
    def create_user(self, nombre_usuario, password=None, **extra_fields):
        if not nombre_usuario:
            raise ValueError('El nombre de usuario es obligatorio')
        user = self.model(nombre_usuario=nombre_usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(nombre_usuario, password, **extra_fields)

class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=100)

    class Meta:
        db_table = 'Rol'
        managed = False  # La tabla ya existe en la base de datos

    def __str__(self):
        return self.tipo

class Usuarios(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=150, unique=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='rol_id')
    contraseña_hash = models.CharField(max_length=128)  
    estado = models.BooleanField(default=True)

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'Usuarios'
        managed = False  # Importante: No gestiona la creación/eliminación

    def __str__(self):
        return self.nombre_usuario

    def set_password(self, raw_password):
        self.contraseña_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Check the password against the stored hash.
        """
        return django_check_password(raw_password, self.contraseña_hash)


    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
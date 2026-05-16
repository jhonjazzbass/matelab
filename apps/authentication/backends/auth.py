# apps/authentication/backends/auth.py
from django.contrib.auth.backends import BaseBackend
from apps.authentication.models import Usuarios
from django.contrib.auth.hashers import check_password
import logging

logger = logging.getLogger(__name__)

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, nombre_usuario=None, contraseña_hash=None, **kwargs):
        if not nombre_usuario or not contraseña_hash:
            return None

        try:
            # Usamos el ORM de Django con select_related para optimizar la carga del Rol
            user = Usuarios.objects.select_related('rol').get(nombre_usuario=nombre_usuario)
            
            # Verificamos la contraseña (texto plano heredado o hash seguro)
            password_matches = (user.contraseña_hash == contraseña_hash) or check_password(contraseña_hash, user.contraseña_hash)
            
            if password_matches:
                # Guardar el rol en la sesión si el request está disponible
                if request and hasattr(user, 'rol') and user.rol:
                    request.session['user_role'] = user.rol.tipo.lower()
                
                # Establecer explícitamente el backend en el usuario
                user.backend = 'apps.authentication.backends.auth.CustomAuthBackend'
                return user

        except Usuarios.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Database error during authentication: {e}")
            return None

        return None

    def get_user(self, user_id):
        try:
            return Usuarios.objects.get(pk=user_id)
        except Usuarios.DoesNotExist:
            return None
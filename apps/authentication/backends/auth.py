# apps/authentication/backends/auth.py
from django.contrib.auth.backends import ModelBackend
from django.db import connections
from django.contrib.auth import get_user_model
from django.db.utils import DatabaseError
import logging

logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, nombre_usuario=None, contraseña_hash=None, **kwargs):
        if not nombre_usuario or not contraseña_hash:
            return None

        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("""
                    SELECT u.usuario_id, u.nombre_usuario, u.contraseña_hash, r.tipo as rol
                    FROM [dbo].[Usuarios] u
                    JOIN [dbo].[Rol] r ON u.rol_id = r.id
                    WHERE u.nombre_usuario = %s
                """, [nombre_usuario])
                user_data = cursor.fetchone()

            if user_data and self.check_password(contraseña_hash, user_data[2]):
                User = get_user_model()
                try:
                    user = User.objects.get(nombre_usuario=user_data[1])
                except User.DoesNotExist:
                    user = User(nombre_usuario=user_data[1])
                    user.set_unusable_password()
                    user.save()
                
                # Guardar el rol en la sesión
                request.session['user_role'] = user_data[3].lower()
                # Establecer el backend en el usuario antes de retornarlo
                user.backend = 'apps.authentication.backends.auth.CustomAuthBackend'
                return user

        except DatabaseError as e:
            logger.error(f"Database error during authentication: {e}")
            return None

        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def check_password(self, raw_password, hashed_password):
        # Implementa la lógica de verificación de contraseña
        # Por ahora, comparación directa (no seguro para producción)
        return raw_password == hashed_password
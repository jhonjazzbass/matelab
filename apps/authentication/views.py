from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from apps.authentication.models import Usuarios, Rol
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from django.contrib.auth.hashers import make_password
from ..dashboards.user_views import GestionUsuariosView
from django.contrib.auth.hashers import check_password
from apps.authentication.models import Usuarios

TEMPLATE_MAP = {
    "estudiante": "layout/partials/menu/vertical/student_menu.html",
    "profesor": "layout/partials/menu/vertical/professor_menu.html",
    "admin": "layout/partials/menu/vertical/admin_menu.html",
}


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to auth/urls.py file for more pages.
"""


class AuthView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Update the context
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context

def _build_login_context():
    context = TemplateLayout.init(None, {})
    context.update(
        {
            "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
        }
    )
    return context

 

def login_view(request):
    context = _build_login_context()

    if request.method == "POST":
        username = request.POST.get("nombre_usuario") 
        password = request.POST.get("password")
        try:
            user = Usuarios.objects.get(nombre_usuario=username)
        except Usuarios.DoesNotExist:
            user = None

        if user is not None:
            if user.contraseña_hash == password:
                user_auth = authenticate(request, nombre_usuario=username, contraseña_hash=password)
                auth_login(request, user_auth)
                return redirect("/")
            elif check_password(password, user.contraseña_hash):     
                user_auth = authenticate(request, nombre_usuario=username, contraseña_hash=user.contraseña_hash)
                auth_login(request, user_auth)
                return redirect("/")
 
        messages.error(request, "Usuario o contraseña inválidos")

    return render(request, "auth_login_basic.html", context)

 
def register_view(request, template):
    context = TemplateLayout.init(None, {})
    context.update(
        {
            "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
        }
    )
    if request.method == 'POST':
        username = request.POST.get('nombre_usuario')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role_id = request.POST.get('rol')
        
        # Basic validation
        if not all([username, password, confirm_password, role_id]):
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, template, context)
            
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, template, context)
            
        # Check if username already exists
        if Usuarios.objects.filter(nombre_usuario=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso')
            return render(request, template, context)
            
        # Create new user
        try:
            role = Rol.objects.get(id=role_id)
            user = Usuarios(
                nombre_usuario=username,
                rol=role,
                contraseña_hash=make_password(password),
                estado=True
            )
            user.save()
            
            # Redirect to login page with success message
            messages.success(request, '¡Registro exitoso! Por favor inicia sesión.')
            
            if template == 'gestion_usuarios.html': 
                return redirect('gestion_usuarios')
            else:
                return redirect('auth-login-basic')
            
        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {str(e)}')
            return render(request, template, context)
    
    return render(request, template, context)
 
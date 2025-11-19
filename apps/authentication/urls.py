from django.urls import path
from .views import AuthView, login_view, register_view


urlpatterns = [
    path(
        "auth/login/",
        AuthView.as_view(template_name="auth_login_basic.html"),
        name="auth-login-basic",
    ),
    path(
        "auth/register/",
        AuthView.as_view(template_name="auth_register_basic.html"),
        name="auth-register-basic",
    ),
    path(
        "auth/forgot_password/",
        AuthView.as_view(template_name="auth_forgot_password_basic.html"),
        name="auth-forgot-password-basic",
    ), 
    path('login/', login_view, name='auth-login-basic'),
    path('registro/', register_view, {'template': 'auth_register_basic.html'}, name='register'),
    path('crear-usuario/', register_view, {'template': 'gestion_usuarios.html'}, name='crear-usuario'),
]

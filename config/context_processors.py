from django.conf import settings
from typing import Dict


def my_setting(request):
    return {"MY_SETTING": settings}


def environment(request):
    return {"ENVIRONMENT": settings.ENVIRONMENT}


def _resolve_user_role(request) -> str:
    # Primero verificar si el rol está en la sesión (viene del backend de autenticación)
    if 'user_role' in request.session:
        return request.session['user_role']
        
    # Si no está en la sesión, usar la lógica existente
    user = getattr(request, "user", None)

    if not user or not user.is_authenticated:
        return "guest"
 

    if user.rol.tipo == "Administrador":
        return "administrador"

    if user.rol.tipo == "Profesor":
        return "profesor"

    if user.rol.tipo == "Estudiante":
        return "estudiante"

    return "default"


def sidebar_menu(request) -> Dict[str, str]:
    role = _resolve_user_role(request)

    template_map = {
        "estudiante": "layout/partials/menu/vertical/student_menu.html",
        "profesor": "layout/partials/menu/vertical/professor_menu.html",
        "administrador": "layout/partials/menu/vertical/admin_menu.html",
    }

    return {
        "sidebar_role": role,
        "sidebar_menu_template": template_map.get(role),
    }

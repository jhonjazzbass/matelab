# Matelab — Guía de ejecución

Este proyecto es una aplicación Django con autenticación personalizada, módulo de misiones, biblioteca y dashboards.

## Requisitos
- Windows (recomendado; el proyecto está configurado para SQL Server en Windows)
- Python 3.11 o 3.12
- SQL Server (p. ej. SQL Server Express) en localhost con una instancia `SQLEXPRESS`
- ODBC Driver 17 for SQL Server
- Git (opcional)

Notas:
- El motor por defecto está configurado para Microsoft SQL Server usando `pyodbc` (ver `config/settings.py`).

## Dependencias Python
Vienen definidas en `requirements.txt`.
Incluyen (extracto):
- Django 5.2.5
- whitenoise 6.9.0
- python-dotenv 1.1.1
- mssql-django / pyodbc (para SQL Server)

## Preparación del entorno
1) Crear y activar un entorno virtual
```
python -m venv .venv
.\.venv\Scripts\activate
```

2) Instalar dependencias
```
pip install --upgrade pip
pip install -r requirements.txt
```

3) Instalar el driver ODBC 17 (si no está instalado)
- Descarga e instala desde Microsoft: "ODBC Driver 17 for SQL Server"
- Asegúrate de que la arquitectura (x64/x86) coincide con tu Python

## Variables de entorno
El proyecto lee variables desde `.env` y `.env.prod` (ver `config/settings.py`).
Usa el archivo `.env` del repo como base. Si necesitas generarlo desde cero, un ejemplo mínimo es:
```
SECRET_KEY=tu_clave_secreta_segura
DJANGO_ENVIRONMENT=local
BASE_URL=http://127.0.0.1:8000
```

Notas:
- Si `SECRET_KEY` falta, la app generará una aleatoria en tiempo de ejecución.
- Para producción, usa `.env.prod` y configura `DEBUG=False` (requiere ajustes adicionales).

## Base de datos (SQL Server por defecto)
En `config/settings.py`:
```
DATABASES = {
  'default': {
    'ENGINE': 'mssql',
    'NAME': 'matematicasdb',
    'HOST': 'localhost\\SQLEXPRESS',
    'USER': '',        # Autenticación de Windows
    'PASSWORD': '',    # Autenticación de Windows
    'OPTIONS': {
      'driver': 'ODBC Driver 17 for SQL Server',
      'extra_params': 'Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes'
    },
  }
}
```
Opciones:
- Autenticación de Windows (por defecto): deja `USER` y `PASSWORD` vacíos.
- Usuario/Contraseña SQL: establece `USER` y `PASSWORD` y retira/ajusta `extra_params`.

Asegúrate de crear la BD `matematicasdb` en tu SQL Server antes de migrar.

## Migraciones y datos iniciales
Aplica migraciones:
```
python manage.py migrate
```

Crear cuenta de superusuario (si procede):
```
python manage.py createsuperuser
```
Modelo de usuario personalizado: `authentication.Usuarios`.

## Ejecutar en desarrollo
```
python manage.py runserver
```
La app estará disponible (por defecto) en `http://127.0.0.1:8000`.

Si deseas exponer en todas las interfaces:
```
python manage.py runserver 0.0.0.0:8000
```

## Estructura relevante
- `manage.py`: punto de entrada de comandos Django
- `config/settings.py`: configuración (DB, apps, plantillas, estáticos, etc.)
- `apps/`: aplicaciones del proyecto
  - `apps.authentication`: autenticación y modelo `Usuarios`
  - `apps.misiones`: módulo de misiones
  - `apps.biblioteca`: biblioteca
  - `apps.dashboards`: dashboards y vistas
- `templates/`: plantillas HTML
- `src/assets`: archivos estáticos durante desarrollo
- `staticfiles/`: destino de `collectstatic` para despliegue

## Comandos comunes
- Migraciones: `python manage.py makemigrations` / `python manage.py migrate`
- Crear superusuario: `python manage.py createsuperuser`
- Ejecutar tests: `python manage.py test`
- Recolectar estáticos (producción): `python manage.py collectstatic`

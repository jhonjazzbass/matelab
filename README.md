# MateLab

Bienvenido a MateLab. Una plataforma pedagógica innovadora construida con Django, diseñada para ofrecer una experiencia de aprendizaje interactiva a través de misiones, bibliotecas de recursos y dashboards analíticos.

## Innovación Principal: Motor Adaptativo y Método de Pólya

MateLab va más allá de un sistema tradicional de gestión del aprendizaje. Nuestro núcleo pedagógico y técnico incluye:

- Método de Pólya: Un flujo estructurado de resolución de problemas matemáticos en 4 fases, guiando a los estudiantes a través del razonamiento lógico de forma escalonada.
- Motor Adaptativo: La plataforma captura silenciosamente telemetría en segundo plano (como el tiempo invertido en cada fase y métricas de error). Este motor procesa los datos para ajustar dinámicamente la dificultad de las próximas misiones del estudiante, ofreciendo una ruta de aprendizaje verdaderamente personalizada y automatizada.

## Requisitos del Entorno

El proyecto está diseñado para ejecutarse de forma nativa en entornos Linux y utiliza PostgreSQL como su motor de base de datos principal.

- Sistema Operativo: Linux (Ubuntu/Debian recomendado)
- Python: 3.11 o 3.12
- Base de Datos: PostgreSQL 14 o superior
- Git (opcional, para control de versiones)

## Dependencias Python

Las dependencias principales vienen definidas en el archivo requirements.txt. Algunas de las bibliotecas clave incluyen:

- Django 5.2.5
- psycopg2-binary / psycopg2 (Driver para PostgreSQL)
- whitenoise 6.9.0
- python-dotenv 1.1.1

## Preparación del Entorno (Setup)

1. Clonar el repositorio
   ```bash
   git clone <url-del-repositorio>
   cd matelab
   ```

2. Crear y activar un entorno virtual
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instalar dependencias
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Variables de Entorno

El proyecto lee variables desde el archivo .env o .env.prod para aislar configuraciones sensibles (ver config/settings.py). Crea un archivo .env en la raíz del proyecto basándote en este ejemplo:

```env
# Configuracion Base de Django
SECRET_KEY=tu_clave_secreta_segura_y_aleatoria
DJANGO_ENVIRONMENT=local
BASE_URL=http://127.0.0.1:8000
DEBUG=True

# Credenciales de PostgreSQL
DB_NAME=matelab_db
DB_USER=postgres
DB_PASSWORD=tu_password_seguro
DB_HOST=127.0.0.1
DB_PORT=5432
```

Nota: Para entornos de producción, utiliza un archivo .env.prod y asegúrate estrictamente de configurar DEBUG=False.

## Base de Datos, Migraciones y Sembrado

Antes de ejecutar las migraciones, asegúrate de que tu servidor PostgreSQL esté corriendo y de haber creado la base de datos definida en tu archivo .env (matelab_db en el ejemplo).

1. Aplicar las migraciones a la Base de Datos:
   ```bash
   python manage.py migrate
   ```

2. Setup y Sembrado de Datos Iniciales:
   En lugar de crear usuarios de forma manual, utilizamos nuestro comando personalizado para inicializar la plataforma. Este es el paso principal para dejar la plataforma operativa. Generará los roles necesarios, usuarios base y poblará las tablas pedagógicas:
   ```bash
   python manage.py seed_matelab
   ```
   (Este paso reemplaza completamente la dependencia del clásico createsuperuser y deja tu base de datos lista para pruebas).

## Ejecutar en Desarrollo

Levanta el servidor de desarrollo local de Django:

```bash
python manage.py runserver
```

La aplicación estará disponible por defecto en: http://127.0.0.1:8000

Si deseas exponer el servicio en todas las interfaces de red (útil para probar en otros dispositivos locales):
```bash
python manage.py runserver 0.0.0.0:8000
```

## Estructura Relevante del Proyecto

El proyecto sigue una arquitectura modular enfocada en la escalabilidad:

- manage.py: Punto de entrada de la línea de comandos de Django.
- config/settings.py: Configuración global (Base de datos, apps instaladas, plantillas, estáticos, etc.).
- apps/: Directorio principal de las aplicaciones del negocio.
  - apps.authentication: Gestión de autenticación, sesiones y el modelo personalizado Usuarios.
  - apps.misiones: Lógica core del motor adaptativo, métricas de telemetría y flujo de misiones.
  - apps.biblioteca: Gestión de recursos y material de apoyo.
  - apps.dashboards: Vistas y controladores para los paneles de métricas administrativas.
- templates/: Plantillas HTML globales y componentes de interfaz.
- src/assets: Archivos estáticos en tiempo de desarrollo (CSS, JS, imágenes).
- staticfiles/: Directorio autogenerado que agrupa los estáticos listos para producción tras ejecutar collectstatic.

## Comandos Comunes de Referencia

- Generar nuevas migraciones: python manage.py makemigrations
- Aplicar migraciones: python manage.py migrate
- Sembrar datos iniciales: python manage.py seed_matelab
- Ejecutar pruebas unitarias: python manage.py test
- Recolectar estáticos (Producción): python manage.py collectstatic

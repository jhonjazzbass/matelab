# Imagen base de Python (Debian 12 slim)
FROM python:3.11-slim

# No generar .pyc y logueo sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# --------- Instalar dependencias de sistema ---------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    libpq-dev \
    gcc \
    python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# --------- Instalar dependencias de Python ---------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --------- Copiar código del proyecto ---------
COPY . .

# Variables por defecto dentro del contenedor
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PORT=8000

# --------- Collectstatic (usa tus settings de STATIC_ROOT) ---------
RUN python manage.py collectstatic --noinput

# --------- Comando de arranque ---------
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
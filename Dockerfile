# Imagen base de Python (Debian 12 slim)
FROM python:3.11-slim

# No generar .pyc y logueo sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# --------- Instalar dependencias de sistema + driver ODBC 17 ---------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    unixodbc-dev && \
    mkdir -p /usr/share/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 && \
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
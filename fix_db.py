import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    try:
        cursor.execute('ALTER TABLE "Progreso_Habilidad" DROP CONSTRAINT "Progreso_Habilidad_pkey";')
        print("Dropped Progreso_Habilidad_pkey")
    except Exception as e:
        print("Error on Progreso_Habilidad:", e)
        
    try:
        cursor.execute('ALTER TABLE "Trofeo_Estudiante" DROP CONSTRAINT "Trofeo_Estudiante_pkey";')
        print("Dropped Trofeo_Estudiante_pkey")
    except Exception as e:
        print("Error on Trofeo_Estudiante:", e)

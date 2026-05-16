import os
from django.core.management.base import BaseCommand
from apps.authentication.models import Rol, Usuarios
from apps.misiones.models import Habilidad, Mision
from apps.biblioteca.models import Biblioteca, Biblioteca_Contenido

class Command(BaseCommand):
    help = 'Puebla la base de datos con los registros base (Roles, Usuarios, Habilidades, Misiones, Biblioteca)'

    def handle(self, *args, **kwargs):
        self.stdout.write("=== Iniciando Sembrado de Base de Datos (Seed) ===")

        # 1. Crear Roles
        roles_data = ['Administrador', 'Profesor', 'Estudiante']
        roles_dict = {}
        for r in roles_data:
            rol, created = Rol.objects.get_or_create(tipo=r)
            roles_dict[r] = rol
            if created:
                self.stdout.write(self.style.SUCCESS(f"Rol creado: {r}"))

        # 2. Crear Usuarios
        usuarios_data = [
            {'username': 'admin', 'rol': 'Administrador'},
            {'username': 'profesor', 'rol': 'Profesor'},
            {'username': 'alumno', 'rol': 'Estudiante'},
        ]
        users_dict = {}
        for u in usuarios_data:
            user, created = Usuarios.objects.get_or_create(
                nombre_usuario=u['username'],
                defaults={
                    'rol': roles_dict[u['rol']],
                    'estado': True
                }
            )
            if created:
                user.set_password('123456')
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {u['username']} (Pass: 123456)"))
            users_dict[u['username']] = user

        # 3. Crear Habilidades
        hab_suma, created = Habilidad.objects.get_or_create(nombre='Aritmética: Suma')
        if created:
            self.stdout.write(self.style.SUCCESS("Habilidad creada: Aritmética: Suma"))

        # 4. Crear Biblioteca
        bib_suma, created = Biblioteca.objects.get_or_create(
            titulo='Introducción a la Suma',
            defaults={
                'descripcion': 'Aprende los conceptos básicos de la suma con este material.',
                'solucion': 'Sumar es juntar cosas.',
                'tipo': 'Contenido',
                'usuario': users_dict['profesor'],
                'activo': True
            }
        )
        if created:
            Biblioteca_Contenido.objects.create(
                biblioteca=bib_suma,
                teoria='La suma consiste en juntar dos o más elementos para saber cuántos hay en total.',
                pasos_trucos='1. Alinear números.\\n2. Sumar unidades.\\n3. Sumar decenas y centenas.',
                ejemplo='15 + 12 = 27',
                tipo='suma'
            )
            self.stdout.write(self.style.SUCCESS("Contenido de Biblioteca creado: Introducción a la Suma"))

        # 5. Crear Misiones (Nivel 1, Nivel 2 y Nivel 3)
        misiones_data = [
            {
                'titulo': 'Misión Fácil: Las Manzanas de Juan',
                'descripcion': 'Juan tiene 15 manzanas y compra 12. ¿Cuántas tiene?',
                'instrucciones_polya': 'Sigue los 4 pasos de Pólya de manera obligatoria para resolver este problema.',
                'tipo_operacion': 'suma',
                'nivel_dificultad': '1',
                'alternativa1': '25',
                'alternativa2': '26',
                'alternativa3': '28',
                'solucion_correcta': '27',
            },
            {
                'titulo': 'Misión Media: Ventas de la Tienda',
                'descripcion': 'Una tienda vende 145 libros el lunes y 287 el martes. ¿Total vendido?',
                'instrucciones_polya': 'Sigue los 4 pasos de Pólya de manera obligatoria para resolver este problema.',
                'tipo_operacion': 'suma',
                'nivel_dificultad': '2',
                'alternativa1': '422',
                'alternativa2': '430',
                'alternativa3': '442',
                'solucion_correcta': '432',
            },
            {
                'titulo': 'Misión Difícil: Producción de la Fábrica',
                'descripcion': 'La fábrica produjo 1540 piezas, luego 2380, y finalmente 95. ¿Total?',
                'instrucciones_polya': 'Sigue los 4 pasos de Pólya de manera obligatoria para resolver este problema.',
                'tipo_operacion': 'suma',
                'nivel_dificultad': '3',
                'alternativa1': '4005',
                'alternativa2': '4115',
                'alternativa3': '3915',
                'solucion_correcta': '4015',
            }
        ]

        for m_data in misiones_data:
            mision, created = Mision.objects.get_or_create(
                titulo=m_data['titulo'],
                defaults={
                    'habilidad': hab_suma,
                    'descripcion': m_data['descripcion'],
                    'instrucciones_polya': m_data['instrucciones_polya'],
                    'tipo_operacion': m_data['tipo_operacion'],
                    'nivel_dificultad': m_data['nivel_dificultad'],
                    'alternativa1': m_data['alternativa1'],
                    'alternativa2': m_data['alternativa2'],
                    'alternativa3': m_data['alternativa3'],
                    'solucion_correcta': m_data['solucion_correcta'],
                    'activa': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Misión creada: {m_data['titulo']} (Nivel {m_data['nivel_dificultad']})"))

        self.stdout.write(self.style.SUCCESS("=== Sembrado Completado con Éxito ==="))

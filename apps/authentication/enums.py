# apps/authentication/enums.py
from enum import Enum

class UserRole(Enum):
    ESTUDIANTE = 'Estudiante'
    PROFESOR = 'Profesor'
    ADMIN = 'Admin'
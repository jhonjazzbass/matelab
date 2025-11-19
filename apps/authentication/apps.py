# apps/authentication/apps.py
from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    name = 'apps.authentication'
    label = 'authentication'  # Use a simple label without dots
    verbose_name = 'Authentication'
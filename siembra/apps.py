"""
apps.py — App: siembra
Configuración de la app Django para el módulo de Siembra del Cultivo.
"""

from django.apps import AppConfig


class SiembraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "siembra"
    verbose_name = "Siembra del Cultivo"

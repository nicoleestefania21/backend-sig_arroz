"""
admin.py — App: siembra
Registro de modelos en el panel de administración de Django.
"""

from django.contrib import admin
from .models import CicloProductivo, Siembra


@admin.register(CicloProductivo)
class CicloProductivoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "fecha_inicio", "fecha_fin", "activo", "created_at"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Siembra)
class SiembraAdmin(admin.ModelAdmin):
    list_display = ["id", "fecha_siembra", "variedad", "metodo", "lote", "ciclo", "created_at"]
    list_filter = ["metodo", "ciclo"]
    search_fields = ["variedad", "lote__nombre"]
    date_hierarchy = "fecha_siembra"

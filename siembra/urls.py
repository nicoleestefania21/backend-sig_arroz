"""
urls.py — App: siembra
Registro de rutas para los ViewSets del módulo de Siembra.

El DefaultRouter genera automáticamente las rutas estándar:

  Siembras:
    GET  /api/siembra/        → SiembraViewSet.list()
    POST /api/siembra/        → SiembraViewSet.create()
    GET  /api/siembra/{id}/   → SiembraViewSet.retrieve()

  Ciclos Productivos:
    GET  /api/ciclos/         → CicloProductivoViewSet.list()
    POST /api/ciclos/         → CicloProductivoViewSet.create()
    GET  /api/ciclos/{id}/    → CicloProductivoViewSet.retrieve()
    PUT  /api/ciclos/{id}/    → CicloProductivoViewSet.update()
    DEL  /api/ciclos/{id}/    → CicloProductivoViewSet.destroy()

Nota: el SiembraViewSet limita http_method_names a GET y POST;
las rutas de detalle PUT/PATCH/DELETE existen en la URL pero
retornan 405 Method Not Allowed si se intentan usar.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CicloProductivoViewSet, SiembraViewSet

# Instanciamos el router y registramos ambos ViewSets
router = DefaultRouter()
router.register(r"siembra", SiembraViewSet, basename="siembra")
router.register(r"ciclos", CicloProductivoViewSet, basename="ciclo")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CicloProductivoViewSet,
    PlanificacionCicloViewSet,
    HistorialCicloViewSet,
)

router = DefaultRouter()
router.register(r'ciclos', CicloProductivoViewSet, basename='ciclo')
router.register(r'planificaciones', PlanificacionCicloViewSet, basename='planificacion')
router.register(r'historial', HistorialCicloViewSet, basename='historial')

urlpatterns = [
    path('', include(router.urls)),
]
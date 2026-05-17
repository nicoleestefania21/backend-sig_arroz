from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MonitoreoCultivoViewSet,
    MonitoreoBiologicoViewSet,
    MonitoreoFitosanitarioViewSet,
    RegistroPlagaViewSet,
    RegistroEnfermedadViewSet,
    EstadoGeneralCultivoViewSet,
)

router = DefaultRouter()
router.register(r'monitoreos', MonitoreoCultivoViewSet, basename='monitoreo')
router.register(r'monitoreos-biologicos', MonitoreoBiologicoViewSet, basename='monitoreo-biologico')
router.register(r'monitoreos-fitosanitarios', MonitoreoFitosanitarioViewSet, basename='monitoreo-fitosanitario')
router.register(r'plagas', RegistroPlagaViewSet, basename='plaga')
router.register(r'enfermedades', RegistroEnfermedadViewSet, basename='enfermedad')
router.register(r'estados-generales', EstadoGeneralCultivoViewSet, basename='estado-general')

urlpatterns = [
    path('', include(router.urls)),
]

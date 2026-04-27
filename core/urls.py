# core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FincaViewSet, LoteViewSet, LotesPorFincaView, LaborTerrenoViewSet

router = DefaultRouter()
router.register(r'fincas', FincaViewSet)
router.register(r'lotes', LoteViewSet)
router.register(r'labores', LaborTerrenoViewSet)

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),

    # Usuarios (auth, registro, recuperación de contraseña, perfil)
    path('api/users/', include('users.urls')),

    # Endpoints de core (fincas, lotes, labores)
    # GET/POST /api/fincas/
    # GET/POST /api/lotes/
    # GET/POST /api/labores/
    path('api/', include(router.urls)),

    # Endpoint específico para traer lotes por finca:
    # GET /api/fincas/lotes/?finca_id=...
    path(
        'api/fincas/lotes/',
        LotesPorFincaView.as_view(),
        name='lotes-por-finca'
    ),

    # Rutas de la app ciclos, si ya existe
    # Ejemplo: /api/ciclos/...
    path('api/', include('ciclos.urls')),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
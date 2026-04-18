from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FincaViewSet, LoteViewSet

# Configuración del Router de Fernando
router = DefaultRouter()
router.register(r'fincas', FincaViewSet)
router.register(r'lotes', LoteViewSet)

urlpatterns = [
    # Ruta base de Django
    path('admin/', admin.site.urls),
    
    # rutas probadas (Neon/Usuarios)
    path('api/users/', include('users.urls')),
    
    # rutas exactas probadas de Fernando (Fincas/Lotes)
    path('', include(router.urls)),
]
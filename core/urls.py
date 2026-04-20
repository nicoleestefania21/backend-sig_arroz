from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FincaViewSet, LoteViewSet, LotesPorFincaView

router = DefaultRouter()
router.register(r'fincas', FincaViewSet)
router.register(r'lotes', LoteViewSet)

urlpatterns = [
    path('users/', include('users.urls')),
    path('fincas/lotes/', LotesPorFincaView.as_view(), name='lotes-por-finca'),
    path('', include(router.urls)),
]
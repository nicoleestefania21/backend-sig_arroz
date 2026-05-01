from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FincaViewSet, LoteViewSet, LotesPorFincaView, LaborTerrenoViewSet

router = DefaultRouter()
router.register(r'fincas', FincaViewSet)
router.register(r'lotes', LoteViewSet)
router.register(r'labores', LaborTerrenoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "fincas/<int:finca_id>/lotes/",
        LotesPorFincaView.as_view(),
        name="lotes-por-finca",
    ),
]
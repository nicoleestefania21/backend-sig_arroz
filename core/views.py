from rest_framework import viewsets, generics, filters
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Finca, Lote, LaborTerreno, Siembra
from .serializers import (
    FincaSerializer,
    LoteSerializer,
    LotesPorFincaSerializer,
    LaborTerrenoSerializer,
    SiembraSerializer,
)
from users.permissions import IsProductorOrTecnicoOrAdmin


class FincaViewSet(viewsets.ModelViewSet):
    queryset = Finca.objects.all().order_by("nombre")
    serializer_class = FincaSerializer
    permission_classes = [IsAuthenticated]


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all().select_related("finca").order_by("nombre")
    serializer_class = LoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        finca_id = self.request.query_params.get("finca")
        queryset = super().get_queryset()
        if finca_id:
            queryset = queryset.filter(finca_id=finca_id)
        return queryset


class LotesPorFincaView(generics.ListAPIView):
    serializer_class = LotesPorFincaSerializer
    permission_classes = [IsAuthenticated, IsProductorOrTecnicoOrAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["nombre", "area", "estado"]
    ordering = ["nombre"]

    def get_queryset(self):
        finca_id = self.kwargs["finca_id"]

        if not Finca.objects.filter(pk=finca_id).exists():
            raise NotFound(detail=f"No existe una finca con id={finca_id}.")

        qs = Lote.objects.filter(finca_id=finca_id).select_related("finca")

        estado = self.request.query_params.get("estado")
        if estado:
            estado = estado.upper()
            estados_validos = [c[0] for c in Lote.ESTADO_CHOICES]
            if estado not in estados_validos:
                raise ValidationError(
                    {"estado": f"Valor inválido. Opciones: {', '.join(estados_validos)}"}
                )
            qs = qs.filter(estado=estado)

        return qs


class LaborTerrenoViewSet(viewsets.ModelViewSet):
    serializer_class = LaborTerrenoSerializer
    permission_classes = [IsAuthenticated, IsProductorOrTecnicoOrAdmin]
    queryset = LaborTerreno.objects.all().select_related("lote", "lote__finca").order_by("-fecha", "-id")

    def get_queryset(self):
        queryset = super().get_queryset()

        lote_id = self.request.query_params.get("lote")
        finca_id = self.request.query_params.get("finca")
        tipo_labor = self.request.query_params.get("tipo_labor")
        fecha = self.request.query_params.get("fecha")

        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        if finca_id:
            queryset = queryset.filter(lote__finca_id=finca_id)
        if tipo_labor:
            queryset = queryset.filter(tipo_labor__icontains=tipo_labor)
        if fecha:
            queryset = queryset.filter(fecha=fecha)

        return queryset
    
class SiembraViewSet(viewsets.ModelViewSet):
    serializer_class = SiembraSerializer
    permission_classes = [IsAuthenticated, IsProductorOrTecnicoOrAdmin]
    queryset = Siembra.objects.all().select_related("lote", "lote__finca").order_by("-fecha_siembra", "-id")

    def get_queryset(self):
        queryset = super().get_queryset()

        lote_id = self.request.query_params.get("lote")
        finca_id = self.request.query_params.get("finca")
        metodo = self.request.query_params.get("metodo")
        fecha = self.request.query_params.get("fecha_siembra")

        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        if finca_id:
            queryset = queryset.filter(lote__finca_id=finca_id)
        if metodo:
            queryset = queryset.filter(metodo_siembra=metodo.upper())
        if fecha:
            queryset = queryset.filter(fecha_siembra=fecha)

        return queryset
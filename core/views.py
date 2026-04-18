from rest_framework import viewsets, generics, filters
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Finca, Lote
from .serializers import FincaSerializer, LoteSerializer, LotesPorFincaSerializer
from users.permissions import IsProductorOrTecnicoOrAdmin


class FincaViewSet(viewsets.ModelViewSet):
    queryset = Finca.objects.all()
    serializer_class = FincaSerializer


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer

    def get_queryset(self):
        finca_id = self.request.query_params.get('finca')
        if finca_id:
            return Lote.objects.filter(finca_id=finca_id)
        return super().get_queryset()


class LotesPorFincaView(generics.ListAPIView):
    """
    HU: Como productor o técnico, quiero consultar los lotes registrados
    por finca, para identificar su disponibilidad, características y estado.

    GET /api/fincas/{finca_id}/lotes/
    GET /api/fincas/{finca_id}/lotes/?estado=DISPONIBLE
    GET /api/fincas/{finca_id}/lotes/?estado=EN_USO
    GET /api/fincas/{finca_id}/lotes/?estado=EN_PREPARACION
    GET /api/fincas/{finca_id}/lotes/?estado=INACTIVO
    GET /api/fincas/{finca_id}/lotes/?ordering=area
    """
    serializer_class = LotesPorFincaSerializer
    permission_classes = [IsAuthenticated, IsProductorOrTecnicoOrAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['nombre', 'area', 'estado']
    ordering = ['nombre']

    def get_queryset(self):
        finca_id = self.kwargs['finca_id']

        # Verificar que la finca existe
        if not Finca.objects.filter(pk=finca_id).exists():
            raise NotFound(detail=f"No existe una finca con id={finca_id}.")

        qs = Lote.objects.filter(finca_id=finca_id).select_related('finca')

        # Filtro opcional por estado
        estado = self.request.query_params.get('estado')
        if estado:
            estado = estado.upper()
            estados_validos = [c[0] for c in Lote.ESTADO_CHOICES]
            if estado not in estados_validos:
                raise ValidationError(
                    {"estado": f"Valor inválido. Opciones: {', '.join(estados_validos)}"}
                )
            qs = qs.filter(estado=estado)

        return qs

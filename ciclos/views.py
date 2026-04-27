from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import NotFound, ValidationError

from .models import CicloProductivo, PlanificacionCiclo, HistorialCiclo
from .serializers import (
    CicloProductivoSerializer,
    CicloProductivoCreateSerializer,
    CicloProductivoDetalleSerializer,
    PlanificacionCicloSerializer,
    HistorialCicloSerializer,
)


class IsTecnicoOrAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['TECNICO', 'ADMIN']
        )


class CicloProductivoViewSet(viewsets.ModelViewSet):
    """
    RF-06: Crear ciclos productivos de arroz asociados a un lote.
    RF-09: Asociar lotes a ciclos productivos.
    RF-10: Consultar historial de ciclos productivos por lote.
    """
    queryset = CicloProductivo.objects.all().select_related(
        'lote', 'planificacion'
    ).prefetch_related('historial')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy',
                           'activar', 'cerrar']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CicloProductivoCreateSerializer
        if self.action == 'retrieve':
            return CicloProductivoDetalleSerializer
        return CicloProductivoSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        lote_id = self.request.query_params.get('lote')
        if lote_id:
            qs = qs.filter(lote_id=lote_id)

        estado = self.request.query_params.get('estado')
        if estado:
            estado = estado.upper()
            estados_validos = [e[0] for e in CicloProductivo.ESTADO_CHOICES]
            if estado not in estados_validos:
                raise ValidationError(
                    {"estado": f"Valor inválido. Opciones: {', '.join(estados_validos)}"}
                )
            qs = qs.filter(estado=estado)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ciclo = serializer.save()
        return Response(
            CicloProductivoDetalleSerializer(ciclo).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Cambia el ciclo de PLANIFICADO a ACTIVO."""
        ciclo = self.get_object()
        if ciclo.estado != CicloProductivo.PLANIFICADO:
            raise ValidationError(
                "Solo se puede activar un ciclo en estado Planificado."
            )
        estado_anterior = ciclo.estado
        ciclo.estado = CicloProductivo.ACTIVO
        ciclo.save()

        HistorialCiclo.objects.create(
            ciclo=ciclo,
            estado_anterior=estado_anterior,
            estado_nuevo=ciclo.estado,
            observacion=request.data.get('observacion', 'Ciclo activado.')
        )
        return Response(
            {"message": "Ciclo activado exitosamente.",
             "estado": ciclo.estado},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        """Cambia el ciclo de ACTIVO a CERRADO."""
        ciclo = self.get_object()
        if ciclo.estado != CicloProductivo.ACTIVO:
            raise ValidationError(
                "Solo se puede cerrar un ciclo en estado Activo."
            )
        estado_anterior = ciclo.estado
        ciclo.estado = CicloProductivo.CERRADO
        ciclo.save()

        HistorialCiclo.objects.create(
            ciclo=ciclo,
            estado_anterior=estado_anterior,
            estado_nuevo=ciclo.estado,
            observacion=request.data.get('observacion', 'Ciclo cerrado.')
        )
        return Response(
            {"message": "Ciclo cerrado exitosamente.",
             "estado": ciclo.estado},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """RF-10: Consultar historial de un ciclo específico."""
        ciclo = self.get_object()
        historial = ciclo.historial.all()
        serializer = HistorialCicloSerializer(historial, many=True)
        return Response(serializer.data)


class PlanificacionCicloViewSet(viewsets.ModelViewSet):
    """
    RF-07: Definir cronograma de actividades agrícolas por ciclo.
    RF-08: Registrar fechas clave del ciclo (preparación, siembra, cosecha).
    """
    queryset = PlanificacionCiclo.objects.all().select_related('ciclo')
    serializer_class = PlanificacionCicloSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        ciclo_id = self.request.query_params.get('ciclo')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        return qs

    def perform_create(self, serializer):
        ciclo = serializer.validated_data.get('ciclo')
        if ciclo.estado not in [CicloProductivo.PLANIFICADO, CicloProductivo.ACTIVO]:
            raise ValidationError(
                "Solo se puede definir cronograma en ciclos Planificados o Activos."
            )
        serializer.save()

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.ciclo.estado == CicloProductivo.CERRADO:
            raise ValidationError(
                "No se puede modificar el cronograma de un ciclo Cerrado."
            )
        serializer.save()


class HistorialCicloViewSet(viewsets.ReadOnlyModelViewSet):
    """
    RF-10: Consultar historial de ciclos productivos por lote.
    """
    queryset = HistorialCiclo.objects.all().select_related('ciclo')
    serializer_class = HistorialCicloSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()

        ciclo_id = self.request.query_params.get('ciclo')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)

        lote_id = self.request.query_params.get('lote')
        if lote_id:
            qs = qs.filter(ciclo__lote_id=lote_id)

        return qs
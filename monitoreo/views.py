from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import ValidationError

from .models import (
    MonitoreoCultivo,
    MonitoreoBiologico,
    MonitoreoFitosanitario,
    RegistroPlaga,
    RegistroEnfermedad,
    EstadoGeneralCultivo,
)
from .serializers import (
    MonitoreoCultivoSerializer,
    MonitoreoCultivoCreateSerializer,
    MonitoreoCultivoListSerializer,
    MonitoreoBiologicoSerializer,
    MonitoreoFitosanitarioSerializer,
    MonitoreoFitosanitarioCreateSerializer,
    RegistroPlagaSerializer,
    RegistroEnfermedadSerializer,
    EstadoGeneralCultivoSerializer,
)


class IsTecnicoOrAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['TECNICO', 'ADMIN']
        )


class MonitoreoCultivoViewSet(viewsets.ModelViewSet):
    
    queryset = MonitoreoCultivo.objects.all().select_related(
        'ciclo',
        'ciclo__lote',
        'ciclo__lote__finca',
        'biologico',
        'fitosanitario',
        'estado_general',
    ).prefetch_related(
        'fitosanitario__plagas',
        'fitosanitario__enfermedades',
    ).order_by('-fecha_monitoreo', '-id')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return MonitoreoCultivoListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return MonitoreoCultivoCreateSerializer
        return MonitoreoCultivoSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        ciclo_id = self.request.query_params.get('ciclo')
        lote_id = self.request.query_params.get('lote')
        finca_id = self.request.query_params.get('finca')
        fecha = self.request.query_params.get('fecha')

        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        if lote_id:
            qs = qs.filter(ciclo__lote_id=lote_id)
        if finca_id:
            qs = qs.filter(ciclo__lote__finca_id=finca_id)
        if fecha:
            qs = qs.filter(fecha_monitoreo=fecha)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        monitoreo = serializer.save()
        return Response(
            MonitoreoCultivoSerializer(
                monitoreo,
                context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        monitoreo = serializer.save()
        return Response(
            MonitoreoCultivoSerializer(
                monitoreo,
                context=self.get_serializer_context()
            ).data
        )

    @action(detail=True, methods=['get'])
    def biologico(self, request, pk=None):
        """RF-30: Consulta el monitoreo biológico de un monitoreo específico."""
        monitoreo = self.get_object()
        if not hasattr(monitoreo, 'biologico') or monitoreo.biologico is None:
            return Response(
                {"detail": "Este monitoreo no tiene registro biológico."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MonitoreoBiologicoSerializer(monitoreo.biologico)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def fitosanitario(self, request, pk=None):
        """RF-31: Consulta el monitoreo fitosanitario de un monitoreo específico."""
        monitoreo = self.get_object()
        if not hasattr(monitoreo, 'fitosanitario') or monitoreo.fitosanitario is None:
            return Response(
                {"detail": "Este monitoreo no tiene registro fitosanitario."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MonitoreoFitosanitarioSerializer(monitoreo.fitosanitario)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def estado_general(self, request, pk=None):
        """RF-32: Consulta el estado general del cultivo de un monitoreo específico."""
        monitoreo = self.get_object()
        if not hasattr(monitoreo, 'estado_general') or monitoreo.estado_general is None:
            return Response(
                {"detail": "Este monitoreo no tiene registro de estado general."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EstadoGeneralCultivoSerializer(monitoreo.estado_general)
        return Response(serializer.data)


class MonitoreoBiologicoViewSet(viewsets.ModelViewSet):
    """
    RF-30: CRUD independiente para el monitoreo biológico.
    Permite gestionar el monitoreo biológico de forma separada si se requiere.
    """
    queryset = MonitoreoBiologico.objects.all().select_related(
        'monitoreo', 'monitoreo__ciclo', 'monitoreo__ciclo__lote'
    )
    serializer_class = MonitoreoBiologicoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        monitoreo_id = self.request.query_params.get('monitoreo')
        ciclo_id = self.request.query_params.get('ciclo')
        if monitoreo_id:
            qs = qs.filter(monitoreo_id=monitoreo_id)
        if ciclo_id:
            qs = qs.filter(monitoreo__ciclo_id=ciclo_id)
        return qs

    def perform_create(self, serializer):
        monitoreo = serializer.validated_data.get('monitoreo')
        if hasattr(monitoreo, 'biologico') and monitoreo.biologico is not None:
            raise ValidationError(
                "Este monitoreo ya tiene un registro biológico. "
                "Use el endpoint de actualización."
            )
        serializer.save()


class MonitoreoFitosanitarioViewSet(viewsets.ModelViewSet):
    """
    RF-31: CRUD independiente para el monitoreo fitosanitario.
    """
    queryset = MonitoreoFitosanitario.objects.all().select_related(
        'monitoreo', 'monitoreo__ciclo', 'monitoreo__ciclo__lote'
    ).prefetch_related('plagas', 'enfermedades')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MonitoreoFitosanitarioCreateSerializer
        return MonitoreoFitosanitarioSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        monitoreo_id = self.request.query_params.get('monitoreo')
        ciclo_id = self.request.query_params.get('ciclo')
        if monitoreo_id:
            qs = qs.filter(monitoreo_id=monitoreo_id)
        if ciclo_id:
            qs = qs.filter(monitoreo__ciclo_id=ciclo_id)
        return qs

    def perform_create(self, serializer):
        monitoreo = serializer.validated_data.get('monitoreo')
        if hasattr(monitoreo, 'fitosanitario') and monitoreo.fitosanitario is not None:
            raise ValidationError(
                "Este monitoreo ya tiene un registro fitosanitario. "
                "Use el endpoint de actualización."
            )
        serializer.save()


class RegistroPlagaViewSet(viewsets.ModelViewSet):
    """
    RF-31: CRUD para registros individuales de plagas.
    """
    queryset = RegistroPlaga.objects.all().select_related(
        'monitoreo_fitosanitario',
        'monitoreo_fitosanitario__monitoreo',
    )
    serializer_class = RegistroPlagaSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        fitosanitario_id = self.request.query_params.get('fitosanitario')
        ciclo_id = self.request.query_params.get('ciclo')
        nivel = self.request.query_params.get('nivel')
        if fitosanitario_id:
            qs = qs.filter(monitoreo_fitosanitario_id=fitosanitario_id)
        if ciclo_id:
            qs = qs.filter(
                monitoreo_fitosanitario__monitoreo__ciclo_id=ciclo_id
            )
        if nivel:
            qs = qs.filter(nivel_infestacion=nivel.upper())
        return qs


class RegistroEnfermedadViewSet(viewsets.ModelViewSet):
    """
    RF-31: CRUD para registros individuales de enfermedades.
    """
    queryset = RegistroEnfermedad.objects.all().select_related(
        'monitoreo_fitosanitario',
        'monitoreo_fitosanitario__monitoreo',
    )
    serializer_class = RegistroEnfermedadSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        fitosanitario_id = self.request.query_params.get('fitosanitario')
        ciclo_id = self.request.query_params.get('ciclo')
        severidad = self.request.query_params.get('severidad')
        if fitosanitario_id:
            qs = qs.filter(monitoreo_fitosanitario_id=fitosanitario_id)
        if ciclo_id:
            qs = qs.filter(
                monitoreo_fitosanitario__monitoreo__ciclo_id=ciclo_id
            )
        if severidad:
            qs = qs.filter(severidad=severidad.upper())
        return qs


class EstadoGeneralCultivoViewSet(viewsets.ModelViewSet):
    """
    RF-32: CRUD independiente para el estado general del cultivo.
    """
    queryset = EstadoGeneralCultivo.objects.all().select_related(
        'monitoreo', 'monitoreo__ciclo', 'monitoreo__ciclo__lote'
    )
    serializer_class = EstadoGeneralCultivoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTecnicoOrAdminPermission()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        monitoreo_id = self.request.query_params.get('monitoreo')
        ciclo_id = self.request.query_params.get('ciclo')
        estado = self.request.query_params.get('estado')
        if monitoreo_id:
            qs = qs.filter(monitoreo_id=monitoreo_id)
        if ciclo_id:
            qs = qs.filter(monitoreo__ciclo_id=ciclo_id)
        if estado:
            qs = qs.filter(estado_general=estado.upper())
        return qs

    def perform_create(self, serializer):
        monitoreo = serializer.validated_data.get('monitoreo')
        if hasattr(monitoreo, 'estado_general') and monitoreo.estado_general is not None:
            raise ValidationError(
                "Este monitoreo ya tiene un registro de estado general. "
                "Use el endpoint de actualización."
            )
        serializer.save()

"""
views.py — App: siembra
ViewSets para los endpoints de Siembra y CicloProductivo.

Endpoints expuestos:
  POST   /api/siembra/                    → Registrar siembra  (TECNICO, OPERADOR)
  GET    /api/siembra/                    → Listar siembras    (TECNICO, OPERADOR, PRODUCTOR)
  GET    /api/siembra/?lote=1&ciclo=2     → Filtrar por lote y/o ciclo

  GET    /api/ciclos/                     → Listar ciclos productivos
  POST   /api/ciclos/                     → Crear ciclo (solo TECNICO)

Principios SOLID aplicados:
  · SRP: Cada ViewSet gestiona un único recurso.
  · OCP: El filtrado se extiende mediante query params sin modificar la vista.
  · DIP: Los permisos se inyectan vía permission_classes, no se codifican aquí.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CicloProductivo, Siembra
from .serializers import (
    CicloProductivoSerializer,
    SiembraReadSerializer,
    SiembraWriteSerializer,
)
from .permissions import PuedeAccederSiembra
from users.permissions import IsTecnicoUser


# ---------------------------------------------------------------------------
# CicloProductivo ViewSet
# ---------------------------------------------------------------------------

class CicloProductivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Ciclos Productivos.

    GET  /api/ciclos/      — Listar todos los ciclos (usuarios autenticados).
    POST /api/ciclos/      — Crear un ciclo (solo Técnico).
    GET  /api/ciclos/{id}/ — Detalle de un ciclo (usuarios autenticados).
    """

    queryset = CicloProductivo.objects.all().order_by("-fecha_inicio")
    serializer_class = CicloProductivoSerializer

    def get_permissions(self):
        """
        Determina los permisos según la acción:
          · 'create'  → solo IsTecnicoUser
          · resto     → cualquier usuario autenticado
        """
        if self.action == "create":
            # Solo el Técnico puede crear nuevos ciclos productivos
            return [IsAuthenticated(), IsTecnicoUser()]

        # Lectura abierta para cualquier usuario con sesión activa
        return [IsAuthenticated()]


# ---------------------------------------------------------------------------
# Siembra ViewSet
# ---------------------------------------------------------------------------

class SiembraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el registro y consulta de Siembras.

    HU-POST: Como Técnico u Operador, quiero registrar una siembra
             indicando fecha, variedad, método y densidad.
    HU-GET:  Como Técnico, Operador o Productor, quiero consultar el
             historial de siembras filtrado por lote y/o ciclo.

    Rutas generadas por el router:
      POST  /api/siembra/        → create()
      GET   /api/siembra/        → list()
      GET   /api/siembra/{id}/   → retrieve()
    """

    # Carga select_related para evitar N+1 queries al serializar lote y ciclo
    queryset = Siembra.objects.select_related("lote", "ciclo").order_by("-fecha_siembra")

    # Permiso unificado que diferencia entre lectura y escritura internamente
    permission_classes = [PuedeAccederSiembra]

    # ------------------------------------------------------------------
    # Selección dinámica de serializer (patrón Write/Read)
    # ------------------------------------------------------------------

    def get_serializer_class(self):
        """
        Devuelve el serializer apropiado según el tipo de operación:
          · Escritura (POST/PUT/PATCH) → SiembraWriteSerializer
          · Lectura   (GET)            → SiembraReadSerializer

        Esto permite tener validaciones estrictas al escribir y una
        representación enriquecida al leer, sin mezclar ambas lógicas.
        """
        if self.action in ("create", "update", "partial_update"):
            return SiembraWriteSerializer
        return SiembraReadSerializer

    # ------------------------------------------------------------------
    # Filtrado por query params (GET /api/siembra/?lote=1&ciclo=2)
    # ------------------------------------------------------------------

    def get_queryset(self):
        """
        Aplica filtros opcionales por lote y/o ciclo según los
        parámetros de consulta recibidos en la URL.

        Query params:
          · lote  (int) — ID del lote a filtrar.
          · ciclo (int) — ID del ciclo productivo a filtrar.

        Ambos filtros son independientes y acumulables.
        """
        qs = super().get_queryset()

        lote_id = self.request.query_params.get("lote")
        ciclo_id = self.request.query_params.get("ciclo")

        # Filtrar por lote si se proporciona el parámetro
        if lote_id:
            qs = qs.filter(lote_id=lote_id)

        # Filtrar por ciclo si se proporciona el parámetro
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)

        return qs

    # ------------------------------------------------------------------
    # Acciones limitadas: solo POST y GET están permitidos
    # ------------------------------------------------------------------

    http_method_names = ["get", "post", "head", "options"]
    """
    Se restringe el ViewSet a solo GET y POST.
    PUT, PATCH y DELETE no forman parte de este módulo según los
    requerimientos funcionales de la HU de Siembra.
    """

    # ------------------------------------------------------------------
    # Override de create para respuesta enriquecida
    # ------------------------------------------------------------------

    def create(self, request, *args, **kwargs):
        """
        Registra una nueva siembra.

        Tras crear el objeto con el WriteSerializer, retorna la
        representación completa usando el ReadSerializer (incluye
        nombres de lote, ciclo y label del método).
        """
        # 1. Validar y guardar con el WriteSerializer
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        siembra = write_serializer.save()

        # 2. Serializar la respuesta con el ReadSerializer (más informativo)
        read_serializer = SiembraReadSerializer(
            siembra,
            context=self.get_serializer_context(),
        )

        headers = self.get_success_headers(read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

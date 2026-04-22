"""
permissions.py — App: siembra
Permisos personalizados basados en el rol del usuario autenticado.

Roles disponibles (definidos en users.models.User):
  · ADMIN      — Administrador del sistema
  · TECNICO    — Técnico Agrícola
  · OPERADOR   — Operador de Campo
  · PRODUCTOR  — Productor Arrocero

Reglas de acceso para el módulo de Siembra:
  · Registrar (POST)  → TECNICO, OPERADOR
  · Consultar (GET)   → TECNICO, OPERADOR, PRODUCTOR

Principio aplicado (SRP):
  Cada clase de permiso tiene una única responsabilidad:
  verificar si el rol del usuario pertenece a un conjunto permitido.
"""

from rest_framework.permissions import BasePermission


class PuedeRegistrarSiembra(BasePermission):
    """
    Permiso para la acción de escritura (POST) en el endpoint de Siembra.

    Solo los roles TECNICO y OPERADOR pueden registrar nuevas siembras.
    El ADMIN no registra siembras directamente (lo hace mediante el panel
    de administración de Django), y el PRODUCTOR es un actor de solo lectura.
    """

    # Conjunto de roles autorizados para crear siembras
    ROLES_AUTORIZADOS = {"TECNICO", "OPERADOR"}

    message = (
        "No tienes permiso para registrar siembras. "
        "Esta acción está reservada para Técnicos y Operadores."
    )

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and request.user.role in self.ROLES_AUTORIZADOS
        )


class PuedeConsultarSiembra(BasePermission):
    """
    Permiso para la acción de lectura (GET) en el endpoint de Siembra.

    Los roles TECNICO, OPERADOR y PRODUCTOR pueden consultar el historial
    de siembras. El PRODUCTOR tiene acceso de lectura para monitorear
    el estado de sus cultivos.
    """

    # Conjunto de roles autorizados para consultar siembras
    ROLES_AUTORIZADOS = {"TECNICO", "OPERADOR", "PRODUCTOR"}

    message = (
        "No tienes permiso para consultar siembras. "
        "Esta acción está reservada para Técnicos, Operadores y Productores."
    )

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and request.user.role in self.ROLES_AUTORIZADOS
        )


class PuedeAccederSiembra(BasePermission):
    """
    Permiso unificado para el ViewSet de Siembra.

    Delega la lógica al método HTTP:
      · Métodos seguros  (GET, HEAD, OPTIONS) → PuedeConsultarSiembra
      · Métodos de escritura (POST)           → PuedeRegistrarSiembra

    De esta forma el ViewSet aplica un solo permission_class pero con
    comportamiento diferenciado por acción, siguiendo el principio OCP
    (abierto/cerrado): añadir nuevos métodos no requiere modificar las
    clases existentes.
    """

    METODOS_LECTURA = {"GET", "HEAD", "OPTIONS"}

    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False

        if request.method in self.METODOS_LECTURA:
            return PuedeConsultarSiembra().has_permission(request, view)

        # POST (y cualquier otro método de escritura que pueda agregarse)
        return PuedeRegistrarSiembra().has_permission(request, view)

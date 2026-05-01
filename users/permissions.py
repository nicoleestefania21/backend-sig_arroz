from rest_framework import permissions
from rest_framework.permissions import BasePermission

# Regla: Solo el administrador tiene permiso total
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "ADMIN"
        )

# Regla: Solo el técnico puede crear planes y monitoreos
class IsTecnicoUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'TECNICO'

# Regla: El productor solo puede ver la información de su ciclo
class IsProductorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'PRODUCTOR'

# Regla: El operador solo registra labores diarias
class IsOperadorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'OPERADOR'
    
    # HU: Consulta de lotes por finca — accesible para productor, técnico y admin
class IsProductorOrTecnicoOrAdmin(permissions.BasePermission):
    ROLES_PERMITIDOS = {'PRODUCTOR', 'TECNICO', 'ADMIN'}

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in self.ROLES_PERMITIDOS
        )
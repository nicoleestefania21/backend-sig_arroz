from rest_framework import permissions

# Regla: Solo el administrador tiene permiso total
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

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
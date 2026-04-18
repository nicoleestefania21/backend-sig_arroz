from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Esto hace que el modelo User sea visible y manejable en el Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Agregamos el campo 'role' y 'telefono' a la interfaz del admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información de SIG-Arroz', {'fields': ('role', 'telefono')}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']
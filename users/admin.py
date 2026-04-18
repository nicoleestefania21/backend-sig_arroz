from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Esto hace que el modelo User sea visible y manejable en el Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Se cambio 'telefono' por 'estado' en los campos extra
    fieldsets = UserAdmin.fieldsets + (
        ('Información de SIG-Arroz', {'fields': ('role', 'estado')}),
    )
    # Se agregó first_name, last_name y estado 
    list_display = ['username', 'first_name', 'last_name', 'email', 'role', 'estado', 'is_staff']
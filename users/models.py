from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 1. Definimos los roles
    ADMIN = 'ADMIN'
    TECNICO = 'TECNICO'
    PRODUCTOR = 'PRODUCTOR'
    OPERADOR = 'OPERADOR'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrador del Sistema'),
        (TECNICO, 'Técnico Agrícola'),
        (PRODUCTOR, 'Productor Arrocero'),
        (OPERADOR, 'Operador de Campo'),
    ]
    
    # 2. Creamos el campo para asignar el rol
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default=PRODUCTOR
    )
    
    # Un campo extra útil que suele pedirse
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Definicion de los roles
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

    # Definicion de los estados
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    # Campo para asignar el rol
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default=PRODUCTOR
    )
    
    # Campo para el estado 
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='ACTIVO'
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()} ({self.estado})"
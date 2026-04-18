from django.urls import path
from .views import RegisterUserView

urlpatterns = [
    # Tarea 4: Endpoint para registrar usuarios
    path('register/', RegisterUserView.as_view(), name='register'),
]
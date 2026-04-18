from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdminUser

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # CUMPLIMIENTO TAREA 2 Y 3: Solo un usuario autenticado y que sea ADMIN puede registrar
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Usuario registrado exitosamente como " + user.get_role_display(),
            "user": user.username
        }, status=status.HTTP_201_CREATED)
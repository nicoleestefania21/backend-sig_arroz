from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User
from .serializers import UserSerializer
from .permissions import IsAdminUser


class RegisterUserView(generics.CreateAPIView):
    """
    Solo un usuario autenticado con rol ADMIN puede crear otros usuarios.
    URL: POST /api/users/register/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Usuario registrado exitosamente como " + user.get_role_display(),
                "user": user.username,
            },
            status=status.HTTP_201_CREATED,
        )


class PasswordResetRequestView(APIView):
    """Solicitar recuperación de contraseña."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()
        response_msg = {
            "message": "Si el correo existe, recibirás instrucciones en breve."
        }

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(response_msg, status=status.HTTP_200_OK)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        send_mail(
            subject="Recuperación de contraseña — SIGARROZ",
            message=(
                f"Hola {user.first_name or user.username},\n\n"
                f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n"
                f"{reset_link}\n\n"
                "Si no solicitaste esto, ignora este mensaje."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return Response(response_msg, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Confirmar nueva contraseña."""
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([uid, token, new_password]):
            return Response(
                {"error": "Datos incompletos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Enlace inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "El enlace ha expirado o ya fue usado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Contraseña actualizada exitosamente."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Devuelve los datos del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class UserListView(generics.ListAPIView):
    """
    Lista de usuarios solo para ADMIN.
    GET /api/users/list/
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
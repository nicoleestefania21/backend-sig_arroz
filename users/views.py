from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

import traceback
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSerializer, EmailOrUsernameTokenObtainPairSerializer
from .permissions import IsAdminUser


class EmailOrUsernameTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": f"Usuario registrado exitosamente como {user.get_role_display()}",
                "user": user.username,
            },
            status=status.HTTP_201_CREATED,
        )


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        if user.id == request.user.id:
            return Response(
                {"detail": "No puedes eliminar tu propio usuario."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print("ENTRÓ A PASSWORD RESET")
            print("REQUEST DATA:", request.data)

            identifier = (request.data.get("identifier") or "").strip()
            print("IDENTIFIER:", identifier)

            response_msg = {
                "message": "Si la cuenta existe, recibirás instrucciones en breve."
            }

            if not identifier:
                return Response(
                    {"error": "Debes enviar el correo o usuario."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.filter(email__iexact=identifier).first()

            if not user:
                user = User.objects.filter(username__iexact=identifier).first()

            print("USER ENCONTRADO:", user)

            if not user or not user.email:
                return Response(response_msg, status=status.HTTP_200_OK)

            print("EMAIL DEL USER:", user.email)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/restablecer-contrasena/{uid}/{token}"

            print("FRONTEND_URL:", settings.FRONTEND_URL)
            print("RESET LINK:", reset_link)
            print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)
            print("ANTES DE SEND_MAIL")

            send_mail(
                subject="Recuperación de contraseña — SIGARROZ",
                message=(
                    f"Hola {user.first_name or user.username},\n\n"
                    f"Recibimos una solicitud para restablecer tu contraseña.\n"
                    f"Puedes hacerlo desde el siguiente enlace:\n\n"
                    f"{reset_link}\n\n"
                    "Si no solicitaste este cambio, ignora este mensaje."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            print("DESPUÉS DE SEND_MAIL")

            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            print("ERROR EN PASSWORD RESET:", str(e))
            print(traceback.format_exc())
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordResetValidateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            pk = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(
                {"valid": False, "detail": "Enlace inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"valid": False, "detail": "El enlace es inválido o ha expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"valid": True, "detail": "Token válido."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not password or not confirm_password:
            return Response(
                {"error": "Debes enviar y confirmar la nueva contraseña."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != confirm_password:
            return Response(
                {"error": "Las contraseñas no coinciden."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(password) < 8:
            return Response(
                {"error": "La contraseña debe tener al menos 8 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pk = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(
                {"error": "Enlace inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "El enlace es inválido o ha expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return Response(
            {"message": "Contraseña actualizada exitosamente."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterUserView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    MeView,
    UserListView,
    UserDetailView,
    EmailOrUsernameTokenObtainPairView,
)

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("list/", UserListView.as_view(), name="user_list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("token/", EmailOrUsernameTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
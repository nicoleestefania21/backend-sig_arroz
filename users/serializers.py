from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'role', 'telefono']
        # La contraseña se marca como 'write_only' para que no se vea en las respuestas
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usamos create_user para que Django encriptre la contraseña
        user = User.objects.create_user(**validated_data)
        return user
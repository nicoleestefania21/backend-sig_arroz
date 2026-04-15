from rest_framework import serializers
from .models import Finca, Lote


class FincaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finca
        fields = '__all__'

    def validate_area_total(self, value):
        if value <= 0:
            raise serializers.ValidationError("El área debe ser mayor a cero")
        return value


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = '__all__'

    def validate_area(self, value):
        if value <= 0:
            raise serializers.ValidationError("El área debe ser mayor a cero")
        return value
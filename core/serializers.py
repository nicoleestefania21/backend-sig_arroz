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
    disponible = serializers.BooleanField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Lote
        fields = '__all__'

    def validate_area(self, value):
        if value <= 0:
            raise serializers.ValidationError("El área debe ser mayor a cero")
        return value


class LotesPorFincaSerializer(serializers.ModelSerializer):
    """Serializer detallado para consulta de lotes por finca (productor/técnico)."""
    disponible = serializers.BooleanField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    finca_nombre = serializers.CharField(source='finca.nombre', read_only=True)

    class Meta:
        model = Lote
        fields = [
            'id',
            'nombre',
            'finca',
            'finca_nombre',
            'area',
            'tipo_suelo',
            'latitud',
            'longitud',
            'estado',
            'estado_display',
            'disponible',
            'observaciones',
        ]

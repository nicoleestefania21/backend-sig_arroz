from rest_framework import serializers
from .models import Finca, Lote, LaborTerreno


class FincaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finca
        fields = "__all__"

    def validate_area_total(self, value):
        if value <= 0:
            raise serializers.ValidationError("El área debe ser mayor a cero")
        return value


class LoteSerializer(serializers.ModelSerializer):
    disponible = serializers.BooleanField(read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Lote
        fields = "__all__"

    def validate_area(self, value):
        if value <= 0:
            raise serializers.ValidationError("El área debe ser mayor a cero")
        return value


class LotesPorFincaSerializer(serializers.ModelSerializer):
    disponible = serializers.BooleanField(read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    finca_nombre = serializers.CharField(source="finca.nombre", read_only=True)

    class Meta:
        model = Lote
        fields = [
            "id",
            "nombre",
            "finca",
            "finca_nombre",
            "area",
            "tipo_suelo",
            "latitud",
            "longitud",
            "estado",
            "estado_display",
            "disponible",
            "observaciones",
        ]


class LaborTerrenoSerializer(serializers.ModelSerializer):
    lote_nombre = serializers.CharField(source="lote.nombre", read_only=True)
    finca_id = serializers.IntegerField(source="lote.finca.id", read_only=True)
    finca_nombre = serializers.CharField(source="lote.finca.nombre", read_only=True)

    class Meta:
        model = LaborTerreno
        fields = [
            "id",
            "lote",
            "lote_nombre",
            "finca_id",
            "finca_nombre",
            "tipo_labor",
            "fecha",
            "ph",
            "humedad",
            "nivelacion",
            "drenaje",
            "adecuacion",
            "estado_terreno",
            "observaciones",
        ]

    def validate_ph(self, value):
        if value is not None and (value < 0 or value > 14):
            raise serializers.ValidationError("El pH debe estar entre 0 y 14.")
        return value

    def validate_humedad(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("La humedad debe estar entre 0 y 100.")
        return value
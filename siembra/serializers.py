"""
serializers.py — App: siembra
Serializers para CicloProductivo y Siembra.

Responsabilidades:
  · Validar que fecha_siembra no sea futura.
  · Validar que los campos obligatorios estén presentes.
  · Exponer información legible (display labels) en los responses.
"""

from datetime import date

from rest_framework import serializers

from .models import CicloProductivo, Siembra


# ---------------------------------------------------------------------------
# CicloProductivo
# ---------------------------------------------------------------------------

class CicloProductivoSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo CicloProductivo."""

    class Meta:
        model = CicloProductivo
        fields = [
            "id",
            "nombre",
            "fecha_inicio",
            "fecha_fin",
            "activo",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        """
        Validación a nivel objeto: verifica que fecha_fin no sea
        anterior a fecha_inicio cuando ambas están presentes.
        """
        fecha_inicio = attrs.get("fecha_inicio")
        fecha_fin = attrs.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        return attrs


# ---------------------------------------------------------------------------
# Siembra — escritura (POST)
# ---------------------------------------------------------------------------

class SiembraWriteSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar una siembra (POST).

    Aplica reglas de negocio:
      1. fecha_siembra no puede ser futura.
      2. variedad es obligatorio y no puede estar vacío.
      3. metodo debe pertenecer a los choices definidos en el modelo.
    """

    class Meta:
        model = Siembra
        fields = [
            "id",
            "fecha_siembra",
            "variedad",
            "densidad",
            "metodo",
            "lote",
            "ciclo",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    # ------------------------------------------------------------------
    # Validaciones de campo individual (field-level validators)
    # ------------------------------------------------------------------

    def validate_fecha_siembra(self, value: date) -> date:
        """
        Regla de negocio: no se puede registrar una siembra con fecha futura.
        Una siembra es un hecho ya ocurrido; registrarla hacia el futuro
        sería un error de captura de datos.
        """
        if value > date.today():
            raise serializers.ValidationError(
                "La fecha de siembra no puede ser una fecha futura. "
                f"Hoy es {date.today().isoformat()}."
            )
        return value

    def validate_variedad(self, value: str) -> str:
        """La variedad no puede ser una cadena vacía ni solo espacios."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "El campo 'variedad' es obligatorio y no puede estar vacío."
            )
        return value

    def validate_densidad(self, value):
        """Si se proporciona, la densidad debe ser un valor positivo."""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "La densidad debe ser un valor mayor a cero."
            )
        return value


# ---------------------------------------------------------------------------
# Siembra — lectura (GET)
# ---------------------------------------------------------------------------

class SiembraReadSerializer(serializers.ModelSerializer):
    """
    Serializer enriquecido para consultas GET.

    Incluye campos legibles (display) para metodo, lote y ciclo,
    facilitando la visualización en el frontend sin necesidad de
    lookups adicionales.
    """

    # Campos de solo lectura que exponen el label legible del choice
    metodo_display = serializers.CharField(
        source="get_metodo_display",
        read_only=True,
    )

    # Información desnormalizada del Lote
    lote_nombre = serializers.CharField(
        source="lote.nombre",
        read_only=True,
    )

    # Información desnormalizada del Ciclo
    ciclo_nombre = serializers.CharField(
        source="ciclo.nombre",
        read_only=True,
    )

    class Meta:
        model = Siembra
        fields = [
            "id",
            "fecha_siembra",
            "variedad",
            "densidad",
            "metodo",
            "metodo_display",
            "lote",
            "lote_nombre",
            "ciclo",
            "ciclo_nombre",
            "created_at",
        ]
        read_only_fields = fields   # En GET todos los campos son de solo lectura

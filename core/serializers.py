from rest_framework import serializers
from .models import Finca, Lote, LaborTerreno, Siembra, ActividadAgronomica


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
    
class SiembraSerializer(serializers.ModelSerializer):
    lote_nombre = serializers.CharField(source="lote.nombre", read_only=True)
    finca_id = serializers.IntegerField(source="lote.finca.id", read_only=True)
    finca_nombre = serializers.CharField(source="lote.finca.nombre", read_only=True)

    class Meta:
        model = Siembra
        fields = [
            "id",
            "lote",
            "lote_nombre",
            "finca_id",
            "finca_nombre",
            "fecha_siembra",
            "variedad",
            "densidad_siembra",
            "metodo_siembra",
            "observaciones",
        ]

    def validate_densidad_siembra(self, value):
        if value <= 0:
            raise serializers.ValidationError("La densidad de siembra debe ser mayor a cero.")
        return value
    
class ActividadAgronomicaSerializer(serializers.ModelSerializer):
    lote_nombre = serializers.CharField(source='lote.nombre', read_only=True)
    finca_nombre = serializers.CharField(source='lote.finca.nombre', read_only=True)
    etapa_fenologica_display = serializers.CharField(
        source='get_etapa_fenologica_display', read_only=True
    )

    class Meta:
        model = ActividadAgronomica
        fields = [
            'id',
            'lote', 'lote_nombre', 'finca_nombre', 'siembra',
            'fertilizante', 'cantidad_fertilizante', 'fecha_fertilizacion',
            'control_malezas', 'metodo_malezas', 'producto_malezas',
            'fecha_control_malezas',
            'producto_fitosanitario', 'dosis_fitosanitario',
            'fecha_aplicacion_fitosanitaria',
            'etapa_fenologica', 'etapa_fenologica_display',
            'observaciones',
        ]

    def validate_cantidad_fertilizante(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'La cantidad de fertilizante debe ser mayor a cero.'
            )
        return value

    def validate(self, data):
        # RF-21: si control_malezas=True → metodo y fecha son requeridos
        control_malezas = data.get(
            'control_malezas',
            getattr(self.instance, 'control_malezas', False),
        )
        metodo_malezas = data.get(
            'metodo_malezas',
            getattr(self.instance, 'metodo_malezas', ''),
        )
        fecha_control_malezas = data.get(
            'fecha_control_malezas',
            getattr(self.instance, 'fecha_control_malezas', None),
        )
        if control_malezas and not metodo_malezas:
            raise serializers.ValidationError({
                'metodo_malezas': (
                    'Debe indicar el método de control cuando '
                    'control_malezas es verdadero.'
                )
            })
        if control_malezas and not fecha_control_malezas:
            raise serializers.ValidationError({
                'fecha_control_malezas': (
                    'Debe indicar la fecha del control de malezas.'
                )
            })

        # RF-22: si se indica producto fitosanitario → dosis y fecha obligatorios
        producto_fito = data.get(
            'producto_fitosanitario',
            getattr(self.instance, 'producto_fitosanitario', ''),
        )
        dosis_fito = data.get(
            'dosis_fitosanitario',
            getattr(self.instance, 'dosis_fitosanitario', ''),
        )
        fecha_fito = data.get(
            'fecha_aplicacion_fitosanitaria',
            getattr(self.instance, 'fecha_aplicacion_fitosanitaria', None),
        )
        if producto_fito:
            if not dosis_fito:
                raise serializers.ValidationError({
                    'dosis_fitosanitario': (
                        'La dosis es obligatoria cuando se registra un '
                        'producto fitosanitario.'
                    )
                })
            if not fecha_fito:
                raise serializers.ValidationError({
                    'fecha_aplicacion_fitosanitaria': (
                        'La fecha de aplicación es obligatoria cuando se '
                        'registra un producto fitosanitario.'
                    )
                })

        return data


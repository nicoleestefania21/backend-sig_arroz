from rest_framework import serializers
from django.utils import timezone
from .models import CicloProductivo, PlanificacionCiclo, HistorialCiclo


class PlanificacionCicloSerializer(serializers.ModelSerializer):
    """
    RF-07: Cronograma de actividades agrícolas por ciclo.
    RF-08: Fechas clave del ciclo (preparación, siembra, cosecha).
    """

    class Meta:
        model = PlanificacionCiclo
        fields = '__all__'

    def validate(self, data):
        # RF-07: coherencia cronológica de fechas estimadas
        # Preparación < Siembra < Manejo < Cosecha
        fp = data.get('fecha_preparacion_estimada')
        fs = data.get('fecha_siembra_estimada')
        fm = data.get('fecha_manejo_estimada')
        fc = data.get('fecha_cosecha_estimada')

        if fp and fs and fs < fp:
            raise serializers.ValidationError(
                "La fecha de siembra estimada debe ser posterior a la de preparación."
            )
        if fs and fm and fm < fs:
            raise serializers.ValidationError(
                "La fecha de manejo estimada debe ser posterior a la de siembra."
            )
        if fm and fc and fc < fm:
            raise serializers.ValidationError(
                "La fecha de cosecha estimada debe ser posterior a la de manejo."
            )

        # RF-08: coherencia de fechas reales
        fp_real = data.get('fecha_preparacion_real')
        fs_real = data.get('fecha_siembra_real')
        fc_real = data.get('fecha_cosecha_real')

        if fp_real and fs_real and fs_real < fp_real:
            raise serializers.ValidationError(
                "La fecha real de siembra debe ser posterior a la real de preparación."
            )
        if fs_real and fc_real and fc_real < fs_real:
            raise serializers.ValidationError(
                "La fecha real de cosecha no puede ser anterior a la de siembra."
            )

        # RF-08: fechas reales solo si el ciclo está Activo
        ciclo = data.get('ciclo') or (self.instance.ciclo if self.instance else None)
        tiene_fecha_real = fp_real or fs_real or fc_real
        if tiene_fecha_real and ciclo and ciclo.estado != CicloProductivo.ACTIVO:
            raise serializers.ValidationError(
                "Solo se pueden registrar fechas reales cuando el ciclo está Activo."
            )

        # RF-07: ninguna fecha puede ser anterior a la fecha de inicio del ciclo
        if ciclo:
            fecha_inicio = ciclo.fecha_inicio_estimada
            for nombre_campo, valor in [
                ('fecha_preparacion_estimada', fp),
                ('fecha_siembra_estimada', fs),
                ('fecha_manejo_estimada', fm),
                ('fecha_cosecha_estimada', fc),
            ]:
                if valor and valor < fecha_inicio:
                    raise serializers.ValidationError(
                        f"La {nombre_campo} no puede ser anterior a la fecha de inicio del ciclo."
                    )

        return data


class CicloProductivoSerializer(serializers.ModelSerializer):
    """
    RF-06: Crear ciclos productivos asociados a un lote.
    RF-09: Asociar lotes a ciclos productivos.
    """
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    planificacion = PlanificacionCicloSerializer(read_only=True)

    class Meta:
        model = CicloProductivo
        fields = '__all__'

    def validate_fecha_inicio_estimada(self, value):
        # RF-06: la fecha de inicio no puede ser anterior a la fecha actual
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de inicio no puede ser anterior a la fecha actual."
            )
        return value

    def validate_lote(self, value):
        # RN-03: un lote solo puede tener un ciclo activo o planificado a la vez
        qs = CicloProductivo.objects.filter(
            lote=value,
            estado__in=[CicloProductivo.PLANIFICADO, CicloProductivo.ACTIVO]
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "El lote ya tiene un ciclo productivo activo o planificado."
            )
        return value


class CicloProductivoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación con planificación anidada opcional.
    RF-06 + RF-07 en una sola operación.
    """
    planificacion = PlanificacionCicloSerializer(required=False)

    class Meta:
        model = CicloProductivo
        fields = '__all__'

    def validate_fecha_inicio_estimada(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de inicio no puede ser anterior a la fecha actual."
            )
        return value

    def validate_lote(self, value):
        qs = CicloProductivo.objects.filter(
            lote=value,
            estado__in=[CicloProductivo.PLANIFICADO, CicloProductivo.ACTIVO]
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "El lote ya tiene un ciclo productivo activo o planificado."
            )
        return value

    def create(self, validated_data):
        planificacion_data = validated_data.pop('planificacion', None)
        ciclo = CicloProductivo.objects.create(**validated_data)

        if planificacion_data:
            PlanificacionCiclo.objects.create(ciclo=ciclo, **planificacion_data)

        # RF-10: registrar en historial la creación
        HistorialCiclo.objects.create(
            ciclo=ciclo,
            estado_anterior='',
            estado_nuevo=ciclo.estado,
            observacion='Ciclo creado.'
        )
        return ciclo


class HistorialCicloSerializer(serializers.ModelSerializer):
    """
    RF-10: Consultar historial de ciclos productivos por lote.
    """

    class Meta:
        model = HistorialCiclo
        fields = '__all__'


class CicloProductivoDetalleSerializer(serializers.ModelSerializer):
    """
    RF-10: Vista detallada del ciclo con planificación e historial.
    """
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    planificacion = PlanificacionCicloSerializer(read_only=True)
    historial = HistorialCicloSerializer(many=True, read_only=True)
    lote_nombre = serializers.CharField(source='lote.nombre', read_only=True)

    class Meta:
        model = CicloProductivo
        fields = '__all__'
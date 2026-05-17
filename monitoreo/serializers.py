from rest_framework import serializers
from .models import (
    MonitoreoCultivo,
    MonitoreoBiologico,
    MonitoreoFitosanitario,
    RegistroPlaga,
    RegistroEnfermedad,
    EstadoGeneralCultivo,
)
from ciclos.models import CicloProductivo


# ---------- Plagas y Enfermedades ----------

class RegistroPlagaSerializer(serializers.ModelSerializer):
    nivel_infestacion_display = serializers.CharField(
        source='get_nivel_infestacion_display', read_only=True
    )

    class Meta:
        model = RegistroPlaga
        fields = [
            'id',
            'monitoreo_fitosanitario',
            'nombre_plaga',
            'nivel_infestacion',
            'nivel_infestacion_display',
            'porcentaje_afectacion',
            'accion_tomada',
            'observaciones',
        ]

    def validate_porcentaje_afectacion(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "El porcentaje de afectación debe estar entre 0 y 100."
            )
        return value


class RegistroEnfermedadSerializer(serializers.ModelSerializer):
    severidad_display = serializers.CharField(
        source='get_severidad_display', read_only=True
    )

    class Meta:
        model = RegistroEnfermedad
        fields = [
            'id',
            'monitoreo_fitosanitario',
            'nombre_enfermedad',
            'severidad',
            'severidad_display',
            'porcentaje_afectacion',
            'accion_tomada',
            'observaciones',
        ]

    def validate_porcentaje_afectacion(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "El porcentaje de afectación debe estar entre 0 y 100."
            )
        return value


# ---------- Subcomponentes de monitoreo ----------

class MonitoreoBiologicoSerializer(serializers.ModelSerializer):
    """
    RF-30: Monitoreo biológico (germinación, macollamiento).
    """
    etapa_fenologica_display = serializers.CharField(
        source='get_etapa_fenologica_display', read_only=True
    )

    class Meta:
        model = MonitoreoBiologico
        fields = [
            'id',
            'monitoreo',
            'porcentaje_germinacion',
            'dias_desde_siembra',
            'num_macollas_promedio',
            'plantas_por_metro_cuadrado',
            'etapa_fenologica',
            'etapa_fenologica_display',
            'altura_promedio_cm',
            'observaciones',
        ]

    def validate_porcentaje_germinacion(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "El porcentaje de germinación debe estar entre 0 y 100."
            )
        return value

    def validate_dias_desde_siembra(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Los días desde la siembra no pueden ser negativos."
            )
        return value

    def validate_num_macollas_promedio(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "El número de macollas promedio no puede ser negativo."
            )
        return value

    def validate_altura_promedio_cm(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "La altura promedio no puede ser negativa."
            )
        return value


class MonitoreoFitosanitarioSerializer(serializers.ModelSerializer):
    """
    RF-31: Monitoreo fitosanitario (plagas y enfermedades).
    """
    plagas = RegistroPlagaSerializer(many=True, read_only=True)
    enfermedades = RegistroEnfermedadSerializer(many=True, read_only=True)

    class Meta:
        model = MonitoreoFitosanitario
        fields = [
            'id',
            'monitoreo',
            'presencia_plagas',
            'presencia_enfermedades',
            'plagas',
            'enfermedades',
            'observaciones',
        ]


class MonitoreoFitosanitarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer de creación con plagas y enfermedades anidadas.
    RF-31: permite registrar plagas y enfermedades en una sola operación.
    """
    plagas = RegistroPlagaSerializer(many=True, required=False)
    enfermedades = RegistroEnfermedadSerializer(many=True, required=False)

    class Meta:
        model = MonitoreoFitosanitario
        fields = [
            'id',
            'monitoreo',
            'presencia_plagas',
            'presencia_enfermedades',
            'plagas',
            'enfermedades',
            'observaciones',
        ]

    def validate(self, data):
        plagas = data.get('plagas', [])
        enfermedades = data.get('enfermedades', [])

        if data.get('presencia_plagas') and not plagas:
            raise serializers.ValidationError(
                "Si se indica presencia de plagas, debe registrar al menos una plaga."
            )
        if data.get('presencia_enfermedades') and not enfermedades:
            raise serializers.ValidationError(
                "Si se indica presencia de enfermedades, debe registrar al menos una enfermedad."
            )
        return data

    def create(self, validated_data):
        plagas_data = validated_data.pop('plagas', [])
        enfermedades_data = validated_data.pop('enfermedades', [])

        fitosanitario = MonitoreoFitosanitario.objects.create(**validated_data)

        for plaga_data in plagas_data:
            RegistroPlaga.objects.create(
                monitoreo_fitosanitario=fitosanitario,
                **plaga_data
            )
        for enfermedad_data in enfermedades_data:
            RegistroEnfermedad.objects.create(
                monitoreo_fitosanitario=fitosanitario,
                **enfermedad_data
            )
        return fitosanitario

    def update(self, instance, validated_data):
        plagas_data = validated_data.pop('plagas', None)
        enfermedades_data = validated_data.pop('enfermedades', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if plagas_data is not None:
            instance.plagas.all().delete()
            for plaga_data in plagas_data:
                RegistroPlaga.objects.create(
                    monitoreo_fitosanitario=instance,
                    **plaga_data
                )
        if enfermedades_data is not None:
            instance.enfermedades.all().delete()
            for enfermedad_data in enfermedades_data:
                RegistroEnfermedad.objects.create(
                    monitoreo_fitosanitario=instance,
                    **enfermedad_data
                )
        return instance


class EstadoGeneralCultivoSerializer(serializers.ModelSerializer):
    """
    RF-32: Estado general del cultivo.
    """
    estado_general_display = serializers.CharField(
        source='get_estado_general_display', read_only=True
    )
    color_follaje_display = serializers.CharField(
        source='get_color_follaje_display', read_only=True
    )
    densidad_plantas_display = serializers.CharField(
        source='get_densidad_plantas_display', read_only=True
    )

    class Meta:
        model = EstadoGeneralCultivo
        fields = [
            'id',
            'monitoreo',
            'estado_general',
            'estado_general_display',
            'color_follaje',
            'color_follaje_display',
            'densidad_plantas',
            'densidad_plantas_display',
            'uniformidad_cultivo',
            'presencia_malezas',
            'nivel_estres_hidrico',
            'observaciones',
        ]


# ---------- Monitoreo principal ----------

class MonitoreoCultivoSerializer(serializers.ModelSerializer):
    """
    HU-011: Vista de detalle del monitoreo con todos sus subcomponentes.
    """
    ciclo_nombre = serializers.CharField(source='ciclo.nombre', read_only=True)
    lote_nombre = serializers.CharField(source='ciclo.lote.nombre', read_only=True)
    finca_nombre = serializers.CharField(source='ciclo.lote.finca.nombre', read_only=True)
    biologico = MonitoreoBiologicoSerializer(read_only=True)
    fitosanitario = MonitoreoFitosanitarioSerializer(read_only=True)
    estado_general = EstadoGeneralCultivoSerializer(read_only=True)

    class Meta:
        model = MonitoreoCultivo
        fields = [
            'id',
            'ciclo',
            'ciclo_nombre',
            'lote_nombre',
            'finca_nombre',
            'fecha_monitoreo',
            'observaciones_generales',
            'biologico',
            'fitosanitario',
            'estado_general',
            'created_at',
            'updated_at',
        ]


class MonitoreoCultivoCreateSerializer(serializers.ModelSerializer):
    """
    HU-011: Creación completa del monitoreo con subcomponentes anidados.
    RF-30 + RF-31 + RF-32 en una sola operación.
    """
    biologico = MonitoreoBiologicoSerializer(required=False)
    fitosanitario = MonitoreoFitosanitarioCreateSerializer(required=False)
    estado_general = EstadoGeneralCultivoSerializer(required=False)

    class Meta:
        model = MonitoreoCultivo
        fields = [
            'id',
            'ciclo',
            'fecha_monitoreo',
            'observaciones_generales',
            'biologico',
            'fitosanitario',
            'estado_general',
        ]

    def validate_ciclo(self, value):
        if value.estado == CicloProductivo.CERRADO:
            raise serializers.ValidationError(
                "No se puede registrar monitoreo en un ciclo cerrado."
            )
        return value

    def create(self, validated_data):
        biologico_data = validated_data.pop('biologico', None)
        fitosanitario_data = validated_data.pop('fitosanitario', None)
        estado_general_data = validated_data.pop('estado_general', None)

        monitoreo = MonitoreoCultivo.objects.create(**validated_data)

        if biologico_data:
            MonitoreoBiologico.objects.create(monitoreo=monitoreo, **biologico_data)

        if fitosanitario_data:
            plagas_data = fitosanitario_data.pop('plagas', [])
            enfermedades_data = fitosanitario_data.pop('enfermedades', [])
            fitosanitario = MonitoreoFitosanitario.objects.create(
                monitoreo=monitoreo, **fitosanitario_data
            )
            for plaga in plagas_data:
                RegistroPlaga.objects.create(
                    monitoreo_fitosanitario=fitosanitario, **plaga
                )
            for enfermedad in enfermedades_data:
                RegistroEnfermedad.objects.create(
                    monitoreo_fitosanitario=fitosanitario, **enfermedad
                )

        if estado_general_data:
            EstadoGeneralCultivo.objects.create(
                monitoreo=monitoreo, **estado_general_data
            )

        return monitoreo

    def update(self, instance, validated_data):
        biologico_data = validated_data.pop('biologico', None)
        fitosanitario_data = validated_data.pop('fitosanitario', None)
        estado_general_data = validated_data.pop('estado_general', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if biologico_data is not None:
            MonitoreoBiologico.objects.update_or_create(
                monitoreo=instance,
                defaults=biologico_data
            )

        if fitosanitario_data is not None:
            plagas_data = fitosanitario_data.pop('plagas', None)
            enfermedades_data = fitosanitario_data.pop('enfermedades', None)
            fito, _ = MonitoreoFitosanitario.objects.update_or_create(
                monitoreo=instance,
                defaults=fitosanitario_data
            )
            if plagas_data is not None:
                fito.plagas.all().delete()
                for plaga in plagas_data:
                    RegistroPlaga.objects.create(
                        monitoreo_fitosanitario=fito, **plaga
                    )
            if enfermedades_data is not None:
                fito.enfermedades.all().delete()
                for enfermedad in enfermedades_data:
                    RegistroEnfermedad.objects.create(
                        monitoreo_fitosanitario=fito, **enfermedad
                    )

        if estado_general_data is not None:
            EstadoGeneralCultivo.objects.update_or_create(
                monitoreo=instance,
                defaults=estado_general_data
            )

        return instance


class MonitoreoCultivoListSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listados de monitoreo.
    """
    ciclo_nombre = serializers.CharField(source='ciclo.nombre', read_only=True)
    lote_nombre = serializers.CharField(source='ciclo.lote.nombre', read_only=True)
    tiene_biologico = serializers.SerializerMethodField()
    tiene_fitosanitario = serializers.SerializerMethodField()
    tiene_estado_general = serializers.SerializerMethodField()

    class Meta:
        model = MonitoreoCultivo
        fields = [
            'id',
            'ciclo',
            'ciclo_nombre',
            'lote_nombre',
            'fecha_monitoreo',
            'tiene_biologico',
            'tiene_fitosanitario',
            'tiene_estado_general',
            'observaciones_generales',
            'created_at',
        ]

    def get_tiene_biologico(self, obj):
        return hasattr(obj, 'biologico') and obj.biologico is not None

    def get_tiene_fitosanitario(self, obj):
        return hasattr(obj, 'fitosanitario') and obj.fitosanitario is not None

    def get_tiene_estado_general(self, obj):
        return hasattr(obj, 'estado_general') and obj.estado_general is not None

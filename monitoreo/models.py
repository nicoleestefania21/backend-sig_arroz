from django.db import models
from ciclos.models import CicloProductivo


class MonitoreoCultivo(models.Model):
   
    ciclo = models.ForeignKey(
        CicloProductivo,
        on_delete=models.CASCADE,
        related_name='monitoreos'
    )
    fecha_monitoreo = models.DateField()
    observaciones_generales = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_monitoreo', '-id']

    def __str__(self):
        return f"Monitoreo {self.fecha_monitoreo} - {self.ciclo.nombre}"


class MonitoreoBiologico(models.Model):
    """
    RF-30: Monitoreo biológico (germinación, macollamiento).
    """
    ETAPA_GERMINACION = 'GERMINACION'
    ETAPA_PLANTULA = 'PLANTULA'
    ETAPA_MACOLLAMIENTO = 'MACOLLAMIENTO'
    ETAPA_ELONGACION = 'ELONGACION'
    ETAPA_PANICULACION = 'PANICULACION'
    ETAPA_FLORACION = 'FLORACION'
    ETAPA_MADUREZ = 'MADUREZ'

    ETAPA_CHOICES = [
        (ETAPA_GERMINACION, 'Germinación'),
        (ETAPA_PLANTULA, 'Plántula'),
        (ETAPA_MACOLLAMIENTO, 'Macollamiento'),
        (ETAPA_ELONGACION, 'Elongación del tallo'),
        (ETAPA_PANICULACION, 'Paniculación'),
        (ETAPA_FLORACION, 'Floración'),
        (ETAPA_MADUREZ, 'Madurez'),
    ]

    monitoreo = models.OneToOneField(
        MonitoreoCultivo,
        on_delete=models.CASCADE,
        related_name='biologico'
    )

    # Germinación
    porcentaje_germinacion = models.FloatField(
        null=True,
        blank=True,
        help_text="Porcentaje de germinación observado (0-100)"
    )
    dias_desde_siembra = models.IntegerField(
        null=True,
        blank=True,
        help_text="Días transcurridos desde la siembra"
    )

    # Macollamiento
    num_macollas_promedio = models.FloatField(
        null=True,
        blank=True,
        help_text="Número promedio de macollas por planta"
    )
    plantas_por_metro_cuadrado = models.FloatField(
        null=True,
        blank=True,
        help_text="Densidad de plantas por m²"
    )

    # Etapa fenológica general
    etapa_fenologica = models.CharField(
        max_length=20,
        choices=ETAPA_CHOICES,
        help_text="Etapa fenológica actual del cultivo"
    )
    altura_promedio_cm = models.FloatField(
        null=True,
        blank=True,
        help_text="Altura promedio de las plantas en cm"
    )

    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Monitoreo biológico - {self.monitoreo}"


class MonitoreoFitosanitario(models.Model):
    """
    RF-31: Monitoreo fitosanitario (plagas y enfermedades).
    """
    monitoreo = models.OneToOneField(
        MonitoreoCultivo,
        on_delete=models.CASCADE,
        related_name='fitosanitario'
    )
    presencia_plagas = models.BooleanField(
        default=False,
        help_text="Indica si se detectó presencia de plagas"
    )
    presencia_enfermedades = models.BooleanField(
        default=False,
        help_text="Indica si se detectó presencia de enfermedades"
    )
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Monitoreo fitosanitario - {self.monitoreo}"


class RegistroPlaga(models.Model):
    """
    RF-31: Registro detallado de cada plaga detectada en el monitoreo fitosanitario.
    """
    NIVEL_BAJO = 'BAJO'
    NIVEL_MEDIO = 'MEDIO'
    NIVEL_ALTO = 'ALTO'
    NIVEL_CRITICO = 'CRITICO'

    NIVEL_CHOICES = [
        (NIVEL_BAJO, 'Bajo'),
        (NIVEL_MEDIO, 'Medio'),
        (NIVEL_ALTO, 'Alto'),
        (NIVEL_CRITICO, 'Crítico'),
    ]

    monitoreo_fitosanitario = models.ForeignKey(
        MonitoreoFitosanitario,
        on_delete=models.CASCADE,
        related_name='plagas'
    )
    nombre_plaga = models.CharField(max_length=150)
    nivel_infestacion = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES
    )
    porcentaje_afectacion = models.FloatField(
        null=True,
        blank=True,
        help_text="Porcentaje del cultivo afectado (0-100)"
    )
    accion_tomada = models.TextField(
        blank=True,
        help_text="Medida de control aplicada o recomendada"
    )
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre_plaga} ({self.get_nivel_infestacion_display()}) - {self.monitoreo_fitosanitario}"


class RegistroEnfermedad(models.Model):
    """
    RF-31: Registro detallado de cada enfermedad detectada en el monitoreo fitosanitario.
    """
    SEVERIDAD_LEVE = 'LEVE'
    SEVERIDAD_MODERADA = 'MODERADA'
    SEVERIDAD_SEVERA = 'SEVERA'

    SEVERIDAD_CHOICES = [
        (SEVERIDAD_LEVE, 'Leve'),
        (SEVERIDAD_MODERADA, 'Moderada'),
        (SEVERIDAD_SEVERA, 'Severa'),
    ]

    monitoreo_fitosanitario = models.ForeignKey(
        MonitoreoFitosanitario,
        on_delete=models.CASCADE,
        related_name='enfermedades'
    )
    nombre_enfermedad = models.CharField(max_length=150)
    severidad = models.CharField(
        max_length=10,
        choices=SEVERIDAD_CHOICES
    )
    porcentaje_afectacion = models.FloatField(
        null=True,
        blank=True,
        help_text="Porcentaje del cultivo afectado (0-100)"
    )
    accion_tomada = models.TextField(
        blank=True,
        help_text="Medida de control aplicada o recomendada"
    )
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre_enfermedad} ({self.get_severidad_display()}) - {self.monitoreo_fitosanitario}"


class EstadoGeneralCultivo(models.Model):
    """
    RF-32: Estado general del cultivo.
    """
    COLOR_VERDE_OSCURO = 'VERDE_OSCURO'
    COLOR_VERDE_NORMAL = 'VERDE_NORMAL'
    COLOR_AMARILLENTO = 'AMARILLENTO'
    COLOR_CLOROTICO = 'CLOROTICO'

    COLOR_CHOICES = [
        (COLOR_VERDE_OSCURO, 'Verde oscuro'),
        (COLOR_VERDE_NORMAL, 'Verde normal'),
        (COLOR_AMARILLENTO, 'Amarillento'),
        (COLOR_CLOROTICO, 'Clorótico'),
    ]

    DENSIDAD_BAJA = 'BAJA'
    DENSIDAD_NORMAL = 'NORMAL'
    DENSIDAD_ALTA = 'ALTA'

    DENSIDAD_CHOICES = [
        (DENSIDAD_BAJA, 'Baja'),
        (DENSIDAD_NORMAL, 'Normal'),
        (DENSIDAD_ALTA, 'Alta'),
    ]

    ESTADO_EXCELENTE = 'EXCELENTE'
    ESTADO_BUENO = 'BUENO'
    ESTADO_REGULAR = 'REGULAR'
    ESTADO_MALO = 'MALO'

    ESTADO_CHOICES = [
        (ESTADO_EXCELENTE, 'Excelente'),
        (ESTADO_BUENO, 'Bueno'),
        (ESTADO_REGULAR, 'Regular'),
        (ESTADO_MALO, 'Malo'),
    ]

    monitoreo = models.OneToOneField(
        MonitoreoCultivo,
        on_delete=models.CASCADE,
        related_name='estado_general'
    )
    estado_general = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        help_text="Evaluación general del estado del cultivo"
    )
    color_follaje = models.CharField(
        max_length=15,
        choices=COLOR_CHOICES,
        help_text="Color predominante del follaje"
    )
    densidad_plantas = models.CharField(
        max_length=10,
        choices=DENSIDAD_CHOICES,
        help_text="Densidad de plantas en el lote"
    )
    uniformidad_cultivo = models.BooleanField(
        default=True,
        help_text="Indica si el cultivo presenta uniformidad en el lote"
    )
    presencia_malezas = models.BooleanField(
        default=False,
        help_text="Indica si hay presencia significativa de malezas"
    )
    nivel_estres_hidrico = models.BooleanField(
        default=False,
        help_text="Indica si el cultivo presenta síntomas de estrés hídrico"
    )
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Estado general ({self.get_estado_general_display()}) - {self.monitoreo}"

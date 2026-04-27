from django.db import models
from core.models import Lote


class CicloProductivo(models.Model):
    """
    RF-06: Crear ciclos productivos de arroz asociados a un lote.
    RF-09: Asociar lotes a ciclos productivos.
    """
    PLANIFICADO = 'PLANIFICADO'
    ACTIVO = 'ACTIVO'
    CERRADO = 'CERRADO'

    ESTADO_CHOICES = [
        (PLANIFICADO, 'Planificado'),
        (ACTIVO, 'Activo'),
        (CERRADO, 'Cerrado'),
    ]

    VARIEDAD_CHOICES = [
        ('IR42', 'IR42'),
        ('FEDEARROZ_50', 'Fedearroz 50'),
        ('FEDEARROZ_67', 'Fedearroz 67'),
        ('FEDEARROZ_174', 'Fedearroz 174'),
        ('OTRA', 'Otra'),
    ]

    # RF-09: asociación con lote
    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name='ciclos'
    )
    nombre = models.CharField(max_length=100)
    variedad_planificada = models.CharField(
        max_length=20,
        choices=VARIEDAD_CHOICES,
        blank=True
    )
    fecha_inicio_estimada = models.DateField()
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default=PLANIFICADO,
    )
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # RN-03: un lote solo puede tener un ciclo activo o planificado a la vez
        constraints = [
            models.UniqueConstraint(
                fields=['lote'],
                condition=models.Q(estado__in=['PLANIFICADO', 'ACTIVO']),
                name='unique_ciclo_activo_por_lote'
            )
        ]

    def __str__(self):
        return f"{self.nombre} - Lote: {self.lote.nombre} ({self.estado})"


class PlanificacionCiclo(models.Model):
    """
    RF-07: Definir cronograma de actividades agrícolas por ciclo.
    RF-08: Registrar fechas clave del ciclo (preparación, siembra, cosecha).
    """
    ciclo = models.OneToOneField(
        CicloProductivo,
        on_delete=models.CASCADE,
        related_name='planificacion'
    )
    # RF-07: cronograma de etapas estimadas
    fecha_preparacion_estimada = models.DateField()
    fecha_siembra_estimada = models.DateField()
    fecha_manejo_estimada = models.DateField()
    fecha_cosecha_estimada = models.DateField()

    # RF-08: fechas reales registradas a medida que se ejecutan
    fecha_preparacion_real = models.DateField(null=True, blank=True)
    fecha_siembra_real = models.DateField(null=True, blank=True)
    fecha_cosecha_real = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Planificación - {self.ciclo.nombre}"


class HistorialCiclo(models.Model):
    """
    RF-10: Consultar historial de ciclos productivos por lote.
    Registra cada cambio de estado del ciclo para trazabilidad.
    """
    ciclo = models.ForeignKey(
        CicloProductivo,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    estado_anterior = models.CharField(max_length=15, blank=True)
    estado_nuevo = models.CharField(max_length=15)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"{self.ciclo.nombre}: {self.estado_anterior} → {self.estado_nuevo}"
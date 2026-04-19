from django.db import models

class Finca(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    vereda = models.CharField(max_length=100)
    area_total = models.FloatField()
    tipo_suelo = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Lote(models.Model):
    DISPONIBLE = 'DISPONIBLE'
    EN_USO = 'EN_USO'
    EN_PREPARACION = 'EN_PREPARACION'
    INACTIVO = 'INACTIVO'

    ESTADO_CHOICES = [
        (DISPONIBLE, 'Disponible'),
        (EN_USO, 'En uso'),
        (EN_PREPARACION, 'En preparación'),
        (INACTIVO, 'Inactivo'),
    ]

    finca = models.ForeignKey(Finca, on_delete=models.CASCADE, related_name='lotes')
    nombre = models.CharField(max_length=100)
    area = models.FloatField()
    tipo_suelo = models.CharField(max_length=50)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=DISPONIBLE,
    )

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"

    @property
    def disponible(self):
        return self.estado == self.DISPONIBLE
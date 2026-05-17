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
    
class LaborTerreno(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='labores')
    tipo_labor = models.CharField(max_length=100)
    fecha = models.DateField()

    ph = models.FloatField(null=True, blank=True)
    humedad = models.FloatField(null=True, blank=True)

    nivelacion = models.BooleanField(default=False)
    drenaje = models.BooleanField(default=False)
    adecuacion = models.BooleanField(default=False)

    estado_terreno = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo_labor} - {self.lote.nombre}"
    
class Siembra(models.Model):
    METODO_DIRECTA = "DIRECTA"
    METODO_TRASPLANTE = "TRASPLANTE"
    METODO_VOLEO = "VOLEO"

    METODO_CHOICES = [
        (METODO_DIRECTA, "Siembra directa"),
        (METODO_TRASPLANTE, "Trasplante"),
        (METODO_VOLEO, "Voleo"),
    ]

    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="siembras")
    fecha_siembra = models.DateField()
    variedad = models.CharField(max_length=100)
    densidad_siembra = models.FloatField(help_text="kg/ha o similar")
    metodo_siembra = models.CharField(max_length=20, choices=METODO_CHOICES)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Siembra {self.variedad} - {self.lote.nombre} ({self.fecha_siembra})"
    
class ActividadAgronomica(models.Model):
    # RF-23 — Etapas fenológicas estándar del cultivo de arroz
    GERMINACION = 'GERMINACION'
    PLÁNTULA = 'PLANTULA'
    MACOLLAMIENTO = 'MACOLLAMIENTO'
    ELONGACION = 'ELONGACION'
    PRIMORDIO = 'PRIMORDIO'
    FLORACION = 'FLORACION'
    GRANO_LECHOSO = 'GRANO_LECHOSO'
    GRANO_PASTOSO = 'GRANO_PASTOSO'
    MADUREZ = 'MADUREZ'
    COSECHA = 'COSECHA'

    ETAPA_CHOICES = [
        (GERMINACION, 'Germinación'),
        (PLÁNTULA, 'Plántula'),
        (MACOLLAMIENTO, 'Macollamiento'),
        (ELONGACION, 'Elongación del tallo'),
        (PRIMORDIO, 'Primordio floral'),
        (FLORACION, 'Floración / Antesis'),
        (GRANO_LECHOSO, 'Grano lechoso'),
        (GRANO_PASTOSO, 'Grano pastoso'),
        (MADUREZ, 'Madurez fisiológica'),
        (COSECHA, 'Cosecha'),
    ]

    # Vínculo principal
    lote = models.ForeignKey(
        Lote, on_delete=models.CASCADE, related_name='actividades'
    )
    # Opcional: asociar a una siembra concreta para trazabilidad por ciclo
    siembra = models.ForeignKey(
        'Siembra',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='actividades',
    )

    # RF-20 — Fertilización
    fertilizante = models.CharField(max_length=100)
    cantidad_fertilizante = models.FloatField()
    fecha_fertilizacion = models.DateField()

    # RF-21 — Control de malezas
    control_malezas = models.BooleanField(default=False)
    metodo_malezas = models.CharField(max_length=100, blank=True)
    producto_malezas = models.CharField(
        max_length=100, blank=True,
        help_text='Herbicida o producto utilizado (si aplica)'
    )
    fecha_control_malezas = models.DateField(
        null=True, blank=True,
        help_text='Fecha en que se realizó el control de malezas'
    )

    # RF-22 — Aplicaciones fitosanitarias
    producto_fitosanitario = models.CharField(max_length=100, blank=True)
    dosis_fitosanitario = models.CharField(max_length=50, blank=True)
    fecha_aplicacion_fitosanitaria = models.DateField(null=True, blank=True)

    # RF-23 — Crecimiento / etapa fenológica
    etapa_fenologica = models.CharField(
        max_length=20,
        choices=ETAPA_CHOICES,
    )

    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.lote.nombre} — {self.get_etapa_fenologica_display()}"

"""
models.py — App: siembra
Modelos del dominio de Siembra del Cultivo para SIG-Arroz.

Contiene:
  · CicloProductivo — ciclo de producción al que pertenece una siembra
  · Siembra         — registro de la siembra de un lote en un ciclo
"""

from django.db import models
from core.models import Lote          # Relación con el lote físico


# ---------------------------------------------------------------------------
# Ciclo Productivo
# ---------------------------------------------------------------------------

class CicloProductivo(models.Model):
    """
    Representa un ciclo de producción arrocera (p.ej. "Ciclo 2024-A").

    Un ciclo agrupa todas las actividades agrícolas —siembras, riegos,
    cosechas— que ocurren dentro de un periodo de tiempo determinado.
    """

    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre descriptivo del ciclo (ej. 'Ciclo 2024-A').",
    )
    fecha_inicio = models.DateField(
        help_text="Fecha en que inicia formalmente el ciclo productivo.",
    )
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha estimada o real de cierre del ciclo. Puede quedar vacía.",
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el ciclo está actualmente en curso.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ciclo Productivo"
        verbose_name_plural = "Ciclos Productivos"
        ordering = ["-fecha_inicio"]

    def __str__(self) -> str:
        estado = "activo" if self.activo else "cerrado"
        return f"{self.nombre} ({estado})"


# ---------------------------------------------------------------------------
# Siembra
# ---------------------------------------------------------------------------

class Siembra(models.Model):
    """
    Registro de la siembra realizada sobre un lote dentro de un ciclo.

    HU: Como Técnico u Operador, quiero registrar la siembra de un lote
    indicando la variedad, método y densidad utilizada, para llevar
    trazabilidad del cultivo dentro del ciclo productivo.
    """

    # ------------------------------------------------------------------
    # Choices para el campo `metodo`
    # ------------------------------------------------------------------
    DIRECTA = "directa"
    TRASPLANTE = "trasplante"

    METODO_CHOICES = [
        (DIRECTA, "Siembra directa"),
        (TRASPLANTE, "Trasplante"),
    ]

    # ------------------------------------------------------------------
    # Campos del modelo
    # ------------------------------------------------------------------

    fecha_siembra = models.DateField(
        help_text="Fecha en que se realizó la siembra. No puede ser futura.",
    )
    variedad = models.CharField(
        max_length=120,
        help_text="Nombre de la variedad de arroz sembrada (ej. 'Fedearroz 67').",
    )
    densidad = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Densidad de siembra en kg/ha. Campo opcional.",
    )
    metodo = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        default=DIRECTA,
        help_text="Método de siembra utilizado: directa o trasplante.",
    )

    # Relaciones
    lote = models.ForeignKey(
        Lote,
        on_delete=models.PROTECT,          # Protege el lote de borrados accidentales
        related_name="siembras",
        help_text="Lote físico donde se realizó la siembra.",
    )
    ciclo = models.ForeignKey(
        CicloProductivo,
        on_delete=models.PROTECT,          # Un ciclo no debe eliminarse si tiene siembras
        related_name="siembras",
        help_text="Ciclo productivo al que pertenece esta siembra.",
    )

    # Auditoría
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se registró la siembra en el sistema.",
    )

    class Meta:
        verbose_name = "Siembra"
        verbose_name_plural = "Siembras"
        ordering = ["-fecha_siembra"]
        # Regla de negocio: un lote no puede tener dos siembras en el mismo ciclo
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "ciclo"],
                name="unique_siembra_por_lote_y_ciclo",
            )
        ]

    def __str__(self) -> str:
        return (
            f"Siembra [{self.variedad}] — "
            f"Lote: {self.lote} | Ciclo: {self.ciclo} | "
            f"Fecha: {self.fecha_siembra}"
        )

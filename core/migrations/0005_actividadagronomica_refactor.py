# Generated manually — HU-007 RF-20/21/22/23 refactor

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_actividadagronomica'),
    ]

    operations = [
        # RF-21: nueva fecha y producto para malezas
        migrations.AddField(
            model_name='actividadagronomica',
            name='producto_malezas',
            field=models.CharField(
                blank=True, max_length=100,
                help_text='Herbicida o producto utilizado (si aplica)',
            ),
        ),
        migrations.AddField(
            model_name='actividadagronomica',
            name='fecha_control_malezas',
            field=models.DateField(
                null=True, blank=True,
                help_text='Fecha en que se realizó el control de malezas',
            ),
        ),

        # RF-22: renombrar dosis → dosis_fitosanitario
        #        renombrar fecha_aplicacion → fecha_aplicacion_fitosanitaria
        migrations.RenameField(
            model_name='actividadagronomica',
            old_name='dosis',
            new_name='dosis_fitosanitario',
        ),
        migrations.RenameField(
            model_name='actividadagronomica',
            old_name='fecha_aplicacion',
            new_name='fecha_aplicacion_fitosanitaria',
        ),

        # RF-23: convertir etapa_fenologica a campo con choices y max_length ajustado
        migrations.AlterField(
            model_name='actividadagronomica',
            name='etapa_fenologica',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('GERMINACION', 'Germinación'),
                    ('PLANTULA', 'Plántula'),
                    ('MACOLLAMIENTO', 'Macollamiento'),
                    ('ELONGACION', 'Elongación del tallo'),
                    ('PRIMORDIO', 'Primordio floral'),
                    ('FLORACION', 'Floración / Antesis'),
                    ('GRANO_LECHOSO', 'Grano lechoso'),
                    ('GRANO_PASTOSO', 'Grano pastoso'),
                    ('MADUREZ', 'Madurez fisiológica'),
                    ('COSECHA', 'Cosecha'),
                ],
            ),
        ),

        # Trazabilidad: FK opcional a Siembra
        migrations.AddField(
            model_name='actividadagronomica',
            name='siembra',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='actividades',
                to='core.siembra',
            ),
        ),
    ]

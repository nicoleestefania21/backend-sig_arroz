from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lote',
            name='estado',
            field=models.CharField(
                choices=[
                    ('DISPONIBLE', 'Disponible'),
                    ('EN_USO', 'En uso'),
                    ('EN_PREPARACION', 'En preparación'),
                    ('INACTIVO', 'Inactivo'),
                ],
                default='DISPONIBLE',
                max_length=20,
            ),
        ),
    ]

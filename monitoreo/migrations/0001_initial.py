import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ciclos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitoreoCultivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_monitoreo', models.DateField()),
                ('observaciones_generales', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ciclo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monitoreos', to='ciclos.cicloproductivo')),
            ],
            options={
                'ordering': ['-fecha_monitoreo', '-id'],
            },
        ),
        migrations.CreateModel(
            name='MonitoreoBiologico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('porcentaje_germinacion', models.FloatField(blank=True, help_text='Porcentaje de germinación observado (0-100)', null=True)),
                ('dias_desde_siembra', models.IntegerField(blank=True, help_text='Días transcurridos desde la siembra', null=True)),
                ('num_macollas_promedio', models.FloatField(blank=True, help_text='Número promedio de macollas por planta', null=True)),
                ('plantas_por_metro_cuadrado', models.FloatField(blank=True, help_text='Densidad de plantas por m²', null=True)),
                ('etapa_fenologica', models.CharField(choices=[('GERMINACION', 'Germinación'), ('PLANTULA', 'Plántula'), ('MACOLLAMIENTO', 'Macollamiento'), ('ELONGACION', 'Elongación del tallo'), ('PANICULACION', 'Paniculación'), ('FLORACION', 'Floración'), ('MADUREZ', 'Madurez')], help_text='Etapa fenológica actual del cultivo', max_length=20)),
                ('altura_promedio_cm', models.FloatField(blank=True, help_text='Altura promedio de las plantas en cm', null=True)),
                ('observaciones', models.TextField(blank=True)),
                ('monitoreo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='biologico', to='monitoreo.monitoreocultivo')),
            ],
        ),
        migrations.CreateModel(
            name='MonitoreoFitosanitario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('presencia_plagas', models.BooleanField(default=False, help_text='Indica si se detectó presencia de plagas')),
                ('presencia_enfermedades', models.BooleanField(default=False, help_text='Indica si se detectó presencia de enfermedades')),
                ('observaciones', models.TextField(blank=True)),
                ('monitoreo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fitosanitario', to='monitoreo.monitoreocultivo')),
            ],
        ),
        migrations.CreateModel(
            name='RegistroPlaga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_plaga', models.CharField(max_length=150)),
                ('nivel_infestacion', models.CharField(choices=[('BAJO', 'Bajo'), ('MEDIO', 'Medio'), ('ALTO', 'Alto'), ('CRITICO', 'Crítico')], max_length=10)),
                ('porcentaje_afectacion', models.FloatField(blank=True, help_text='Porcentaje del cultivo afectado (0-100)', null=True)),
                ('accion_tomada', models.TextField(blank=True, help_text='Medida de control aplicada o recomendada')),
                ('observaciones', models.TextField(blank=True)),
                ('monitoreo_fitosanitario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plagas', to='monitoreo.monitoreofitosanitario')),
            ],
        ),
        migrations.CreateModel(
            name='RegistroEnfermedad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_enfermedad', models.CharField(max_length=150)),
                ('severidad', models.CharField(choices=[('LEVE', 'Leve'), ('MODERADA', 'Moderada'), ('SEVERA', 'Severa')], max_length=10)),
                ('porcentaje_afectacion', models.FloatField(blank=True, help_text='Porcentaje del cultivo afectado (0-100)', null=True)),
                ('accion_tomada', models.TextField(blank=True, help_text='Medida de control aplicada o recomendada')),
                ('observaciones', models.TextField(blank=True)),
                ('monitoreo_fitosanitario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enfermedades', to='monitoreo.monitoreofitosanitario')),
            ],
        ),
        migrations.CreateModel(
            name='EstadoGeneralCultivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_general', models.CharField(choices=[('EXCELENTE', 'Excelente'), ('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo')], help_text='Evaluación general del estado del cultivo', max_length=10)),
                ('color_follaje', models.CharField(choices=[('VERDE_OSCURO', 'Verde oscuro'), ('VERDE_NORMAL', 'Verde normal'), ('AMARILLENTO', 'Amarillento'), ('CLOROTICO', 'Clorótico')], help_text='Color predominante del follaje', max_length=15)),
                ('densidad_plantas', models.CharField(choices=[('BAJA', 'Baja'), ('NORMAL', 'Normal'), ('ALTA', 'Alta')], help_text='Densidad de plantas en el lote', max_length=10)),
                ('uniformidad_cultivo', models.BooleanField(default=True, help_text='Indica si el cultivo presenta uniformidad en el lote')),
                ('presencia_malezas', models.BooleanField(default=False, help_text='Indica si hay presencia significativa de malezas')),
                ('nivel_estres_hidrico', models.BooleanField(default=False, help_text='Indica si el cultivo presenta síntomas de estrés hídrico')),
                ('observaciones', models.TextField(blank=True)),
                ('monitoreo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='estado_general', to='monitoreo.monitoreocultivo')),
            ],
        ),
    ]

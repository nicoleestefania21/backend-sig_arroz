from django.contrib import admin
from .models import (
    MonitoreoCultivo,
    MonitoreoBiologico,
    MonitoreoFitosanitario,
    RegistroPlaga,
    RegistroEnfermedad,
    EstadoGeneralCultivo,
)


class MonitoreoBiologicoInline(admin.StackedInline):
    model = MonitoreoBiologico
    extra = 0


class RegistroPlagaInline(admin.TabularInline):
    model = RegistroPlaga
    extra = 0


class RegistroEnfermedadInline(admin.TabularInline):
    model = RegistroEnfermedad
    extra = 0


class MonitoreoFitosanitarioInline(admin.StackedInline):
    model = MonitoreoFitosanitario
    extra = 0


class EstadoGeneralCultivoInline(admin.StackedInline):
    model = EstadoGeneralCultivo
    extra = 0


@admin.register(MonitoreoCultivo)
class MonitoreoCultivoAdmin(admin.ModelAdmin):
    list_display = ['id', 'ciclo', 'fecha_monitoreo', 'created_at']
    list_filter = ['fecha_monitoreo', 'ciclo__estado']
    search_fields = ['ciclo__nombre', 'ciclo__lote__nombre']
    inlines = [
        MonitoreoBiologicoInline,
        MonitoreoFitosanitarioInline,
        EstadoGeneralCultivoInline,
    ]


@admin.register(MonitoreoFitosanitario)
class MonitoreoFitosanitarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'monitoreo', 'presencia_plagas', 'presencia_enfermedades']
    inlines = [RegistroPlagaInline, RegistroEnfermedadInline]


admin.site.register(MonitoreoBiologico)
admin.site.register(RegistroPlaga)
admin.site.register(RegistroEnfermedad)
admin.site.register(EstadoGeneralCultivo)

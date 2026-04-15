from rest_framework import viewsets
from .models import Finca, Lote
from .serializers import FincaSerializer, LoteSerializer


class FincaViewSet(viewsets.ModelViewSet):
    queryset = Finca.objects.all()
    serializer_class = FincaSerializer


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer

    def get_queryset(self):
        finca_id = self.request.query_params.get('finca')
        if finca_id:
            return Lote.objects.filter(finca_id=finca_id)
        return super().get_queryset()
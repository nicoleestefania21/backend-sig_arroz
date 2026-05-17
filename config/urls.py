from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/', include('core.urls')),
    path('api/ciclos/', include('ciclos.urls')),
    path('api/monitoreo/', include('monitoreo.urls')),

]
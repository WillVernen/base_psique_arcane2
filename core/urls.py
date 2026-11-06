from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from usuarios.views import protected_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('pacientes')),
    path('usuarios/', include('usuarios.urls')),
    path('consultas/', include('consultas.urls')),
    # Mídia autenticada (não servir arquivos clínicos publicamente)
    re_path(r'^media/(?P<path>.*)$', protected_media, name='protected_media'),
]

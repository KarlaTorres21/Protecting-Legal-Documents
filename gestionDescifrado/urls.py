from django.urls import path
from gestionDescifrado import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('descifrarCaso/', views.descifrarCaso, name="descifrarCaso"),
    path('verDocumento/<nombreAbogado>/<url>', views.verDocumento, name="verDocumento"),
    path('abreModalCambios/<nombreAbogado>/<url>', views.abreModalCambios, name="abreModalCambios"),
    path('subirCambios/<nombreAbogado>/<nombreDoc>', views.subirCambios, name="subirCambios"),
    path('descifrarDoc/<nombreAbogado>/<numeroK>/<documento>', views.descifrarDoc, name="descifrarDoc"),
    path('modifDocCifrado/<nombreAbogado>/<numeroK>/<documento>', views.modifDocCifrado, name="modifDocCifrado"),
]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT )

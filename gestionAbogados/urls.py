from django.urls import path
from gestionAbogados import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('cifrarCaso/', views.cifrarCaso, name="cifrarCaso"),
    path('agregarAbogado/', views.agregarAbogado, name="agregarAbogado"),
    path('datosAbogado/', views.datosAbogado, name="datosAbogado"),
    path('guardarCaso/', views.guardarCaso, name="guardarCaso"),
]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT )

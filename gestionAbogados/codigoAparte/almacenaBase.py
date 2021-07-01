from gestionAbogados.models import Casos, Abogado, Relacion
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

def almacenaCaso( caso, nombreArchivo, cantidadK, boolCifrado ):
    caso = Casos( nombreCaso = caso, archivoCaso = nombreArchivo, numK = cantidadK, cifrado = boolCifrado ) 
    caso.save()

def almacenaAbogado( nombreAbog, idAbogado ):
    try:
        abogadoGuadar = Abogado.objects.get( idTelegram = idAbogado )
    except ObjectDoesNotExist:
        abogadoGuadar = Abogado( idTelegram = int( idAbogado ), nombreAbogado = nombreAbog )
        abogadoGuadar.save()
    return abogadoGuadar

def obtenObjectCaso( caso, nombreArchivo ):
    instanceCasos = Casos.objects.get( nombreCaso = caso, archivoCaso = nombreArchivo )
    return instanceCasos


def almacenaRelacion( objectCaso, objectAbogado ):
    relacion = Relacion( idCaso = objectCaso, idTelegram = objectAbogado )
    relacion.save()

def borrarRegistros( nombreCaso ):
    with connection.cursor() as cursor:
        cursor.execute("SELECT idCaso FROM gestionAbogados_casos WHERE nombreCaso= %s", [nombreCaso] )
        idCaso = cursor.fetchone()
        deleteAbogados = cursor.execute("DELETE FROM gestionAbogados_relacion WHERE idCaso_id= %s", [ idCaso[0] ] )
        #Relacion.objects.get( idCaso = idCaso[0] ).delete()
        Casos.objects.get( idCaso = idCaso[0] ).delete()
        #deleteCaso = cursor.execute("DELETE FROM gestionAbogados_casos WHERE idCaso= %s", [ idCaso[0] ] )
        #deleteAbogados = cursor.execute("DELETE FROM gestionAbogados_relacion WHERE idCaso_id= %s", [ idCaso[0] ] )

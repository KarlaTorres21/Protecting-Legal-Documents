from django.db import connection

def consultaDatos( idTegramAbogado ):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT nombreCaso,cifrado,numK FROM Caso_abogado WHERE idCaso IN (SELECT idCaso_id FROM gestionAbogados_relacion WHERE idTelegram_id= %s )", [idTegramAbogado] )
        infoCasos = cursor.fetchall()
        cursor.execute("SELECT DISTINCT archivoCaso FROM Caso_abogado WHERE idCaso IN (SELECT idCaso_id FROM gestionAbogados_relacion WHERE idTelegram_id= %s )", [idTegramAbogado] )
        urls = cursor.fetchall()
        cursor.execute("SELECT DISTINCT nombreCaso,nombreAbogado FROM Caso_abogado WHERE idCaso IN (SELECT idCaso_id FROM gestionAbogados_relacion WHERE idTelegram_id= %s ) AND idTelegram_id <> %s", [idTegramAbogado, idTegramAbogado] ) 
        infoAbogados = cursor.fetchall()
    return infoCasos, urls, infoAbogados

def datosCasosAbogado( idTelegramAbogado ):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT ( DISTINCT nombreCaso ) FROM Caso_abogado WHERE idTelegram= %s", [idTelegramAbogado] )
        numCasos = cursor.fetchone()
        cursor.execute("SELECT COUNT ( DISTINCT nombreCaso ) FROM Caso_abogado WHERE ( idTelegram= %s AND cifrado = True )", [idTelegramAbogado] )
        numCifrado = cursor.fetchone()
        cursor.execute("SELECT COUNT ( DISTINCT nombreCaso ) FROM Caso_abogado WHERE ( idTelegram=%s AND cifrado = False )", [idTelegramAbogado] ) 
        numNoCifrado = cursor.fetchone()
    return numCasos, numCifrado, numNoCifrado
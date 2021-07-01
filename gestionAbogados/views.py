from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from jsonCuentas import almacenaJSON, leerJSON

import base64

from .codigoAparte.almacenaBase import almacenaCaso, obtenObjectCaso, almacenaAbogado, almacenaRelacion, borrarRegistros
from AESEAX import encryptAES, separateKey

def cifrarCaso( request ):

    if request.method == "POST":
        nombreCaso = request.POST["nameCaso"]
        uploadedFile = request.FILES['nameFile']

        fs = FileSystemStorage()
        name = uploadedFile.name
        url = fs.url( name )
        fs.save( name, uploadedFile )

        abrirArchivo = open( url[1:], 'rb' )
        leerArchivo = abrirArchivo.read()
        
        IV, key, tag, cipherText = encryptAES( leerArchivo )
        
        docCifrado = open( url[1:], 'wb' )
        docCifrado.write( cipherText )

        IVandTag = open( url[1:] + "IVandTag", 'wb' )
        IVandTag.write( base64.b64encode(IV) )
        IVandTag.write( base64.b64encode(tag) )

        numeroN = int( request.POST["valorN"] )
        numeroK = int( request.POST["valorK"] )

        almacenaCaso( nombreCaso, url, numeroK, 1 )

        nameUserList, chatID = leerJSON()
        users, boolean = separateKey( key, numeroN, numeroK, nombreCaso, nameUserList, chatID, url )

        if boolean is False:
            borrarRegistros( nombreCaso )
            return render( request, "errorInicio.html", {"aviso": "El certificado del abogado %s es invalido " % users, "subaviso": "Por favor ponte en contacto con el abogado y pide nuevamente su certificado"} )

        return render( request, "casoCifrado.html", {"url": url, "nombreCaso": nombreCaso,"usersandID":zip(users, chatID) }  )

    return render( request, "cifrarCaso.html" )

def agregarAbogado( request ):
    return render( request, "agregarAbogado.html" )

def datosAbogado( request ):
    if request.method == "POST":
        datos = {
        'nombre' : request.POST["nombreAbogado"],
        'idChat' : request.POST["idChatTelegram"]
        } 
        almacenaJSON( datos )

        return render( request, "cifrarCaso.html" )
    
    return render( request, "agregarAbogado.html" )

def guardarCaso( request ):
    if request.method == "POST":
        nombreCaso = request.POST["nameCaso"]  
        uploadedFile = request.FILES['nameFile']

        fs = FileSystemStorage()
        name = uploadedFile.name
        url = fs.url( name )
        fs.save( name, uploadedFile )

        numeroN = int( request.POST["valorN"] )

        nombreAbogado, idTelegram = leerJSON()
        almacenaCaso( nombreCaso, url, 0, 0 )
        objectCaso = obtenObjectCaso( nombreCaso, url )
        
        for abogado in range( 0, numeroN ):
            objectAbogado = almacenaAbogado( nombreAbogado[abogado], idTelegram[abogado] )
            almacenaRelacion( objectCaso, objectAbogado )

        return render( request, "casoCifrado.html", {"url": url, "nombreCaso": nombreCaso,"usersandID":zip(nombreAbogado[:numeroN], idTelegram[:numeroN]) }  )
    return render( request, "guardarCaso.html" )


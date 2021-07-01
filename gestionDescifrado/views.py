from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from gestionAbogados.models import Abogado, Casos
from django.core.exceptions import ObjectDoesNotExist
from .codigoAparte.consultaBase import consultaDatos, datosCasosAbogado
from .codigoAparte.firmaDigital import generarFirmaDigital, verificarFirma
from AESEAX import decryptAES, juntarLlaves, modificarAES
import os
from django.core.files.storage import FileSystemStorage
import base64
from datetime import datetime

URL_STATIC = "/media/"

def descifrarCaso( request ):

    if request.method == "POST":
        idTegramAbogado = request.POST["idChatTelegram"]
        try:
            abogado = Abogado.objects.get( idTelegram = idTegramAbogado )
            numCasos, numCifrado, numNoCifrado = datosCasosAbogado( idTegramAbogado )
            infoCasos, urls, infoAbogados = consultaDatos( idTegramAbogado )

            return render( request, "sesionAbogado.html", {"user":abogado.nombreAbogado, "idTelegram":abogado.idTelegram, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), "alerta": "" } )

        except ObjectDoesNotExist:
            return render( request, "errorInicio.html", {"aviso": "No estas registrado en el sistema", "subaviso": "Por favor revisa que tu ID sea correcto"} )
    return render( request, "login.html" )

def verDocumento( request, nombreAbogado, url ):
    docRequerido =  URL_STATIC + url
    resultCifrado = Casos.objects.get( archivoCaso = docRequerido )

    if resultCifrado.cifrado == True:
        cantidadK = resultCifrado.numK
        rangeK = range( cantidadK )
        return render( request, "ingresarDatosDescifrar.html", {"abogados": rangeK, "documento": url, 
                    "numeroK": cantidadK, "nombreAbogado" : nombreAbogado } )

    else:
        with open( docRequerido[1:], 'rb' ) as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename( docRequerido[1:] )
            return response

def abreModalCambios( request, nombreAbogado, url ):
    docRequerido =  URL_STATIC + url
    resultCifrado = Casos.objects.get( archivoCaso = docRequerido )
    if resultCifrado.cifrado == True:
        cantidadK = resultCifrado.numK
        rangeK = range( cantidadK )
        return render( request, "ingresaDatosModif.html", {"abogados": rangeK, "documento": url, "numeroK": cantidadK,
                        "nombreAbogado": nombreAbogado } )
    else: 
        return render( request, "subeCambioComun.html", {"nombreDoc": url, "nombreAbogado": nombreAbogado} )

def subirCambios( request, nombreAbogado, nombreDoc ):
    if request.method == "POST":
        certificadoDigital = request.FILES["RSAKeyPublic"].read()
        clavePrivada = request.FILES["archKeyPrivate"]  
        archivoNuevo = request.FILES["archModificado"]
        nombreArchivo = archivoNuevo.name

        datosAbogado = Abogado.objects.get( nombreAbogado = nombreAbogado.replace("-", " ") )
        idTelegramAbogado = datosAbogado.idTelegram
        numCasos, numCifrado, numNoCifrado = datosCasosAbogado( idTelegramAbogado )
        infoCasos, urls, infoAbogados = consultaDatos( idTelegramAbogado )

        if nombreArchivo == nombreDoc:
            fs = FileSystemStorage()
            url = fs.url( nombreArchivo )

            nameAbogado = datosAbogado.nombreAbogado
            clavePrivadaRSA = clavePrivada.read()
            contentModificado = archivoNuevo.read()

            firmaDigital, exception = generarFirmaDigital( clavePrivadaRSA, contentModificado )

            if exception is False:
                return render( request, "sesionAbogado.html", {"user": nameAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: El archivo no pertenece a una llave privada" } )

            resultVerificacion = verificarFirma( certificadoDigital, contentModificado, firmaDigital )
            
            if resultVerificacion is False:
                return render( request, "sesionAbogado.html", {"user": nameAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: La firma digital y/o el certificado digitial son erroneos, intenta nuevamente " } )
            
            formatoFecha = '%b %d %Y %I:%M%p'
            dateTime = datetime.now()
            datetimeStr = dateTime.strftime( formatoFecha ) 

            documento = open( url[1:], 'wb' )
            documento.write( contentModificado )
            documento.write( b'\n\n'+ b'Ultima modificacion: ' + nameAbogado.encode() + 
                            b' ' + datetimeStr.encode() + b'\n\n' + base64.b32encode( firmaDigital ) )

            return render( request, "sesionAbogado.html", {"user": nameAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "S Los cambios se realizaron de manera correcta " } )

        else:
            return render( request, "sesionAbogado.html", {"user": datosAbogado.nombreAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: El nombre del documento no concuerda con el original, intenta nuevamente " } )

    else:
        return render( request, "subeCambioComun.html")

def descifrarDoc( request, nombreAbogado, numeroK, documento ):
    if request.method == "POST":
        numeroAES = []
        clavePrivadasRSA = []
        clavePrivadasAES = []

        for i in range( int( numeroK ) ):
            numeroAES.append( request.POST["indiceAES%d" % i] )
            clavePrivadasAES.append( request.POST["keyPrivateAES%d" % i] )
            clavePrivadasRSA.append( request.FILES["RSAKeyPrivate%d" % i].read() )

        abrirArchivo = open( URL_STATIC[1:] + documento, 'rb' )
        cipherText = abrirArchivo.read()

        abrirArchivoDatos = open( URL_STATIC[1:] + documento + "IVandTag", 'rb' )
        IVandTag = abrirArchivoDatos.read()
        keyAES, excepcionDecrypt = juntarLlaves( numeroAES, clavePrivadasAES, clavePrivadasRSA )

        if excepcionDecrypt is False:
            datosAbogado = Abogado.objects.get( nombreAbogado = nombreAbogado.replace("-", " ") )
            idTelegramAbogado = datosAbogado.idTelegram
            numCasos, numCifrado, numNoCifrado = datosCasosAbogado( idTelegramAbogado )
            infoCasos, urls, infoAbogados = consultaDatos( idTelegramAbogado )

            return render( request, "sesionAbogado.html", {"user": datosAbogado.nombreAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: Falló la verificación de integridad o se esta usando llave pública " } )

        plainText, autenticidad = decryptAES( base64.b64decode( IVandTag[:24] ), keyAES, base64.b64decode( IVandTag[24:] ), cipherText )

        if autenticidad is True:
            abrirArchivo = open( URL_STATIC[1:] + "01" + documento, 'wb' )
            cipherText = abrirArchivo.write( plainText )

            with open( URL_STATIC[1:] + "01" + documento, 'rb' ) as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename( URL_STATIC[1:] + "01" + documento )
                return response
        else:
            datosAbogado = Abogado.objects.get( nombreAbogado = nombreAbogado.replace("-", " ") )
            idTelegramAbogado = datosAbogado.idTelegram
            numCasos, numCifrado, numNoCifrado = datosCasosAbogado( idTelegramAbogado )
            infoCasos, urls, infoAbogados = consultaDatos( idTelegramAbogado )

            return render( request, "sesionAbogado.html", {"user": datosAbogado.nombreAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: Llave errónea o mensaje corrupto, intenta nuevamente " } )
    else:
        return render( request, "ingresarDatosDescifrar.html")

def modifDocCifrado( request, nombreAbogado, numeroK, documento ):
    if request.method == "POST":
        numeroAES = []
        clavePrivadasRSA = []
        clavePrivadasAES = []

        for i in range( int( numeroK ) ):
            numeroAES.append( request.POST["indiceAES%d" % i] )
            clavePrivadasAES.append( request.POST["keyPrivateAES%d" % i] )
            clavePrivadasRSA.append( request.FILES["RSAKeyPrivate%d" % i].read() )
        certificadoDigital = request.FILES["RSAKeyPublic"].read()
        docModificado = request.FILES["docModificado"]
        nombreArchivo = docModificado.name

        datosAbogado = Abogado.objects.get( nombreAbogado = nombreAbogado.replace("-", " ") )
        idTelegramAbogado = datosAbogado.idTelegram
        numCasos, numCifrado, numNoCifrado = datosCasosAbogado( idTelegramAbogado )
        infoCasos, urls, infoAbogados = consultaDatos( idTelegramAbogado )
        nameAbogado = datosAbogado.nombreAbogado

        if nombreArchivo[2:] == documento:
            contentModificado = docModificado.read()
            firmaDigital, excepcion = generarFirmaDigital( clavePrivadasRSA[0], contentModificado )

            if excepcion is False:
                return render( request, "sesionAbogado.html", {"user": nameAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: El archivo no pertenece a una llave privada" } )

            resultVerificacion = verificarFirma( certificadoDigital, contentModificado, firmaDigital )

            if resultVerificacion is False:
                return render( request, "sesionAbogado.html", {"user": nameAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: La firma digital y/o el certificado digitial son erroneos, intenta nuevamente " } )

            keyAES, excepcionDecrypt = juntarLlaves( numeroAES, clavePrivadasAES, clavePrivadasRSA )

            if excepcionDecrypt is False:
                return render( request, "sesionAbogado.html", {"user": datosAbogado.nombreAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: Falló la verificación de integridad o se esta usando llave pública " } )

            IV, tag, cipherText = modificarAES( keyAES, contentModificado, nameAbogado, firmaDigital )

            abrirArchivo = open( URL_STATIC[1:] + documento, 'wb' )
            cipherText = abrirArchivo.write( cipherText )

            abrirArchivoDatos = open( URL_STATIC[1:] + documento + "IVandTag", 'wb' )
            IVandTag = abrirArchivoDatos.write( base64.b64encode( IV ) )
            IVandTag = abrirArchivoDatos.write( base64.b64encode( tag ) )

            return render( request, "sesionAbogado.html", {"user": datosAbogado.nombreAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "S Los cambios se realizaron de manera correcta " } )
        else:
            return render( request, "sesionAbogado.html", {"user": datosAbogado.nombreAbogado, "idTelegram": idTelegramAbogado, 
                        "infoCasos": zip(infoCasos, urls), "infoAbogados": infoAbogados, "numeroCasos": int(numCasos[0]), 
                        "casosCifrados": int(numCifrado[0]), "casosComunes": int(numNoCifrado[0]), 
                        "alerta": "E Error: El nombre del documento no concuerda con el original, intenta nuevamente " } )
    else:
        return render( request, "ingresarDatosDescifrar.html")

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from OpenSSL import crypto, SSL

PATH_PUBLIC_KEY = "media/LlavesPublicas/"
PUBLIC_FILE_MASTER = PATH_PUBLIC_KEY + "Master Key receiver.pem"

def generarFirmaDigital( clavePrivadaRSA, message ):
    try:
        key = RSA.importKey( clavePrivadaRSA )
        resultHash = SHA256.new( message )
        signature = pkcs1_15.new( key ).sign( resultHash )
        return signature, True
    except:
        return "", False

def verificarFirma( contenidoCertificado, message, signature ):
    try:
        certificado = crypto.load_certificate_request(crypto.FILETYPE_PEM, contenidoCertificado)

        contenidoPublica = open( PUBLIC_FILE_MASTER, 'rb' ).read()
        llavePublica = crypto.load_publickey(crypto.FILETYPE_PEM, contenidoPublica)

        print( "PASO VERIFICACION" )
        certificado.verify( llavePublica )

        print( "PASO VERIFICACION" )
        publicKeyAbogado = crypto.dump_publickey( crypto.FILETYPE_PEM, certificado.get_pubkey() )

        print( publicKeyAbogado )

        key = RSA.import_key( publicKeyAbogado  )
        resultHash = SHA256.new(message)
        pkcs1_15.new(key).verify( resultHash, signature )
        return True
    except:
        return False

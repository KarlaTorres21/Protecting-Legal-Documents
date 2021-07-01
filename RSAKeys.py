from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from OpenSSL import crypto, SSL

PATH = "media/LlavesPublicas/"
PUBLIC_FILE_MASTER = PATH + "Master Key receiver.pem"

def cifrarKeyRSA( nombreAbogado, message ):
    try:
        contenidoCertificado = open( PATH + nombreAbogado + " certificado.pem", 'rb' ).read()
        certificado = crypto.load_certificate_request(crypto.FILETYPE_PEM, contenidoCertificado)

        contenidoPublica = open( PUBLIC_FILE_MASTER, 'rb' ).read()
        llavePublica = crypto.load_publickey(crypto.FILETYPE_PEM, contenidoPublica)

        certificado.verify( llavePublica )

        publicKeyAbogado = crypto.dump_publickey( crypto.FILETYPE_PEM, certificado.get_pubkey() )
        archKey = RSA.import_key( publicKeyAbogado )

        cipher = PKCS1_OAEP.new( archKey )
        cipherText = cipher.encrypt( message )
        return cipherText, True

    except:
        return "", False

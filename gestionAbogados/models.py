from django.db import models

class Casos( models.Model ):
    idCaso = models.IntegerField( primary_key = True )
    nombreCaso = models.CharField( max_length = 100 )
    archivoCaso = models.CharField( max_length = 200 )
    numK = models.IntegerField()
    cifrado = models.BooleanField()

class Abogado( models.Model ):
    idTelegram = models.IntegerField( primary_key = True )
    nombreAbogado = models.CharField( max_length = 50 )
    #usuario = models.CharField( max_length = 50 )
    #contrasenia = models.CharField( max_length = 50 )

class Relacion( models.Model ):
    idCaso = models.ForeignKey( Casos, on_delete = models.CASCADE )
    idTelegram = models.ForeignKey( Abogado, on_delete = models.CASCADE )
    #idCaso = models.IntegerField(  )
    #idTelegram = models.IntegerField()

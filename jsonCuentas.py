import json 

def almacenaJSON( datos ):
    with open("jsonCuentas.json", mode='r') as f:
        feeds = json.load( f )
    with open("jsonCuentas.json", "w") as f:
        feeds["usuarios"].append( datos )
        json.dump( feeds, f )

def leerJSON( ):
    cadenaJSON = json.loads(open('jsonCuentas.json').read())
    nameUserList = []
    chatID = []
    for jsonRead in cadenaJSON["usuarios"]:
        nameUserList.append( jsonRead["nombre"] )
        chatID.append( jsonRead["idChat"] )
    return nameUserList, chatID

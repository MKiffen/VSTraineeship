#!/usr/bin/env python
"""
Author: Max Kiffen
Date: 04-11-2021
Flask script for contacting API's, reading and sending data to user and database
"""
# Import requirements
from datetime import datetime, timedelta
from flask import Flask
from flask import request
from flask import json 
import sys

# Import modules with API's
from hotelapi import hotelapi
from NS_API import NsTrip
from skyscannerAPI import run_skyscannerAPI
from sqlconnection import db_interactions
from json_to_html import parse

# dictionary met de coordinated, landcodes en vliegveldcodes per stad
"""
Deze dictionary bevat de steden, hun coordinaten, land en luchthavencode.
Dit is belangrijk voor het vertalen van de invoer van de user naar werkende variabelen in de API's
"""
citytocoordinates = {
    "BARCELONA": (41.385063,2.173404, "ES", "BCN"),
    "PARIJS": (48.856613,2.352222, "FR", "CDG"),
    "ROME":	(41.902782,12.49636, "IT", "FCO"),
    "MILAAN": (45.463619,9.188120, "IT", "MXP"),
    "MADRID": (40.416775,-3.703790, "SP", "MAD"),
    "BERLIJN": (52.520008,13.404954, "DE", "BER"),
    "HAMBURG": (53.551086,9.993682, "DE", "HAM"),
    "LISSABON": (38.736946,-9.142685, "PT", "LIS"),
    "ATHENE": (37.983810,23.727539, "GR", "ATH"),
    "LONDEN": (51.509865,-0.118092, "UK", "LHR"),
    "MANCHESTER": (53.483959, -2.244644, "UK", "MAN"),
    "BRUGGE": (51.20892,  3.22424, "BE", "OST"),
    "LEIPZIG": (51.340199, 12.360103, "DE", "LEJ"),
    "LIVERPOOL": (53.400002, -2.983333, "UK", "LPL" ),
    "PORTO": (41.150223, -8.629932, "PT", "OPO" ),
    "MUNCHEN": (48.137154, 11.576124, "DE", "MUC" ),
    "VILLARREAL": (39.939771, -0.100593, "SP", "VLC" ),
    "BERGAMO": (45.695000, 9.670000, "IT", "BGY" ),
    "BERN": (46.947456, 7.451123, "CH", "BRN" ),
    "SALZBURG": (47.811195, 13.033229, "AT", "SZG" ),
    "LILLE": (50.629250, 3.057256, "FR", "LIL" ),
    "WOLFSBURG": (52.427547, 10.780420, "DE", "HAJ" ),
    "SEVILLA": (37.392529, -5.994072, "SP", "SVQ" ),
    "TURIJN": (45.116177, 7.742615, "IT", "TRN" ),
    "MALMO": (55.607075, 13.002716, "SE", "MMX" )
    }


# methode voor het samenvoegen van de informatie uit de API's
def sorteren(vlucht_heen,ns_heen,vlucht_terug,ns_terug,hotels):
    """
    Deze functie sorteert de .json informatie uit de API's in de juiste volgorde en geeft het terug als dictionary.
    Input:
    - Dictionary's en lijsten
    Output:
    - Dictionary
    """
    heenreisdict = {"heenreis":[vlucht_heen,ns_heen]}
    terugreisdict = {"terugreis":[vlucht_terug,ns_terug]}
    reisdict = {"reis":[heenreisdict,terugreisdict,hotels]}
    return reisdict

def error_response(response_status, msg):
    """
    Function to create a response class when an error has occured
    """
    
    response_status = response_status   #Status in response to return
    message = msg                            #Message to give user  

    response = app.response_class(status=response_status,mimetype="application/json",response=str(message))
    return response


app = Flask(__name__)

# Attemping the connection to the database container:
conn, st = db_interactions.trySqlConn()
if st !=0:
    print("Could not connect with sql container on start up, check if sql container is up and running and configured properly", file = sys.stderr)
    print("Closing the container", file = sys.stderr)
    sys.exit(1)
else:  
    print("Connected to database!", file = sys.stderr)

# lege route, gives usage of flask API
@app.route("/")
def index():
    """
    Deze route words aangeroepen als het adres wordt aangeroepen zonder route. Het geeft dan de mogelijke opties terug met de juiste formatering.
    """
    usagestr = 'Usage full program: -X GET "http://<hostname>[:<port>]/api?maxopties=<maxopties>&reispersonen=<reispersonen>&reisdatumheen=<reisdatumheen>&reisdatumterug=<reisdatumterug>&reisbestemming=<reisbestemming>&reisvertrek=<reisvertrek>" \n'
    usagestr = usagestr + 'Usage hotelAPI only: -X GET "http://<hostname>[:<port>]/hotelapi?maxopties=<maxopties>&reisbestemming=<reisbestemming>" \n'
    usagestr = usagestr + 'Usage NSAPI only: -X GET "http://<hostname>[:<port>]/nsapi?maxopties=<maxopties>&reisvertrek=<reisvertrek>&reisvliegveld=<reisvliegveld>&tijd=<tijd>" \n'
    usagestr = usagestr + 'Usage skyscannerAPI only: -X GET "http://<hostname>[:<port>]/vluchtapi?reispersonen=<reispersonen>&reisdatumheen=<reisdatumheen>&reisdatumterug=<reisdatumterug>&reisbestemming=<reisbestemming>&maxopties=<maxopties>" \n'
    usagestr = usagestr + 'Usage selectdb: -X GET "http://<hostname>[:<port>]/selectdb?reisid=<reisid>'
    return usagestr

# Hotel API. Heeft een aantal opties en bestemming nodig
@app.route("/hotelapi", methods=['GET','POST'])
def hotelreach():
    """
    Deze route vraagt de impala hotelapi aan.
    Het haalt eerst de variabelen op uit de aanvraag en checkt ze dan op valide input.
    Het vertaalt dan de bestemmingsinput naar coordinaten en roept de hotelapi aan via de module.
    Het resultaat wordt dan vertaalt naar application/json en nog voordat het terug wordt gegeven wordt de error code gecheckt.
    Error code: 0 = Succes
    Error code: 1 = Geen verbinding met de API
    Error code: 2 = Geen informatie gevonden
    Error code: 3 = Fout in de input
    Error code: 4 = Te veel vragen naar de API
    Input:
    - Integer: Maxopties
    - String: Reisbestemming
    Output:
    - Json object met hotels
        - Naam
        - Adres
        - Inchecktijd
        - Uitchecktijd
        - ID in de hotelapi
    """
    # aanvragen van variabelen
    if request.method == 'POST':
        maxopties = request.form['maxopties']
        reisbestemming = request.form['reisbestemming']
    else:
        maxopties = request.args.get('maxopties', 5)
        reisbestemming = request.args.get("reisbestemming", "BARCELONA")
    
    # error handeling van de variabelen
    try:
        maxopties = int(maxopties)
    except (ValueError,TypeError):
        msg = "maxopties moet een getal zijn in de vorm van een integer. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    if maxopties <= 0:
        msg = "maxopties moet groter zijn dan 0. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
        
    reisbestemming = reisbestemming.upper()
    if reisbestemming in citytocoordinates.keys():
        pass
    else:
        msg = "Opgeven bestemming niet bekend. \n"
        response = error_response(response_status = 400, msg = msg)
        return response

    # vertalen van de opgegeven stad naar coordinaten
    reiscodlat = str(citytocoordinates[reisbestemming][0])
    reiscodlong = str(citytocoordinates[reisbestemming][1])

    # uitvoering van de hotelapi
    status, hotelresult = hotelapi(maxopties, reiscodlat, reiscodlong)
    hotelresult = json.dumps(hotelresult)
    #hotelresult = json.loads(hotelresult)

    response = app.response_class(status=200,mimetype="application/json",response=hotelresult)
    if status == 0:
        pass
    elif status == 1:
        msg = "geen werkende verbinding met hotel API. \n"
        response = error_response(response_status = 500, msg = msg) 
    elif status == 2:
        msg = "geen informatie gevonden met hotel API. \n"
        response = error_response(response_status = 502, msg = msg)
    elif status == 4:
        msg = "Probeer het later opnieuw. \n"
        response = error_response(response_status = 503, msg = msg)
    else:
        msg = "Hotel API is niet werkend. \n"
        response = error_response(response_status = 500, msg = msg)
    return response

# NS API. Heeft vertrekplaats, aankomstplaats en vertrektijd nodig
@app.route("/nsapi", methods=['GET','POST'])
def nsreach():
    """
    Deze route vraagt de NSapi aan.
    Het haalt eerst de variabelen op uit de aanvraag en checkt ze dan op valide input.
    Het roept de nsapi aan via de module.
    Dan wordt er gecheckt of error codes.
    Error code: 0 = Succes
    Error code: 1 = Geen verbinding met de API
    Error code: 2 = Geen informatie gevonden
    Error code: 3 = Fout in de input
    Error code: 4 = Te veel vragen naar de API
    Het resultaat wordt dan vertaalt naar application/json en terug gegeven.
    Input:
    - Integer: Maxopties
    - String: Reisvertrek(plaats)
    - String: Reisvliegveld(vertrek)
    - DateTime: (vertrek)Tijd(en datum)
    Output:
    - Json object met NS reizen
        - Reconstructiecode
        - Duur
        - Overstappen
        - Prijs
        - Vertrektijd
        - Aankomstijd
    """
    # aanvragen van de variabelen
    if request.method == 'POST':
        maxopties = request.form["maxopties"]
        reisvertrek = request.form["reisvertrek"]
        reisvliegveld = request.form["reisvliegveld"]
        tijd = request.form["tijd"]
    else:
        maxopties = request.args.get("maxopties", 5)
        reisvertrek = request.args.get("reisvertrek", "Barendrecht")
        reisvliegveld = request.args.get("reisvliegveld", "Rotterdam_Centraal")
        tijd = request.args.get("tijd", "2021-11-29T16:00:00")
    
    # error handeling van de input
    try:
        maxopties = int(maxopties)
    except (ValueError,TypeError):
        msg = "maxopties moet een getal zijn in de vorm van een integer. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    if maxopties <= 0:
        msg = "maxopties moet groter zijn dan 0. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    if reisvliegveld.find("-") != None:
        reisvliegveld = reisvliegveld.replace("-","_")
    else:
        pass
    try:
        tijd = datetime.strptime(tijd,"%Y-%m-%dT%H:%M:%S")
        if tijd < datetime.now():
            msg = "kan niet in het verleden boeken. \n"
            response = error_response(response_status = 400, msg = msg)
            return response
            
        tijd = str(tijd)
    except (TypeError,ValueError):
        msg = "tijd moet in format van 'YYYY'-'MM'-'DD'T'HH':'MM':'SS'. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    
    # aanmaken van object trip van classe NsTrip
    nstrip = NsTrip(reisvertrek,reisvliegveld,tijd)
    
    # zetten van opties trip
    status = NsTrip.retrieveTripOptions(nstrip,int(maxopties))
    if status == 0:
        pass
    elif status == 1:
        msg = "geen werkende verbinding met NS API. \n"
        response = error_response(response_status = 500, msg = msg) 
        return response
    elif status == 2:
        msg = "geen informatie gevonden met NS API. \n"
        response = error_response(response_status = 502, msg = msg)
        return response
    elif status == 3:
        msg = "Opgegeven station niet bekend. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    else:
        msg = "NS API is niet werkend. \n"
        response = error_response(response_status = 500, msg = msg)
        return response

    # terugvragen van opties trip van de NS api
    nsresult  = NsTrip.getTripOptions(nstrip)
    nsresult  = json.dumps(nsresult, sort_keys=False)
    #nsresult = json.loads(nsresult)
    
    response  = app.response_class(status=200,mimetype="application/json",response=nsresult)

    return response

# Skyscanner API. Neemt de informatie van de user en verandert deze voor de informatie naar de andere API's
@app.route("/vluchtapi", methods=['GET','POST'])
def vluchtreach():
    """
    Deze route vraagt de Skyscanner API aan.
    Het haalt eerst de variabelen op uit de aanvraag en checkt ze dan op valide input.
    Dan worden de gegevens uit de bestemmingsdictionary gehaald.
    De skyscanner API wordt dan twee keer aangeroepen, voor een heen en terugvlucht, via de module.
    Dan wordt er gecheckt of error codes.
    Error code: 0 = Succes
    Error code: 1 = Geen verbinding met de API
    Error code: 2 = Geen informatie gevonden
    Error code: 3 = Fout in de input
    Error code: 4 = Te veel vragen naar de API
    Het resultaat wordt dan samengevoegd en vertaalt naar application/json en terug gegeven.
    Input:
    - Integer: Reispersonen
    - Integer: Maxopties
    - Date: Reisdatumheen
    - Date: Reisdatumterug
    - String: Reisbestemming
    Output:
    - Json object met vluchten
        - Externe vlucht ID
        - Vluchtvertrektijd
        - Vluchtaankomsttijd
        - Vluchtduur
        - Vluchtprijs
        - Vluchtmaatschappij
        - Vliegveldaankomst
    """
    # ontvangen van de variabelen van de user en error handeling hiervan
    if request.method == "POST":
        reispersonen = request.form["reispersonen"]
        maxopties = request.form["maxopties"]
        reisdatumheen = request.form["reisdatumheen"]
        reisdatumterug = request.form["reisdatumterug"]
        reisbestemming = request.form["reisbestemming"]
    else:
        reispersonen = request.args.get("reispersonen", 1)
        maxopties = request.args.get("maxopties", 3)
        reisdatumheen = request.args.get("reisdatumheen", "2022-05-30")
        reisdatumterug = request.args.get("reisdatumterug", "2022-06-02")
        reisbestemming = request.args.get("reisbestemming", "BERLIJN")
    try:
        reispersonen = int(reispersonen)
        maxopties = int(maxopties)
    except (ValueError,TypeError):
        msg = "maxopties en reispersonen moeten een getal zijn in de vorm van een integer. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    if reispersonen <= 0 or maxopties <= 0:
        msg = "reispersonen en maxopties moeten groter zijn dan 0. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    elif reispersonen > 10:
        msg = "kan geen vlucht boeken voor meer dan 10 personen per keer. \n"
        response = error_response(response_status = 400, msg = msg)
        return response

    try:
        reisdatumheen = datetime.strptime(reisdatumheen,"%Y-%m-%d")
        reisdatumterug = datetime.strptime(reisdatumterug,"%Y-%m-%d")
        if reisdatumheen < datetime.now() or reisdatumterug < datetime.now():
            msg = "mag niet in het verleden boeken. \n"
            response = error_response(response_status = 400, msg = msg)
            return response
        elif reisdatumterug < reisdatumheen:
            msg = "datum terug is eerder dan datum heen. \n"
            response = error_response(response_status = 400, msg = msg)
            return response
            
        reisdatumterug = datetime.strftime(reisdatumterug,"%Y-%m-%d")
        reisdatumheen = datetime.strftime(reisdatumheen,"%Y-%m-%d")
    except (TypeError,ValueError):
        msg = "reisdatumheen en reisdatumterug moeten een datum zijn in het formaat 'YYYY'-'MM'-'DD'. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
       
    reisbestemming = reisbestemming.upper()
    if reisbestemming in citytocoordinates.keys():
        pass
    else:
        msg = "Opgeven bestemming staat niet in de dictionary. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    reislandbestemming = str(citytocoordinates[reisbestemming][2])
    reisbestemmingvlucht = str(citytocoordinates[reisbestemming][3])
    land = "NL"
    reisvertrek = "AMS"
    
    # contact leggen met de API's via skyscannerAPI.py
    result_heen, error = run_skyscannerAPI(reispersonen, land, reisdatumheen, reisbestemmingvlucht, str(maxopties), reisvertrek)
    result_terug, error = run_skyscannerAPI(reispersonen, reislandbestemming, reisdatumterug, reisvertrek, str(maxopties), reisbestemmingvlucht)
    if error == 0:
        pass
    elif error == 1:
        msg = "geen verbinding met de skyscanner API. \n"
        response = error_response(response_status = 500, msg = msg)
        return response 
    elif error == 2:
        msg = "geen informatie uit de skyscanner API verkregen. \n"
        response = error_response(response_status = 502, msg = msg)
        return response
    elif error == 3:
        msg = "skyscanner API heeft een fout gevonden in de input. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    
    result_heen = json.loads(result_heen)
    result_terug = json.loads(result_terug)

    # resultaten combineren
    resultaat_dict ={}
    resultaat_dict["heenvlucht"] =result_heen
    resultaat_dict["terugvlucht"] =result_terug
    
    response = app.response_class(status=200,mimetype="application/json",response=json.dumps(resultaat_dict, sort_keys = False))

    return response

# Combinatie van alle API in sequentie
@app.route("/api", methods=['GET','POST'])
def totalapi(conn = conn):
    """
    Deze route vraagt de totale flaskapp aan met een combinatie van alle drie de API's
    Het haalt eerst de variabelen op uit de aanvraag en checkt ze dan op valide input.
    Dan worden de gegevens uit de bestemmingsdictionary gehaald.
    De skyscanner API wordt dan twee keer aangeroepen, voor een heen en terugvlucht, via de module.
    Dan wordt er gecheckt of error codes voor de skyscanner API.
    De datum die daaruit terugkomt wordt dan verlaagt met twee uur zodat je er optijd bent met de NS.
    Dan wordt de NSapi twee keer aangeroepen en gecheckt op errors.
    Hierna roept het de hotelapi aan en checkt ook deze op errors.
    Error code: 0 = Succes
    Error code: 1 = Geen verbinding met de API
    Error code: 2 = Geen informatie gevonden
    Error code: 3 = Fout in de input
    Error code: 4 = Te veel vragen naar de API
    Het resultaat wordt dan gesorteerd en samengevoegd.
    Dan wordt het vertaalt naar application/json.
    Dan wordt de database gevuld met deze nieuwe informatie en dan wordt het terug gegeven aan de user.
    Input:
    - Integer: Reispersonene
    - Integer: Maxopties
    - Date: Reisdatumheen
    - Date: Reisdatumterug
    - String: Bestemming
    - String: Vertrekplaats
    Output:
    - Json object met vluchten, ns reizen en hotels in volgorde
        - Vlucht
            - Vertektijd
            - Aankomstijd
            - Duur
            - Prijs
            - Maatschappij
            - Aankomstvliegveld
        - NS
            - Vertrektijd
            - Aankomsttijd
            - Duur
            - Overstappen
            - Prijs
        - Nogmaals vlucht en NS reis
        - Hotels
            - Naam
            - Adres
            - Inchecktijd
            - Uitchecktijd
    """
    # vaststellen van alle parameters
    if request.method == "POST":
        reispersonen = request.form["reispersonen"]
        maxopties = request.form["maxopties"]
        reisdatumheen = request.form["reisdatumheen"]
        reisdatumterug = request.form["reisdatumterug"]
        reisbestemming = request.form["reisbestemming"]
        reisvertrek = request.form["reisvertrek"]
    else:
        reispersonen = request.args.get('reispersonen', 1)
        maxopties = request.args.get('maxopties', 3)
        reisdatumheen = request.args.get('reisdatumheen',"2022-05-30")
        reisdatumterug = request.args.get('reisdatumterug',"2022-06-02")
        reisbestemming = request.args.get('reisbestemming',"BERLIJN")
        reisvertrek = request.args.get('reisvertrek',"Utrecht_Centraal")
    
    #Check if database is connected
    status = db_interactions.sqlCheckConn(conn)
    if status != 0:
        #retry to make connection with database:
        conn, st = db_interactions.trySqlConn(N = 5, s =5)
        if st != 0:
           print("ERROR: CAN'T CONNECT TO THE SQL SERVER", file = sys.stderr)
           msg = "Sorry, geen werkende verbinding met onze database. Probeer later opnieuw. \n"
           response = error_response(response_status = 500, msg = msg)
           return response    
    
    # error handeling
    try:
        reispersonen = int(reispersonen)
        maxopties = int(maxopties)
    except (ValueError,TypeError):
        msg = "maxopties en reispersonen moeten een getal zijn in de vorm van een integer. \n"
        response = error_response(response_status = 400, msg = msg)
        return response

    if reispersonen <= 0 or maxopties <= 0:
        msg = "reispersonen en maxopties moeten groter zijn dan 0. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    elif reispersonen > 50:
        msg = "kan geen reis boeken voor meer dan 50 personen per keer. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    try:
        reisdatumheen = datetime.strptime(reisdatumheen,"%Y-%m-%d")
        reisdatumterug = datetime.strptime(reisdatumterug,"%Y-%m-%d")
        if reisdatumheen < datetime.now() or reisdatumterug < datetime.now():
            msg = "mag niet in het verleden boeken. \n"
            response = error_response(response_status = 400, msg = msg)
            return response
        elif reisdatumterug < reisdatumheen:
            msg = "datum terug is eerder dan datum heen. \n"
            response = error_response(response_status = 400, msg = msg)
            return response

        reisdatumterug = datetime.strftime(reisdatumterug,"%Y-%m-%d")
        reisdatumheen = datetime.strftime(reisdatumheen,"%Y-%m-%d")
    except (TypeError,ValueError):
        msg = "reisdatumheen en reisdatumterug moeten een datum zijn in het formaat 'YYYY'-'MM'-'DD'. \n"
        response = error_response(response_status = 400, msg = msg)
        return response

    reisbestemming = reisbestemming.upper()
    if reisbestemming in citytocoordinates.keys():
        pass
    else:
        msg = "Opgeven bestemming staat niet in de dictionary. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    if reisvertrek.find("-") != None:
        reisvliegveld = reisvertrek.replace("-","_")
    else:
        pass
    
    # parameters die we parsen
    reiscodlat = str(citytocoordinates[reisbestemming][0])
    reiscodlong = str(citytocoordinates[reisbestemming][1])
    reisland = str(citytocoordinates[reisbestemming][2])
    reisbestemmingvlucht = str(citytocoordinates[reisbestemming][3])
    reisvliegveld = "Schiphol"

    # aanroepen skyscannerapi
    result_heen, error = run_skyscannerAPI(reispersonen, "NL", reisdatumheen, reisbestemmingvlucht, str(maxopties), "AMS")
    result_terug, error = run_skyscannerAPI(reispersonen, reisland, reisdatumterug, "AMS", str(maxopties), reisbestemmingvlucht)

    if error == 0:
        pass
    elif error == 1:
        msg = "geen verbinding met de skyscanner API. \n"
        response = error_response(response_status = 500, msg = msg)
        return response 
    elif error == 2:
        msg = "geen informatie uit de skyscanner API verkregen. \n"
        response = error_response(response_status = 502, msg = msg)
        return response
    elif error == 3:
        msg = "skyscanner API heeft een fout gevonden in de input. \n"
        response = error_response(response_status = 400, msg = msg)
        return response

    result_heen = json.loads(result_heen)
    result_terug = json.loads(result_terug)

    # veranderen van de opgegeven vertrektijd met de nieuwe waarde uit de skyscanner api
    vertrektijd = result_heen["vlucht"][0]["vluchtvertrektijd"]
    aankomsttijd = result_terug["vlucht"][0]["vluchtaankomsttijd"]

    # aanroepen van NSapi voor vertrek
    vertrekdatetime = datetime.strptime(vertrektijd,'%Y-%m-%dT%H:%M:%S')
    vertrekdatetime = vertrekdatetime - timedelta(hours=2)
    vertrektijd = str(vertrekdatetime)
    nstrip = NsTrip(reisvertrek,reisvliegveld,vertrektijd)
    
    # error handeling NS API
    status = NsTrip.retrieveTripOptions(nstrip,int(maxopties))
    if status == 0 :
        pass
    elif status == 1:
        msg = "geen werkende verbinding met NS API. \n"
        response = error_response(response_status = 500, msg = msg) 
        return response
    elif status == 3:
        msg = "Opgegeven station niet bekend. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    else:
        msg = "NS API is niet werkend. \n"
        response = error_response(response_status = 500, msg = msg)
        return response
    nsresult_heen = NsTrip.getTripOptions(nstrip)
    nsresult_heen = json.dumps(nsresult_heen, sort_keys=False)
    nsresult_heen = json.loads(nsresult_heen)
    
    # aanroepen van NSapi voor terugreis
    aankomstdatetime = datetime.strptime(aankomsttijd,'%Y-%m-%dT%H:%M:%S')
    aankomstdatetime = aankomstdatetime - timedelta(hours=2)
    aankomsttijd = str(aankomstdatetime)
    nstrip = NsTrip(reisvliegveld,reisvertrek,aankomsttijd)

    # error handeling NS API
    status = NsTrip.retrieveTripOptions(nstrip,int(maxopties))
    if status == 0 :
        pass
    elif status == 1:
        msg = "geen werkende verbinding met NS API. \n"
        response = error_response(response_status = 500, msg = msg) 
        return response
    elif status == 2:
        msg = "geen informatie gevonden met NS API. \n"
        response = error_response(response_status = 502, msg = msg)
        return response
    elif status == 3:
        msg = "Opgegeven station niet bekend. \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    else:
        msg = "NS API is niet werkend. \n"
        response = error_response(response_status = 500, msg = msg)
        return response

    nsresult_terug = NsTrip.getTripOptions(nstrip)
    nsresult_terug = json.dumps(nsresult_terug, sort_keys=False)
    nsresult_terug = json.loads(nsresult_terug)

    # aanroepen van hotelapi
    status, hotelresult = hotelapi(maxopties, reiscodlat, reiscodlong)
    hotelresult = json.dumps(hotelresult)
    hotelresult = json.loads(hotelresult)

    if status == 0:
        pass
    elif status == 1:
        msg = "geen werkende verbinding met hotel API. \n"
        response = error_response(response_status = 500, msg = msg)
        return response
    elif status == 2:
        msg = "geen informatie gevonden met hotel API. \n"
        response = error_response(response_status = 502, msg = msg)
        return response
    elif status == 4:
        msg = "Probeer het later opnieuw. \n"
        response = error_response(response_status = 503, msg = msg)
        return response
    else:
        msg = "Hotel API is niet werkend. \n"
        response = error_response(response_status = 500, msg = msg)
        return response

    # combineren van resultaten
    resultaat = sorteren(result_heen,nsresult_heen,result_terug,nsresult_terug,hotelresult)
    op_te_slaan_reis_db = (reisvertrek, reisbestemming, reisvliegveld, reisdatumheen, reisdatumterug, reispersonen)
    reis_id = db_interactions.insertInformation(conn, resultaat, op_te_slaan_reis_db)

    resultaat["reisid"] = reis_id  
    res_html = parse(resultaat)

    response = app.response_class(status=200,mimetype="application/html",response=res_html)
    
    return response

    
@app.route("/selectdb", methods=['GET','POST'])
def databasereach(conn = conn):
    """
    Deze route wordt gebruikt om de data te halen uit de database wat gelinkt is aan een bepaalde reis_id.
    Het haalt eerst de reis_id variabele uit de invoer en checkt deze op fouten.
    De data wordt dan opgehaald uit de database en vertaald naar application/json
    Deze wordt dan terugegeven aan de user.
    Input:
    - Integer: ReisID
    Output:
    - Json object met alle informatie uit de database van 1 reis_ID
    - Voor structuur zie /api route
    """
    #Check if data base is connected
    status = db_interactions.sqlCheckConn(conn)
    if status != 0:
        #retry to make connection with database:
        conn, st = db_interactions.trySqlConn(N = 3, s =2)
        if st != 0:
           print("ERROR: CAN'T CONNECT TO THE SQL SERVER", file = sys.stderr)
           msg = "Sorry, geen werkende verbinding met onze database. Probeer later opnieuw. \n"
           response = error_response(response_status = 500, msg = msg)
           return response

    # aanvragen van variabelen
    if request.method == 'POST':
        reis_id = request.form['reisid']
    else:
        reis_id = request.args.get("reisid")

    #  error handeling van de variabelen
    if reis_id == None:
        msg = "geen reis_id ingegeven \n"
        response = error_response(response_status = 400, msg = msg)
        return response
    
    #check if reis_id is an int
    try:
        reis_id = eval(reis_id)
    except:
        msg = "reis_id moet in een integer zijn, bv. /selectdb?reisid=1"
        response = error_response(response_status = 400, msg = msg)
        return response

    if type(reis_id) != int:
        msg = "reis_id moet een integer zijn"
        response = error_response(response_status = 400, msg = msg)
        return response

    # data ophalen uit de database
    dataIsFound, data = db_interactions.getDataFromDb(conn, reis_id)

    if dataIsFound == False:
        msg = "Geen data gevonden for ingegeven reis_id"
        response = error_response(response_status = 400, msg = msg)
        return response

    data = json.dumps(data, default=str, sort_keys = False)
    #data = json.loads(data)
    response = app.response_class(status=200,mimetype="application/json",response=data)

    return response

app.run(host="0.0.0.0")
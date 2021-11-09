"""
Author: Sophie Hospel
Date: 03-11-2021
Script for calling SkyScanner API
"""

import requests
import json


def parse_to_json(flight_info):
    """
    Maakt hoofdkopje vlucht aan. Per gevonden informatie benoemd de functie
    de waardes die in de informatie staan in JSON format. 
    """
    
    parsed_string = '{"vlucht":['

    for vluchtid, information in flight_info.items():
        parsed_string += '{'
        parsed_string += '"vluchtid":"{}", '.format(vluchtid)
        parsed_string += '"vluchtvertrektijd":"{}", '.format(information[1])
        parsed_string += '"vluchtaankomsttijd":"{}", '.format(information[2])
        parsed_string += '"vluchtduur":"{}", '.format(information[3])
        parsed_string += '"vluchtprijs":"{}", '.format(information[0])
        parsed_string += '"vliegmaatschappij":"{}", '.format(information[4])
        parsed_string += '"vliegveldheen":"{}", '.format(information[5])
        parsed_string += '"vliegveldterug":"{}"'.format(information[6])
        parsed_string += '},'
    
    
    parsed_string = parsed_string.rstrip(',')
    parsed_string += ']}'

    return parsed_string
    

def get_flight_places(originplace, destinationplace, places):
    """
    Kijkt naar de 3-letter afkorting wat staat voor vertrekplek en bestemmingplek
    waar deze afkorting opgeslagen staat in de lijst places. Met de afkorting
    kan uit de lijst de volledige naam worden gehaald. Deze worden returned. 
    """
    originplacename = ""
    destinationplacename = ""

    for pl in places:
        if pl["Id"] == int(originplace):
            originplacename = pl["Name"]
        elif pl["Id"] == int(destinationplace):
            destinationplacename = pl["Name"]

    return originplacename, destinationplacename


def get_agent_information(carriers, carrierid):
    """
    Kijkt naar het carrierid in de lijst carriers. Als de id's 
    overeenkomen dan wordt de naam van de vluchtmaatschappij gereturnd. 
    """
    
    for i, car in enumerate(carriers):
        if car["Id"] == carrierid:
            return carriers[i]["Name"]


def get_flight_information(legs, outboundlegid):
    """
    Kijkt naar het vluchtid in de lijst legs. Als de vluchtids overeenkomen
    dan wordt in de dictionary (bij de key vluchtid) vertrektijd, aankomsttijd,
    duur, vluchtnummer en carrierid toegevoegd.
    """

    for item in legs:
        if item["Id"] == outboundlegid and item["Directionality"] == "Outbound":
            flight_info = [item["Departure"], item["Arrival"], item["Duration"], item["FlightNumbers"][0]["CarrierId"]]
            return flight_info


def format_information(response_dict, aantalresultaten):
    """
    Eerst worden de benodigde kopjes benoemd vanuit de informatie. 
    Dan wordt er gecheckt of de runstatus oke was. Daarna worden het
    aantal (ingevoerd door gebruiker) vluchtids opgeslagen en de info
    erbij gezocht. 
    """
    flight_info = {}
    error = 2
    query = response_dict["Query"]
    status = response_dict["Status"]
    itineraries = response_dict["Itineraries"] 
    legs = response_dict["Legs"]
    carriers = response_dict["Carriers"]
    places = response_dict["Places"]
    status_ok = ["UpdatesComplete", "UpdatesPending"] # UpdatesPending in dit geval goed want door weergave kijken we niet verder pagina 1.

    if status in status_ok:
        for i in range(int(aantalresultaten)):
            flight_info[itineraries[i]["OutboundLegId"]] = [itineraries[i]["PricingOptions"][0]["Price"]]

        for outboundlegid, lst in flight_info.items():
            info = get_flight_information(legs, outboundlegid)
            lst.extend(info)
            carrierid = lst[-1]
            agency_name = get_agent_information(carriers, carrierid)
            lst.pop(4)
            originplacename, destinationplacename = get_flight_places(query["OriginPlace"], query["DestinationPlace"], places)
            lst.extend([agency_name, originplacename, destinationplacename]) 
            error = 0
            
    return flight_info, error
    

def poll_session(sessionkey, aantalresultaten):
    """
    Call tweede API om resultaten van de vorige call te krijgen. Checkt eerst of 
    er een error in de response is vermeld. Als er geen error is wordt de inhoud 
    opgeslagen als dict.
    """

    url = "http://partners.api.skyscanner.net/apiservices/pricing/v1.0/{0}?apikey=prtl6749387986743898559646983194&pageIndex=0&pageSize={1}".format(sessionkey, aantalresultaten)
    
    response = requests.request("GET", url, headers={}, data={})
    reponse_dict = json.loads(response.text)
    error = 2

    try:
        if reponse_dict["code"]:
            reponse_dict = None
            return {}, error
    except KeyError:
        error = 0
        return reponse_dict, error


def get_sessionkey(reispersonen, land, reisdatumheen, reisbestemming, reisvertrek):
    """
    Call eerste API om sessieid te krijgen. Variabelen worden in deze call meegegeven.
    Checkt eerst of er een error in de response is vermeld. Als er geen error is 
    wordt het sessieid gepakt.
    """

    url = "http://partners.api.skyscanner.net/apiservices/pricing/v1.0"

    payload="cabinclass=Economy&country={1}&currency=EUR&locale=nl-NL&locationSchema=iata&originplace={4}&destinationplace={3}&outbounddate={2}&adults={0}&children=0&infants=0&apikey=prtl6749387986743898559646983194".format(reispersonen, land, reisdatumheen, reisbestemming, reisvertrek)
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    reponse_dict = json.loads(response.text)
    sessionkey = ""
    error = 2
   
    try:
        if reponse_dict["code"]:
            print("Script shut down. Error: {0} {1}".format(reponse_dict["code"], reponse_dict["message"]))
            sessionkey = None

    except KeyError:
        sessionkey = response.headers["Location"].rsplit("/", 1)[1]
        error = 0

    except json.decoder.JSONDecodeError as j :
        print("Script shut down. Error: {}".format(j))
        sessionkey = None
        error = 3
           
    finally:
        return sessionkey, error


def run_skyscannerAPI(reispersonen, land, reisdatumheen, reisbestemming, aantalresultaten, reisvertrek):
    """
    Call functie van het script. Vraagt eerst een sessieid op met de parameters. Bekijkt dan de resultaten
    van het sessieid. Formatteerd de resultaten naar een dict, die daarna naar JSON wordt geparst.
    @param reispersonen: String aantal adults, kinderen worden gerekend als adult in deze code.
    @param land: String land van vertrek, 2 lettercode.
    @param reisdatumheen: String datum vertrek op volgorde YYYY-MM-DD. 
    @param reisbestemming: String plek van bestemming, 3 lettercode.
    @param aantalresultaten: String aantal resultaten die ingeladen mogen worden, hangt snelheid applicatie vanaf.
    @param reisvertrek: String String plek van vertrek, 3 lettercode. 
    @return: JSON format {vlucht:[{vluchtid : [timestamp vertrek, timestamp aankomst, duur (in minuten), prijs (in euro), vliegmaatschappij, vertrekplek, aankomstplek]}]}
    """
    
    sessionkey, error = get_sessionkey(reispersonen, land, reisdatumheen, reisbestemming, reisvertrek)
    if error == 0:
            response_dict, error = poll_session(sessionkey, aantalresultaten)
            if error == 0:
                flight_info, error = format_information(response_dict, aantalresultaten)
                if error == 0:
                    flight_json = parse_to_json(flight_info)
                    return flight_json, error
                else:
                    return None, error
            else:
                return None, error
    else:
        print("Script shut down. Error in sessionkey")
        return None, error

result_heen = run_skyscannerAPI(reispersonen="1", land="NL", reisdatumheen="2022-05-29", reisbestemming="BER", aantalresultaten="10", reisvertrek="AMS")
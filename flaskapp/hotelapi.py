"""
Script for calling Hotel API
Auteur: Anoek
Datum: 05-11-2021
"""

import requests
import sys



def hotelapi(maxopties, reiscodlat, reiscodlong):
    """
    hotelapi geeft voor #maxopties en een locatie (latitude/longitude) voor de beschikbare hotels; hotelid, hotelnaam, hoteladres, hotelincheck, hoteluitcheck. 
    @param maxopties: integer, ingegeven door user (meer hierover in main.py)
    @param reiscodlat: user geeft stad op, uit dictionary worden zowel latitude als longitude gehaald
    @param reiscodlong: user geeft stad op, uit dictionary worden zowel latitude als longitude gehaald
    @return: return geeft status code en indien mogelijk hotelid, hotelnaam, hoteladres, hotelincheck, hoteluitcheck

    """
    

    url = "https://sandbox.impala.travel/v1/hotels?latitude="+reiscodlat+"&longitude="+reiscodlong+"&radius=10000&size="+str(maxopties)  

    payload={}
    headers = {'X-API-KEY': 'sandb_rwo663jBUtmUfsKuiW4N7GHpY4iCgiOaKxOQMiFM'}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        if response.raise_for_status() == None:

            if response.status_code > 199 and response.status_code <=299:
                status = 0
                hotellijst = []
                hoteldict = {}
                hoteldata = response.json()
                
                for zoekresultaat in (hoteldata)["data"]:
                    hotellijst.append({"hotelId" : zoekresultaat["hotelId"], "hotelnaam" : zoekresultaat["name"].replace(' [SANDBOX]', ''), "hoteladres" : zoekresultaat["address"]["line1"] + ", " + zoekresultaat["address"]["city"],  "hotelInCheck" : zoekresultaat["checkIn"]["from"], "hotelUitCheck" : zoekresultaat["checkOut"]["to"]})
                    hoteldict["hotel"] = hotellijst
                print(hoteldict)
        
            elif response.status_code == 429:
                # too many requests - try again
                status = 4
                hoteldict = []

            else:
                status = 2
                hoteldict = []

            return status, hoteldict

    except requests.exceptions.HTTPError as errh:
        print("Hotel API: Http Error: ", errh, file = sys.stderr)
        hoteldict = []
        status = 1
        return status, hoteldict

    except requests.exceptions.ConnectionError as errc:
        print("Hotel API: Connection Error: ", errc, file = sys.stderr)
        hoteldict = []
        status = 1
        return status, hoteldict

    except requests.exceptions.Timeout as errt:
        print("Hotel API: Timeout Error: ", errt, file = sys.stderr)
        hoteldict = []
        status = 1
        return status, hoteldict
            
    except requests.exceptions.RequestException as err:
        print ("Hotel API: Oops: Error in connection",err, file = sys.stderr)  
        hoteldict = []     
        status = 1
        return status, hoteldict
        

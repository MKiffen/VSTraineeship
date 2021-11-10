import requests
import json
from datetime import datetime
import sys
import syslog
syslog.openlog()

class NsTrip: # duidelijke uitleg
    """
    Class to represent a NS train trip 
    Attributes: 
        - String: fromStationCode:          NS Station code of departure station
        - String: toStationCode:            NS Station code of arrival station
        - String: toStation:                NS Station name arrival, format: "Rotterdam_centraal"
        - String: fromStation:              NS Station name departure, format: "Rotterdam_centraal"
        - String: dateTimeArrival:          Date time (RFC 3339 format) of wanted arrival time
        - String: tripOptions:              String in JSON format with tripOptions retrieved from the NS API "/reisinformatie-api/api/v3/trips" endpoint. 
                                            format is a nested list with the option parameters: [[idx, duration, transfers, departureTime, arrivalTime, priceInCents, shareUrl, ctxRecon, overstappen]]

    Methods:
        - retrieveTripOptions():    retrieves the trip options from the NS api 
        - retrieveNsStation():      retrieves the ns station code based on the station name
        - getTripOptions():         returns tripoptions into list 
    
    Author: Dennis
    Date: 11-1-2021
    """
        
    def __init__(self, fromStation, toStation, dateTimeArrival):
        """
        parameters:
        - fromStation: String :             NS Station code of departure station
        - toStation:   String :             NS Station code of arrival station
        - dateTime:    dateTimeArrival:     Date time (RFC 3339 format) of wanted arrival time
        """

        #INPUT
        self.fromStation        = fromStation.upper()          
        self.toStation          = toStation.upper()             
        self.dateTimeArrival    = dateTimeArrival      

        
        self.tripOptions        = []                           #List with tripoptions retrieved NS API
        self.fromStationCode    = ""
        self.toStationCode      = ""


    def retrieveNsStation(self):
        """
        retrieves the ns station code of the from and to station based upon the ns station name in the NsTrip object.
        Parameters:
            - NsTrip object

        Output: 
            - nsTrip.toStationCode, NsTrip.fromStation
        """
        #input
        fromStation        = self.fromStation       
        toStation          = self.toStation
        
        #output
        fromStationCode = self.fromStationCode
        toStationCode   = self.fromStationCode

        #local variables
        filePath = "./afkortingennsstations.txt" #path to text file with ns station codes
        codeDict = {}                            #Dictionairy to hold station codes coupled to names
        codeDict_file = open(filePath)           #Opened file

        #Replacing _ with spaces:
        fromStation = fromStation.replace("_", " ")
        toStation = toStation.replace("_", " ")
        
        #Writing afkortingennsstations into Dictionairy
        for line in codeDict_file:
            value, key = line.split(sep=" ", maxsplit = 1)
            codeDict[key.strip().upper()] = value.strip()
        
        #getting station codes from dictionairy based on station names
        try:
            fromStationCode = codeDict[fromStation]
        except:
            errorMessage = "NS_API: Station: '"+ fromStation + "' could not be found, returning with error status"
            print(errorMessage, file = sys.stderr)
            status = 3
            
            return status
        
        try:
            toStationCode   = codeDict[toStation]
        except:
            errorMessage = "NS_API: Station: '"+ toStation + "' could not be found, returning with error status"
            print(errorMessage, file = sys.stderr)
            status = 3
            
            return status
        
        codeDict_file.close() # Closing text file 
        
        self.toStationCode = toStationCode
        self.fromStationCode = fromStationCode
        status = 0
        
        return status

    def retrieveTripOptions(self, maxOptions = 5):   
        """
        Function to retrieve trip options given a NsTrip object. 

        Parameters:
            - NsTrip object
            - int: maxOptions:      Maximal trip options return, defaults to 5

        Output: 
            - status: 
                - 0: Success
                - 1: Connection problem with api
                - 2: No info found
                - 3: Input error, eg. station not found
        """
        status = 0
        status = NsTrip.retrieveNsStation(self)
        
        #Checking if stations could be found in dictionary
        if status != 0:
            return status

        fromStationCode     = self.fromStationCode       
        toStationCode       = self.toStationCode         
        dateTimeArrival     = self.dateTimeArrival   
        tripOptions         = self.tripOptions          #Stores output of tripoptions
        maxOptions          = maxOptions                #Maxium number of trip options to return

        #local varriables:           
        searchForArrival = "True"                       #boolean, If set, the date and time parameters specify the arrival time for the trip search
        reservation = "True"                            #trains for domestic trips that require a reservation (e.g. Thalys)
        travelClass= "2"                                #Class of travel to use when calculating product prices
        travelRequestType = "DEFAULT"                   #Class of travel to use when calculating product prices
         
        url = ""                                        #String to hold url for API
        data = {}                                       #Type of data returned for request
        
        #variables containing API info
        baseurl = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips?"  #Base url of API gateway
        headers = {'Ocp-Apim-Subscription-Key': 'bdb0eee46b7e420f9955de70b01bcd02'}   #Application key, added as argument to request
        
        #code
        #Base string with arguments to pass to the base url:
        
        argumentString =    "lang=nl"\
                            "&fromStation={fromStation}"\
                            "&toStation={toStation}"\
                            "&dateTime={dateTimeArrival}"\
                            "&searchForArrival={searchForArrival}"\
                            "&excludeTrainsWithReservationRequired={reservation}"\
                            "&travelClass={travelClass}"\
                            "&travelRequestType={travelRequestType}"
        
        #filling in arguments with the variables
        dateTimeArrival = dateTimeArrival.replace(" ", "T")
        argumentString = argumentString.format(fromStation      = fromStationCode,
                                               toStation        = toStationCode,
                                               dateTimeArrival  = dateTimeArrival,
                                               searchForArrival = searchForArrival,
                                               reservation      = reservation,
                                               travelClass      = travelClass,
                                               travelRequestType= travelRequestType
                                             )
        
        #Concatting baseurl with argument string 
        url = baseurl + argumentString
        print(url, file = sys.stderr)
        #retrieving trip from NS:
        try:
            response = requests.request("GET", url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print ("NS API: Http Error:",errh, file = sys.stderr)
            status = 1
            return status
        
        except requests.exceptions.ConnectionError as errc:
            print ("NS API: Error Connecting:",errc, file = sys.stderr)
            status = 1
            return status

        except requests.exceptions.Timeout as errt:
            print ("NS API: Timeout Error:",errt, file = sys.stderr)
            status = 1
            return status 

        except requests.exceptions.RequestException as err:
            print ("NS API: OOps: Error in connection",err, file = sys.stderr)
            status = 1
            return status 

        tripOptionsJson = json.loads(response.text)
        tripOptionsJson, status = NsTrip.checkKey(dictionary=tripOptionsJson, keys =['trips'], elseValue = None, criticalError = True)
        
        #Check if trips have been found:
        if status != 0:
            status = 2
            return status
        
        #Filtering on wanted information per trip option:
        for index, option in zip(range(maxOptions), tripOptionsJson):
            if index == maxOptions:
                break
            
            tripOption = {} #Dict to store trip option info
            tripOption['idx']               =   NsTrip.checkKey(dictionary=option, keys =['idx'], elseValue = None)[0]
            tripOption['ctxRecon']          =   NsTrip.checkKey(dictionary=option, keys =['ctxRecon'], elseValue = None)[0]
            tripOption['duur']              =   NsTrip.checkKey(dictionary=option, keys =['plannedDurationInMinutes'], elseValue = None)[0]
            tripOption['aantalOverstapen']  =   NsTrip.checkKey(dictionary=option, keys =['transfers'], elseValue = None)[0]
            tripOption['url']               =   NsTrip.checkKey(dictionary=option, keys =['shareUrl', 'uri'], elseValue = None)[0]
            tripOption['prijsInCenten']     =   NsTrip.checkKey(dictionary=option, keys =['fares', 1, 'priceInCents'], elseValue = None)[0]
            
            #getting deparure time and arrival time from ctxReconList:
            ctxReconList = option['ctxRecon'].split(sep ="|")
            
            departureTime               = ctxReconList[3].split("=", maxsplit = 2)[1]
            tripOption["vertrekTijd"]   = datetime.fromisoformat(departureTime)

            arrivalTime                 = ctxReconList[4].split("=", maxsplit = 2)[1]
            tripOption['aankomstTijd']  = datetime.fromisoformat(arrivalTime)
            
            #Filtering relevant information from legs:
            legs = NsTrip.checkKey(dictionary=option, keys =['legs'], elseValue = None)[0]
            
            if legs != None:
                overstappen = NsTrip.filterLegs(option['legs'])    
                tripOption["overstappen"] = overstappen
            
            else:
                print("Warning, NS_API: Overstappen not found, assing null value", file = sys.stderr)

            #Adding tripOption to the tripOptions
            tripOptions.append(tripOption)
        
        tripOptions = {'trein': tripOptions}
        self.tripOptions = tripOptions
        status = 0
        return status

    def getTripOptions(self):
        """
        Function to retrieve trip options for NS trip

        Input:
        - NsTrip object 
        
        Output: 
        - Array: tripOptions: 
             format is a nested list with the option parameters: [[idx, duration, transfers, departureTime, arrivalTime, priceInCents, shareUrl, ctxRecon]]
        """
        tripOptions = self.tripOptions 
        return tripOptions

    def filterLegs(legsJson):
        """
        Function to retrieve relevant information from the raw legs object returned by NS API. 
        
        Input:
            - legs Json object returned by the NS API
        
        Output: 
            - Dict with relevant info of the legs:
                "overstappen": 
                [
                    {
                        "vertrekStation": "Breda-Prinsenbeek",
                        "vertrekPerron": "2",
                        "vertekTijd": "2021-11-29T13:16:00+0100",
                        "treinCode": "SPR 6644",
                        "richting": "Arnhem Centraal",
                        "aankomstStation": "Breda",
                        "aankomstPerron": "6",
                        "aankomstTijd": "2021-11-29T13:21:00+0100"
                    }
                ]
        """
        overstappen = []
 
        for leg in legsJson:
            overstap = {}
            overstap["vertrekStation"]      = NsTrip.checkKey(dictionary=leg, keys =['origin','name'], elseValue = None)[0]
            overstap["vertrekPerron"]       = NsTrip.checkKey(dictionary=leg, keys =['origin','plannedTrack'], elseValue = None)[0]
            overstap["vertekTijd"]          = NsTrip.checkKey(dictionary=leg, keys =['origin','plannedDateTime'], elseValue = None)[0]
            overstap["treinCode"]           = NsTrip.checkKey(dictionary=leg, keys =['name'], elseValue = None)[0]
            overstap["richting"]            = NsTrip.checkKey(dictionary=leg, keys =['direction'], elseValue = None)[0]
            overstap['aankomstStation']     = NsTrip.checkKey(dictionary=leg, keys =['destination', 'name'], elseValue = None)[0]
            overstap['aankomstPerron']      = NsTrip.checkKey(dictionary=leg, keys =['destination','plannedTrack'], elseValue = None)[0]
            overstap['aankomstTijd']        = NsTrip.checkKey(dictionary=leg, keys =['destination','plannedDateTime'], elseValue = None)[0]
        
            #save overstap in overstappen
            overstappen.append(overstap)
        
        return overstappen
    
    def checkKey(dictionary, keys = [], elseValue = None, criticalError = False):
        """
        Function to check if key is in dictionary. if true it returns the value, else it returns the elseValue and logs a warning message.
        input:
            - dict: Dictionary: Dictionary to check keys in 
            - array: keys: array of key and optional subkeys to check, e.g. to check keys in dict[key1][key2], the correct input is [key1, key2]
            - elseValue: value to return when key is not present, can be of any type
            - bolean: critical error: when True error status 2 is returned, and error message instead of warning is printed, defaults on False
        
        Output: 
            - When key found: value of key in dict, status (int)
            - when key not found: elseValue, status
        """
        status = 0                              # Int to store status in, 0 = succesfull 
        keys   = keys                           # Array of keys to check in dictionary 
        dictionary = dictionary                 # Dictionary to check keys in
        elseValue  = elseValue                  # value to return when key not found 

        #Local 
        subDictionary = dictionary              # dict to store subdictionary 
        previousSubDictionary = subDictionary   # dict to store previous subdictionary in 
        
        syslog.syslog("Checking if key is found in data NS")

        for key in keys:
            try:
                previousSubDictionary = subDictionary
                subDictionary = subDictionary[key]
            except: 
                if criticalError == True:
                    errorMessage = "ERROR NS_API: Key: '"+ str(key) + "' not found in data, assigning: '" + str(elseValue) + "' instead."
                    print(errorMessage, file = sys.stderr)
                    status = 2
                    return elseValue, status

                else:
                    warningMessage = "NS_API: Key: '"+ str(key) + "' not found in data, assigning: '" + str(elseValue) + "' instead"
                    print(warningMessage, file = sys.stderr)
                    syslog.syslog(syslog.LOG_WARNING, warningMessage )
                
                    return elseValue, status
        
        result = previousSubDictionary[keys[-1]]

        return result, status
    
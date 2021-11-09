"""
Script for parsing JSON format to HTML format. 
Auteur: Sophie Hospel
Datum: 09-11-2021
"""

def parse(jsonobj):
    """
    TO DO: Omzetten naar recursieve functie ipv al de loopjes in geneste structuur.
    Kijkt in JSON dict naar plaatsing in HTML format.
    """

    # jsonobj = {'reis': [{'heenreis': [{'vlucht': [{'vluchtid': '9451-2205300945--31799,-32544-2-9828-2205301615', 'vluchtvertrektijd': '2022-05-30T09:45:00', 'vluchtaankomsttijd': '2022-05-30T16:15:00', 'vluchtduur': '390', 'vluchtprijs': '438.54', 'vliegmaatschappij': 'SWISS', 'vliegveldheen': 'Amsterdam', 'vliegveldterug': 'Berlijn'}, {'vluchtid': '9451-2205301645--32132-0-9828-2205301800', 'vluchtvertrektijd': '2022-05-30T16:45:00', 'vluchtaankomsttijd': '2022-05-30T18:00:00', 'vluchtduur': '75', 'vluchtprijs': '76.27', 'vliegmaatschappij': 'KLM', 'vliegveldheen': 'Amsterdam', 'vliegveldterug': 'Berlijn'}]}, {'trein': [{'idx': 0, 'ctxRecon': 'arnu|fromStation=8400621|toStation=8400561|plannedFromTime=2021-11-09T11:26:00+01:00|plannedArrivalTime=2021-11-09T11:58:00+01:00|yearCard=false|excludeHighSpeedTrains=false|searchForAccessibleTrip=false', 'duur': 32, 'aantalOverstapen': 0, 'url': 'https://www.ns.nl/rpx?ctx=arnu%7CfromStation%3D8400621%7CtoStation%3D8400561%7CplannedFromTime%3D2021-11-09T11%3A26%3A00%2B01%3A00%7CplannedArrivalTime%3D2021-11-09T11%3A58%3A00%2B01%3A00%7CyearCard%3Dfalse%7CexcludeHighSpeedTrains%3Dfalse%7CsearchForAccessibleTrip%3Dfalse', 'prijsInCenten': 950, 'vertrekTijd': 'Tue, 09 Nov 2021 10:26:00 GMT', 'aankomstTijd': 'Tue, 09 Nov 2021 10:58:00 GMT', 'overstappen': [{'vertrekStation': 'Utrecht Centraal', 'vertrekPerron': '5', 'vertekTijd': '2021-11-09T11:26:00+0100', 'treinCode': 'IC 3134', 'richting': 'Schiphol Airport', 'aankomstStation': 'Schiphol Airport', 'aankomstPerron': '4', 'aankomstTijd': '2021-11-09T11:58:00+0100'}]}, {'idx': 1, 'ctxRecon': 'arnu|fromStation=8400621|toStation=8400561|plannedFromTime=2021-11-09T11:41:00+01:00|plannedArrivalTime=2021-11-09T12:10:00+01:00|yearCard=false|excludeHighSpeedTrains=false|searchForAccessibleTrip=false', 'duur': 29, 'aantalOverstapen': 0, 'url': 'https://www.ns.nl/rpx?ctx=arnu%7CfromStation%3D8400621%7CtoStation%3D8400561%7CplannedFromTime%3D2021-11-09T11%3A41%3A00%2B01%3A00%7CplannedArrivalTime%3D2021-11-09T12%3A10%3A00%2B01%3A00%7CyearCard%3Dfalse%7CexcludeHighSpeedTrains%3Dfalse%7CsearchForAccessibleTrip%3Dfalse', 'prijsInCenten': 950, 'vertrekTijd': 'Tue, 09 Nov 2021 10:41:00 GMT', 'aankomstTijd': 'Tue, 09 Nov 2021 11:10:00 GMT', 'overstappen': [{'vertrekStation': 'Utrecht Centraal', 'vertrekPerron': '7', 'vertekTijd': '2021-11-09T11:41:00+0100', 'treinCode': 'IC 3536', 'richting': 'Schiphol Airport', 'aankomstStation': 'Schiphol Airport', 'aankomstPerron': '4', 'aankomstTijd': '2021-11-09T12:10:00+0100'}]}]}], 'reisid': 47}, {'terugreis': [{'vlucht': [{'vluchtid': '9828-2206022030--32677-1-9451-2206030945', 'vluchtvertrektijd': '2022-06-02T20:30:00', 'vluchtaankomsttijd': '2022-06-03T09:45:00', 'vluchtduur': '795', 'vluchtprijs': '141.16', 'vliegmaatschappij': 'Air France', 'vliegveldheen': 'Berlijn', 'vliegveldterug': 'Amsterdam'}, {'vluchtid': '9828-2206020830--32480-1-9451-2206021405', 'vluchtvertrektijd': '2022-06-02T08:30:00', 'vluchtaankomsttijd': '2022-06-02T14:05:00', 'vluchtduur': '335', 'vluchtprijs': '186.0', 'vliegmaatschappij': 'British Airways', 'vliegveldheen': 'Berlijn', 'vliegveldterug': 'Amsterdam'}]}, {'trein': [{'idx': 0, 'ctxRecon': 'arnu|fromStation=8400561|toStation=8400621|plannedFromTime=2021-11-09T11:19:00+01:00|plannedArrivalTime=2021-11-09T11:48:00+01:00|yearCard=false|excludeHighSpeedTrains=false|searchForAccessibleTrip=false', 'duur': 29, 'aantalOverstapen': 0, 'url': 'https://www.ns.nl/rpx?ctx=arnu%7CfromStation%3D8400561%7CtoStation%3D8400621%7CplannedFromTime%3D2021-11-09T11%3A19%3A00%2B01%3A00%7CplannedArrivalTime%3D2021-11-09T11%3A48%3A00%2B01%3A00%7CyearCard%3Dfalse%7CexcludeHighSpeedTrains%3Dfalse%7CsearchForAccessibleTrip%3Dfalse', 'prijsInCenten': 950, 'vertrekTijd': 'Tue, 09 Nov 2021 10:19:00 GMT', 'aankomstTijd': 'Tue, 09 Nov 2021 10:48:00 GMT', 'overstappen': [{'vertrekStation': 'Schiphol Airport', 'vertrekPerron': '3', 'vertekTijd': '2021-11-09T11:19:00+0100', 'treinCode': 'IC 3539', 'richting': 'Helmond', 'aankomstStation': 'Utrecht Centraal', 'aankomstPerron': '18', 'aankomstTijd': '2021-11-09T11:48:00+0100'}]}, {'idx': 1, 'ctxRecon': 'arnu|fromStation=8400561|toStation=8400621|plannedFromTime=2021-11-09T11:32:00+01:00|plannedArrivalTime=2021-11-09T12:04:00+01:00|yearCard=false|excludeHighSpeedTrains=false|searchForAccessibleTrip=false', 'duur': 32, 'aantalOverstapen': 0, 'url': 'https://www.ns.nl/rpx?ctx=arnu%7CfromStation%3D8400561%7CtoStation%3D8400621%7CplannedFromTime%3D2021-11-09T11%3A32%3A00%2B01%3A00%7CplannedArrivalTime%3D2021-11-09T12%3A04%3A00%2B01%3A00%7CyearCard%3Dfalse%7CexcludeHighSpeedTrains%3Dfalse%7CsearchForAccessibleTrip%3Dfalse', 'prijsInCenten': 950, 'vertrekTijd': 'Tue, 09 Nov 2021 10:32:00 GMT', 'aankomstTijd': 'Tue, 09 Nov 2021 11:04:00 GMT', 'overstappen': [{'vertrekStation': 'Schiphol Airport', 'vertrekPerron': '3', 'vertekTijd': '2021-11-09T11:32:00+0100', 'treinCode': 'IC 3141', 'richting': 'Nijmegen', 'aankomstStation': 'Utrecht Centraal', 'aankomstPerron': '19', 'aankomstTijd': '2021-11-09T12:04:00+0100'}]}]}]}, {'hotel': [{'hotelId': '8f2d2c3c-7827-47e3-ac9d-ad5e39516439', 'hotelInCheck': '15:00', 'hotelUitCheck': '11:00', 'hoteladres': 'Grünberger Strasse 54, Berlin', 'hotelnaam': 'Sketch Rooms & Apartments'}, {'hotelId': 'f4c52e6f-3a25-402c-a76d-cff124ed00ea', 'hotelInCheck': '15:00', 'hotelUitCheck': '11:00', 'hoteladres': 'Belforter Str. 24, Berlin', 'hotelnaam': 'Belfort Rooms & Apartments'}]}], 'reisid':47}
    
    i = 0
    reisinfo = ['heenreis', 'terugreis']

    result = "<TABLE border='1'>"
    result += "<TR><TD>Algemeen</TD><TD>Vlucht</TD><TD>Trein</TD></TR>"

    for key in jsonobj['reis']:
        result += '<TR>'
        for k,v in key.items():
            if k in reisinfo:
                result += "<TD>{}</TD>".format(k)
                for j in v:
                    ta = ""
                    for m, n in j.items():
                        for q in n:
                            for naam, antwoord in q.items():
                                ta += str(naam) + " : " + str(antwoord) + "<br><br>"
                    result += "<TD>{}</TD>".format(ta)
                result += "</TR>"
                break
            elif k == 'hotel':
                to_add = ""
                for item in v:
                    for naam, antwoord in item.items():
                        to_add += str(naam) + " : " + str(antwoord) + "<br><br>"
                result += "<TD>{}</TD><TD>{}</TD>".format(k,to_add)

   
    result += "<TR><TD>{}</TD><TD>{}</TD></TR>".format('reisid', jsonobj['reisid'])
    result += "</TABLE>"

    return result
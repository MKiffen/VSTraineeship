import mysql.connector as mysql
import sys
from datetime import datetime 
import time

class db_interactions():
    def trySqlConn(N=10,s=1, host = 'db', user='root', password = "test_pass",database='booking' ):
        """
        Function to try to make sql connection, retries db_interaction N times with waiting time s.
        Input:
            N: int: number of attempts before system exit, defaults to 10
            s: int: number of seconds to wait between each attempt, defaults to 10
        
        output:
            - status:
                - 0: connection made
                - 1: connection error
            - sqlconnection: mysql.connector.connect
        """
        retries = N     # Number of times to retry making connection 
        wait_time = s   # Number of seconds to wait between tries      
        
        counter = 1
        status = 1
        while status>0 and counter<(retries+1):
            print("Trying to connect to database, attempt number: ", str(counter), file = sys.stderr)
            conn, status = db_interactions.sqlConnect()
            if status == 0:
                break
            time.sleep(wait_time)
            counter += 1  
        if status !=0:
            print("Could not connect with database", file = sys.stderr)

        return conn, status
    
    def sqlCheckConn(conn):
        try:
            connected = conn.is_connected()
        except Exception as ex:
            print("SQL DB: Error in connecting to database: ", ex, file = sys.stderr)
            status = 1
            return status
        
        if connected == True:
            status = 0
            return status
        else:
            print("SQL DB: Error in connecting to database", file = sys.stderr)
            status = 1
            return status



    def sqlConnect(host = 'db', user='root', password = "test_pass",database='booking'):
        """
        Function to check connection to sql database and return it.
        Input:
            - string: host
            - string: user
            - string: password 
            - string: database
        
        Output: 
            - status:
                - 0: connection made
                - 1: connection error
            - sqlconnection: mysql.connector.connect
        
        Also prints error message to terminal if needed.
        """
        #Variables input
        host     = host             #Host to connect to 
        user     = user             #username to use with login     
        password = password         #password coupled to user 
        database = database         #database to open

        #Variables output 
        status = 0                  #Int to store and return status, 0 = successful connection, 1 = connection error

        try:
            connection = mysql.connect(host = 'db', user='root', password = "test_pass",database='booking')
            status =   db_interactions.sqlCheckConn(connection)
        except Exception as ex:
            print("SQL DB: Error in connecting to database: ", ex, file = sys.stderr)
            status = 1
            return None, status
        
        if status == 0:
            return connection, status
        else:
            print("SQL DB: Error in connecting to database", file = sys.stderr)
            status = 1
            return None, status

    ############# SELECT QUERIES #################
    def selectFromHotel(connection_database, reis_id):
        """
        Function to retrieve info from the Hotel table in the booking database. 

        Input:
            - connection_database: mysql.connector.connect object: initialized connection with booking database 
            - reis_id: int: primary key from REIS tabel
        
        Output:
            - dataIsFound: bolean: True if data is found, False when not 
            - hotelData: list[dict]: List of dictionaries per hotel found (with matching reis_id) 
        """

        cnx     = connection_database      # mysql.connector.connect object
        reis_id  = reis_id                   # primary key from REIS table
        hotelData = []                     # list to store output
        #Local variables 
        cursor  = cnx.cursor(buffered = True)             #Cursor from connect object
        query   = ""                       #String var to store query
        dataIsFound = False                #Bolean if data is found

        #Defining the main query:
        query = ("SELECT * FROM HOTEL WHERE reis_id = {reis_id}")
        query = query.format(reis_id = reis_id)

        cursor.execute(query)

        #Checking if data is present:
        if cursor.rowcount == 0:
            dataIsFound = False
            return dataIsFound, None

        for row in cursor:
            hotel = {}
            hotel["id"]         = row[0]
            hotel["naam"]       = row[1]
            hotel["adres"]      = row[2]
            hotel["incheck"]    = row[3]
            hotel["uitcheck"]   = row[4]
            hotel["externid"]   = row[5]
            
            hotelData.append(hotel)
        dataIsFound = True
        cursor.close()
        return dataIsFound, {"hotels": hotelData}

    def selectFromNs(connection_database, reis_id):
        """
        Function to retrieve info from the NS table in the booking database. 

        Input:
            - connection_database: mysql.connector.connect object: initialized connection with booking database 
            - reis_id: int: primary key from REIS tabel
        
        Output:
            - dataIsFound: bolean: True if data is found, False when not 
            - nsData: list[dict]: List of dictionaries per Ns found (with matching reis_id) 
        """

        cnx     = connection_database      # mysql.connector.connect object
        reis_id  = reis_id                   # primary key from REIS table
        NsData  = []                        # list to store output
        
        #Local variables 
        cursor  = cnx.cursor(buffered=True) #Cursor from connect object
        query   = ""                        #String var to store query
        dataIsFound = False                 #Bolean if data is found

        #Defining the main query:
        query = ("SELECT * FROM NS WHERE reis_id = {reis_id}")
        query = query.format(reis_id = reis_id)

        cursor.execute(query)

        #Checking if data is present:
        if cursor.rowcount == 0:
            dataIsFound = False
            return dataIsFound, None

        for row in cursor:
            Ns = {}
            Ns["id"]         = row[0]
            Ns["vertrektijd"]       = row[1]
            Ns["aankomsttijd"]      = row[2]
            Ns["duur"]              = row[3]
            Ns["overstappen"]       = row[4]
            Ns["prijs"]             = row[5]
            
            NsData.append(Ns)
        dataIsFound = True
        cursor.close()
        return dataIsFound, {"Ns": NsData}

    def selectFromVlucht(connection_database, reis_id):
        """
        Function to retrieve info from the Vlucht table in the booking database. 

        Input:
            - connection_database: mysql.connector.connect object: initialized connection with booking database 
            - reis_id: int: primary key from REIS tabel
        
        Output:
            - dataIsFound: bolean: True if data is found, False when not 
            - VluchtData: list[dict]: List of dictionaries per vlucht found (with matching reis_id) 
        """

        cnx     = connection_database      # mysql.connector.connect object
        reis_id  = reis_id                   # primary key from REIS table
        vluchtData  = []                        # list to store output
        
        #Local variables 
        cursor  = cnx.cursor(buffered=True) #Cursor from connect object
        query   = ""                        #String var to store query
        dataIsFound = False                 #Bolean if data is found

        #Defining the main query:
        query = ("SELECT * FROM VLUCHT WHERE reis_id = {reis_id}")
        query = query.format(reis_id = reis_id)

        cursor.execute(query)

        #Checking if data is present:
        if cursor.rowcount == 0:
            dataIsFound = False
            return dataIsFound, None

        for row in cursor:
            vlucht = {}
            vlucht["id"]                = row[0]
            vlucht["vertrektijd"]       = row[1]
            vlucht["aankomsttijd"]      = row[2]
            vlucht["duur"]              = row[3]
            vlucht["prijs"]             = row[4]
            vlucht["maatschappij"]      = row[5]
            vlucht["aankomstvliegveld"] = row[6]
            vluchtData.append(vlucht)
        dataIsFound = True
        cursor.close()
        
        return dataIsFound, {"vlucht": vluchtData}

    def selectFromReis(connection_database, reis_id):
        """
        Function to retrieve info from the Vlucht table in the booking database. 

        Input:
            - connection_database: mysql.connector.connect object: initialized connection with booking database 
            - reis_id: int: reis_id key from REIS tabel #####WHAT IS THE BUSINESS KEY#####
        
        Output:
            - dataIsFound: bolean: True if data is found, False when not 
            - reis_id: int:  
        """

        cnx     = connection_database      # mysql.connector.connect object
        reis_id  = reis_id                 # primary key from REIS table
        
        #Local variables 
        cursor  = cnx.cursor(buffered=True) #Cursor from connect object
        query   = ""                        #String var to store query
        dataIsFound = False                 #Bolean if data is found
        reisData = []

        #Defining the main query:
        query = ("SELECT * FROM REIS WHERE reis_id = {reis_id}")
        query = query.format(reis_id = reis_id)

        cursor.execute(query)

        #Checking if data is present:
        if cursor.rowcount == 0:
            dataIsFound = False
            return dataIsFound, None
        
        for row in cursor:
            reis = {}
            reis["id"]                = row[0]
            reis["vertrekstation"]    = row[1]
            reis["bestemming"]        = row[2]
            reis["vertrekvliegveld"]  = row[3]
            reis["datumheen"]         = row[4]
            reis["datumterug"]        = row[5]
            reis["personen"]          = row[6]
            reis["querytimestamp"]    = row[7]
            reisData.append(reis)

        dataIsFound = True
        cursor.close()

        return dataIsFound, reisData

    def getDataFromDb(connection_database, reis_id):
        """
        - reis_id: int: reis_id key from REIS tabel #####WHAT IS THE BUSINESS KEY#####
        """
        
        dataIsFound, reisData = db_interactions.selectFromReis(connection_database, reis_id)
        dataIsFoundHotel = False
        dataIsFoundNs = False
        dataIsFoundVlucht = False
        
        if dataIsFound == True:
            dataIsFoundHotel, hotelData = db_interactions.selectFromHotel(connection_database, reis_id)
            dataIsFoundNs, nsData       = db_interactions.selectFromNs(connection_database, reis_id)
            dataIsFoundVlucht, vluchtData   = db_interactions.selectFromVlucht(connection_database, reis_id)

            if dataIsFoundHotel == True & dataIsFoundNs == True & dataIsFoundVlucht == True:
                dataIsFound = True
                data =data = {"query_result": {"reis":reisData,"hotel":hotelData, "ns":nsData, "vlucht":vluchtData}}
                return dataIsFound, data
            else:
                dataIsFound = False
                data = None
                return dataIsFound, data
        else:
            data = None
            return dataIsFound, data

    ###INSERT STATEMENTS###

    def insertInformation(conn, resultaat, op_te_slaan_reis_db):

        reisid = db_interactions.insertintotabelreis(conn, op_te_slaan_reis_db)

        for i in range(len(resultaat["reis"][0]["heenreis"][0]["vlucht"])):
            db_interactions.insertintotabelvlucht(conn, reisid, resultaat["reis"][0]["heenreis"][0]["vlucht"][i]) 
        for i in range(len(resultaat["reis"][1]["terugreis"][0]["vlucht"])):
            db_interactions.insertintotabelvlucht(conn, reisid, resultaat["reis"][1]["terugreis"][0]["vlucht"][i])
    
        for i in range(len(resultaat['reis'][0]['heenreis'][1]['trein'])):
            db_interactions.insertintotabelns(conn, reisid, resultaat['reis'][0]['heenreis'][1]['trein'][i])
        for i in range(len(resultaat['reis'][1]['terugreis'][1]['trein'])):
            db_interactions.insertintotabelns(conn, reisid, resultaat['reis'][0]['heenreis'][1]['trein'][i])
        
        for i in range(len(resultaat['reis'][2]['hotel'])):
            db_interactions.insertintotabelhotel(conn, reisid, resultaat['reis'][2]['hotel'][i])
        
        return reisid

    def insertintotabelreis(conn, reisinfo):
        reisinfo = reisinfo + (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)

        mycursor = conn.cursor(buffered=True)

        sql = "INSERT INTO REIS(reis_vertrekstation,reis_bestemming,reis_vertrekvliegveld,reis_datumheen,reis_datumterug,reis_personen,reis_querytimestamp)VALUES(%s, %s, %s,%s,%s,%s,%s);"
        val = reisinfo
        mycursor.execute(sql, val)
        conn.commit()
        reisid = mycursor.lastrowid
        mycursor.close()

        return reisid

    def insertintotabelns(conn, reisid, nsinfo):

        mycursor = conn.cursor(buffered=True)

        sql = "INSERT INTO NS (ns_vertrekijd,ns_aankomsttijd,ns_duur,ns_overstappen,ns_prijs,reis_id) VALUES (%s, %s, %s, %s, %s, %s);"
        vertrektijd = nsinfo['vertrekTijd'].split(" ")[4]
        aankomsttijd = nsinfo['aankomstTijd'].split(" ")[4]
        val = (vertrektijd, aankomsttijd,int(nsinfo['duur']),int(nsinfo['aantalOverstapen']),int(nsinfo['prijsInCenten']), reisid)
        mycursor.execute(sql, val)
        conn.commit()
        mycursor.close()

    def insertintotabelvlucht(conn, reisid, vluchtinfo):
        mycursor = conn.cursor(buffered=True)

        sql = "INSERT INTO VLUCHT(vlucht_vertrektijd,vlucht_aankomsttijd,vlucht_duur,vlucht_prijs,vlucht_maatschappij,vlucht_aankomstvliegveld,reis_id)VALUES(%s, %s, %s,%s,%s,%s, %s);"
        val = (vluchtinfo['vluchtvertrektijd'],vluchtinfo['vluchtaankomsttijd'],int(vluchtinfo['vluchtduur']),float(vluchtinfo['vluchtprijs']), vluchtinfo['vliegmaatschappij'],vluchtinfo['vliegveldterug'],reisid)
        mycursor.execute(sql, val)
        conn.commit()
        mycursor.close()


    def insertintotabelhotel(conn, reisid, hotelinfo):
        mycursor = conn.cursor(buffered=True)

        sql = "INSERT INTO HOTEL(hotel_naam,hotel_adres,hotel_incheck,hotel_uitcheck,hotel_externid,reis_id) VALUES (%s, %s, %s,%s,%s, %s);"
        val = (hotelinfo['hotelnaam'],hotelinfo['hoteladres'],hotelinfo['hotelInCheck'],hotelinfo['hotelUitCheck'], hotelinfo['hotelId'], reisid)
        mycursor.execute(sql, val)
        conn.commit()
        mycursor.close()
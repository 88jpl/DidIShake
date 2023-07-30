import json
import requests
import shutil
import threading
import time
import datetime
import urllib.parse
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
# Local Imports
from distance import distance
from features_db import FeaturesDB
from mapHandler import GetGoogleMap
from mapHandler import GeoCoding
from uploadBucket import UploadImage
# import env for global key variables
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

SEND_SMS  = True
INTERVAL = 60
CUTOFF = 7.0
RANKINGINTERVAL = 3600
CANADADEPTH = 30
DAILYTOP = None
DAILYRUNNING = []
MONTLYRUNNING = []
# SMS to be moved to own class then remove this
TEXTAPIKEY = os.environ.get("text-api-token")

ENDPOINT_URL = os.environ.get("do-spaces-endpoint-url")
SPACE =  os.environ.get("do-spaces-space")


SERVERSTARTTIME = time.time()
searchCounter = 0

def requestUSGSData():
        headers = {'Accept': 'application/json'}
        try: 
            # r = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson')
            r = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson')
            # r = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson')
        except requests.exceptions.ConnectionError:
            class ConnectionErrorObject(object):
                pass
            r = ConnectionErrorObject()
            r.status_code = "Connection Refused"
        return r 

def requestCanadaData():
        headers = {'Accept': 'application/json'}
        # format endtime
        currentTime = datetime.datetime.now(datetime.timezone.utc)
        theTime = str(currentTime).split('.')
        pastTime = str(currentTime - datetime.timedelta(days = CANADADEPTH)).split('.')
        endtime = urllib.parse.quote(theTime[0].replace(' ', 'T'))
        # format startime
        startTime = urllib.parse.quote(pastTime[0].replace(' ', 'T'))
        try:
            searchURL = 'https://earthquakescanada.nrcan.gc.ca/fdsnws/event/1/query?endtime={}&eventtype=L&format=text&latitude=63.13&longitude=-90.34&maxdepth=1000&maxlatitude=90&maxlongitude=180&maxmagnitude=10&maxradius=45.04504504504504&mindepth=-5&minlatitude=-90&minlongitude=-180&minmagnitude=-5&minradius=0&nodata=404&onlyfelt=0&starttime={}'.format(endtime, startTime)
            r = requests.get(searchURL)
        except requests.exceptions.ConnectionError:
            class ConnectionErrorObject(object):
                pass
            r = ConnectionErrorObject()
            r.status_code = "Connection Refused"
        return r

def formatCanadaFeatures(response):
    data = response.text
    listOfFeatures = data.split('\n')
    eventsCollection = []
    for i in range(1, len(listOfFeatures)):
        if listOfFeatures[i] == '':
            pass
        else:
            splitFeature = listOfFeatures[i].split('|')
            eventsCollection.append(splitFeature)
            # print(splitFeature)
    # print(eventsCollection)
    return eventsCollection

# Move this to its own class
def sendSMSNotification(message):
    resp = requests.post('https://textbelt.com/text', {
    'phone': '4352184016',
    'message': message,
    'key': TEXTAPIKEY,
    })
    print(resp.json())
    save_printToLog(str(resp.json()), "USGS_DB.txt")

def saveFeatureFromCollectionToDB(collection):
    # CREATE TABLE features (id INTEGER PRIMARY KEY, featureID TEXT, mag REAL, place TEXT, time INTEGER, updated TEXT, tz INTEGER, url TEXT, detail TEXT, felt INTEGER, cdi REAL, mmi REAL, alert TEXT, status TEXT, tsunami INTEGER, sig INTEGER, net TEXT, code TEXT, ids TEXT, sources TEXT, types TEXT, nst INTEGER, dmin REAL, rms REAL, gap REAL, magType TEXT, type TEXT, lat REAL, long REAL, depth REAL);
    DB = FeaturesDB()
    for i in range(collection['metadata']['count']):
        feature = DB.getFeature(collection['features'][i]['id'])
        if feature == None:
            # Properties
            feature = collection['features'][i]['id']
            mag = validateRealForDB(collection['features'][i]['properties']['mag'])
            place = validateTextForDB(collection['features'][i]['properties']['place'])
            eqtime = validateIntForDB(collection['features'][i]['properties']['time'])
            updated = validateIntForDB(collection['features'][i]['properties']['updated'])
            tz = validateIntForDB(collection['features'][i]['properties']['tz'])
            url = validateTextForDB(collection['features'][i]['properties']['url'])
            detail = validateTextForDB(collection['features'][i]['properties']['detail'])
            felt = validateIntForDB(collection['features'][i]['properties']['felt'])
            cdi = validateRealForDB(collection['features'][i]['properties']['cdi'])
            mmi = validateRealForDB(collection['features'][i]['properties']['mmi'])
            alert = validateTextForDB(collection['features'][i]['properties']['alert'])
            status = validateTextForDB(collection['features'][i]['properties']['status'])
            tsunami = validateIntForDB(collection['features'][i]['properties']['tsunami'])
            sig = validateIntForDB(collection['features'][i]['properties']['sig'])
            net = validateTextForDB(collection['features'][i]['properties']['net'])
            code = validateTextForDB(collection['features'][i]['properties']['code'])
            ids = validateTextForDB(collection['features'][i]['properties']['ids'])
            sources = validateTextForDB(collection['features'][i]['properties']['sources'])
            types = validateTextForDB(collection['features'][i]['properties']['types'])
            nst = validateIntForDB(collection['features'][i]['properties']['nst'])
            dmin = validateRealForDB(collection['features'][i]['properties']['dmin'])
            rms = validateRealForDB(collection['features'][i]['properties']['rms'])
            gap = validateRealForDB(collection['features'][i]['properties']['gap'])
            magType = validateTextForDB(collection['features'][i]['properties']['magType'])
            type1 = validateTextForDB(collection['features'][i]['properties']['type'])
            # Geometry
            long = validateRealForDB(collection['features'][i]['geometry']['coordinates'][0])
            lat = validateRealForDB(collection['features'][i]['geometry']['coordinates'][1])
            depth = validateRealForDB(collection['features'][i]['geometry']['coordinates'][2])

            # log message
            seconds = time.time()
            serverTime = time.ctime(seconds)
            save_printToLog("Created new feature: " + feature + " located @ " + place + ". Server time: " + str(serverTime), "USGS_DB.txt")
            print("Created new feature: " + feature + " located @ " + place + ".")
            # Send SMS to user
            if SEND_SMS:
                # Only send if above magnitude cutoff
                if mag >= CUTOFF:
                    # Distance from School
                    distanceFrom = distance(37.101216, -113.568513, lat, long)
                    # old message
                    #sendSMSNotification("A magnitude " + str(mag) + " earthquake happened @ " + place + ".")
                    # Actually send the SMS
                    sendSMSNotification("A magnitude " + str(mag) + " earthquake occured " + str(distanceFrom)  + " miles away.")
                    # print statements for log and one for terminal
                    save_printToLog("A magnitude " + str(mag) + " earthquake occured " + str(distanceFrom)  + " miles away.", "USGS_DB.txt")
                    save_printToLog("Texted feature: " + feature + " it was " + str(mag) +  ".", "USGS_DB.txt")
                    print("Texted feature: " + feature + " it was " + str(mag) +  ".")
                save_printToLog("Didn't text feature: " + feature + " it was " + str(mag) +  ". To Weak!!!", "USGS_DB.txt")
                print("Didn't text feature: " + feature + " it was " + str(mag) +  ". To Weak!!!")
            DB.createNewFeature(feature, mag, place, eqtime, updated, tz, url, detail, felt, cdi, mmi, alert, status, tsunami, sig, net, code, ids, sources, types, nst, dmin, rms, gap, magType, type1, lat, long, depth)
        else:
            print("Feature: " + collection['features'][i]['id'] + " added already!" )

def saveCanadaCollectionToDB(eventsCollection):
    # CREATE TABLE features (id INTEGER PRIMARY KEY, featureID TEXT, mag REAL, place TEXT, time INTEGER, updated TEXT, tz INTEGER, url TEXT, detail TEXT, felt INTEGER, cdi REAL, mmi REAL, alert TEXT, status TEXT, tsunami INTEGER, sig INTEGER, net TEXT, code TEXT, ids TEXT, sources TEXT, types TEXT, nst INTEGER, dmin REAL, rms REAL, gap REAL, magType TEXT, type TEXT, lat REAL, long REAL, depth REAL);
    DB = FeaturesDB()
    for event in eventsCollection:
        feature = DB.getFeature(event[0])
        if feature == None:
            feature = event[0]
            # Properties
            mag = validateRealForDB(float(event[6]))
            place = validateTextForDB(event[7])
            # time needs to be converted from ISO to epoch
            # print("unformatted time: " + event[1])
            utc_dt = datetime.datetime.strptime(event[1], '%Y-%m-%dT%H:%M:%S.%fZ')
            timeStamp = (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()
            # print("timeConverted: " + str(int(timeStamp)*1000))
            eqtime = validateIntForDB(int(timeStamp)*1000)
            updated = validateIntForDB(int(timeStamp)*1000)
            tz = validateIntForDB(None)
            url = validateTextForDB(None)
            detail = validateTextForDB(None)
            felt = validateIntForDB(None)
            cdi = validateRealForDB(None)
            mmi = validateRealForDB(None)
            alert = validateTextForDB(None)
            status = validateTextForDB(None)
            tsunami = validateIntForDB(None)
            sig = validateIntForDB(None)
            net = validateTextForDB(None)
            code = validateTextForDB(None)
            ids = validateTextForDB(None)
            sources = validateTextForDB(None)
            types = validateTextForDB(None)
            nst = validateIntForDB(None)
            dmin = validateRealForDB(None)
            rms = validateRealForDB(None)
            gap = validateRealForDB(None)
            magType = validateTextForDB(event[5])
            type1 = validateTextForDB("earthquake")
            # Geometry
            long = validateRealForDB(float(event[3]))
            lat = validateRealForDB(float(event[2]))
            depth = validateRealForDB(float(event[4]))

            # log message
            seconds = time.time()
            serverTime = time.ctime(seconds)
            save_printToLog("Created new feature: " + feature + " located @ " + place + ". Server time: " + str(serverTime), "USGS_DB.txt")
            print("Created new feature: " + feature + " located @ " + place + ".")
            # Send SMS to user
            if SEND_SMS:
                # Only send if above magnitude cutoff
                if mag >= CUTOFF:
                    # Distance from School
                    distanceFrom = distance(37.101216, -113.568513, lat, long)
                    # old message
                    #sendSMSNotification("A magnitude " + str(mag) + " earthquake happened @ " + place + ".")
                    # Actually send the SMS
                    sendSMSNotification("A magnitude " + str(mag) + " earthquake occured " + str(distanceFrom)  + " miles away.")
                    # print statements for log and one for terminal
                    save_printToLog("A magnitude " + str(mag) + " earthquake occured " + str(distanceFrom)  + " miles away.", "USGS_DB.txt")
                    save_printToLog("Texted feature: " + feature + " it was " + str(mag) +  ".", "USGS_DB.txt")
                    print("Texted feature: " + feature + " it was " + str(mag) +  ".")
                save_printToLog("Didn't text feature: " + feature + " it was " + str(mag) +  ". To Weak!!!", "USGS_DB.txt")
                print("Didn't text feature: " + feature + " it was " + str(mag) +  ". To Weak!!!")
            DB.createNewFeature(feature, mag, place, eqtime, updated, tz, url, detail, felt, cdi, mmi, alert, status, tsunami, sig, net, code, ids, sources, types, nst, dmin, rms, gap, magType, type1, lat, long, depth)
        else:
            print("Feature: " + event[0] + " added already!" )


def validateRealForDB(var):
    if var is None:
        var = 123.456
        return var
    else:
        return var
    
def validateTextForDB(var):
    if var is None:
        var = "NONE"
        return var
    else:
        return var
    
def validateIntForDB(var):
    if var is None:
        var = 00
        return var
    else:
        return var

def getUSGSDataAlways():
    counter = 0
    while(True):
        response = requestUSGSData()
        if response.status_code == 200:   
            saveFeatureFromCollectionToDB(response.json())
            time.sleep(INTERVAL)
            seconds = time.time()
            serverTime = time.ctime(seconds)
            save_printToLog("Retrival: " + str(counter) + " @ " + str(serverTime), "USGS_DB.txt")
            print(counter)
            counter += 1
        else:
            save_printToLog("ERROR: status code - " + str(response.status_code) + " @ " + str(serverTime), "USGS_DB.txt")

def getCanadaDataAlways():
    counter = 0
    while(True):
        response = requestCanadaData()
        # print(response.status_code)
        if response.status_code == 200:   
            collection = formatCanadaFeatures(response)
            saveCanadaCollectionToDB(collection)
            time.sleep(INTERVAL)
            seconds = time.time()
            serverTime = time.ctime(seconds)
            save_printToLog("Retrival: " + str(counter) + " @ " + str(serverTime), "USGS_DB.txt")
            print(counter)
            counter += 1
        else:
            save_printToLog("ERROR: status code - " + str(response.status_code) + " @ " + str(serverTime), "USGS_DB.txt")

def appenedJSONObjectToFile(obj, filename):
    json_object = json.dumps(obj, indent=0)
    with open(filename, 'a') as outp: 
       outp.write(json_object + "\n")

def saveOneJSONObjectToFile(obj, filename):
    json_object = json.dumps(obj, indent=0)
    with open(filename, 'w') as outp: 
       outp.write(json_object + "\n")

def openOneJSONObjectFromFile(filename):
    with open(filename, 'r') as outp:
        data = outp.read()
        jsondata = json.loads(data)
    return jsondata

# print(openOneJSONObjectFromFile("DAILYTOP.txt"))

def save_printToLog(line, filename):
    with open(filename, 'a') as outp: 
       outp.write(line + "\n")

def rankingRefresh():
    # Check if Dailytop stored in file if not try from cached (incase gets erased or reset for the day)
    if os.path.getsize('DAILYTOP.txt') == 0:
        currentTop = DAILYTOP
    else:
        with open('DAILYTOP.txt', 'r') as f:
            data = json.load(f)
            currentTop = data
    # grab features DB and get features from RANKINGINTERVAL length back in time to now
    db = FeaturesDB()
    records = db.getFeaturesFromLast(RANKINGINTERVAL)
    # If no currentTop and no records then pull deeper into DB to get some and perform top comparison
    if currentTop == None and len(records) == 0:
        records = db.getFeaturesFromLast(RANKINGINTERVAL*12)
        for i in range(len(records)):
            if currentTop == None:
                currentTop = records[i]
                currentTop['serverUptime'] = SERVERSTARTTIME - time.time()
            else:
                if currentTop['mag'] <= records[i]['mag']:
                    currentTop = records[i]
                    currentTop['serverUptime'] = SERVERSTARTTIME - time.time()
        return currentTop
    # otherwise go through records and determine if new top
    for i in range(len(records)):
        if currentTop == None:
            currentTop = records[i]
            currentTop['serverUptime'] = SERVERSTARTTIME - time.time()
        else:
            if currentTop['mag'] <= records[i]['mag']:
                DAILYRUNNING.append(currentTop)
                currentTop = records[i]
                currentTop['serverUptime'] = SERVERSTARTTIME - time.time()
    # after getting top feature get map based of only this single feature
    m = GetGoogleMap()
    m = m.featureOnlyMapFromGoogle(currentTop)
    # read map.png from googleStaticMap API into local file
    path = 'public'
    heroImage = 'hero.png'
    with open(heroImage, 'wb') as f:
        m.decode_content = True
        shutil.copyfileobj(m, f)
    # Upload local image
    imageObj = UploadImage()
    imageObj.uploadSingleToSpace(path, heroImage)
    # return top as object
    return currentTop

def saveImageFromAddressSearch(path, fileName, latlong, feature):
    m = GetGoogleMap()
    m = m.locationToFeatureMap(latlong, feature)
    with open(fileName, 'wb') as f:
        m.decode_content = True
        shutil.copyfileobj(m, f)
    # Upload local image
    imageObj = UploadImage()
    imageObj.uploadSingleToSpace(path, fileName)

 
def runRanking():
    open("DAILYTOP.txt", 'w').close()
    counter = 0
    day = date.today().weekday()
    while(True):
        global DAILYRUNNING, DAILYTOP
        if day != date.today().weekday():
            DAILYRUNNING = []
            DAILYTOP = None
            open("DAILYTOP.txt", 'w').close()
            day = date.today().weekday()
        DAILYTOP = rankingRefresh()
        saveOneJSONObjectToFile(DAILYTOP, "DAILYTOP.txt")
        seconds = time.time()
        serverTime = time.ctime(seconds)
        appenedJSONObjectToFile(DAILYTOP, "USGS_DB.txt")
        save_printToLog("Rank Refreshed for the " + str(counter) + " @ " + str(serverTime), "USGS_DB.txt")
        counter += 1
        time.sleep(RANKINGINTERVAL)
        
def getNearestFeatureToAddress(address):
    # Save Searched address to log
    global searchCounter
    str(time.ctime(int(time.time())))
    addressSave = str(searchCounter) + " Searched: " + str(address) + " @ " + str(time.ctime(int(time.time())))
    save_printToLog(addressSave, "searchLogs.txt")
    
    searchCounter += 1
    #convert address received to lat long
    x = GeoCoding()
    latlong = x.addressToLatLong(address)
    # print(latlong)
    lat = latlong[0]
    long = latlong[1]
    totalDepth = 36         #amount of chunks to looks through
    rangePerChunk = 7200    # in seconds
    listOfFeatures = []
    start = 1
    stop = rangePerChunk
    db = FeaturesDB()
    checked = 0
    path = "public"
    for i in range(1, totalDepth+1):
        listOfFeatures = db.getFeaturesFromTo(start, stop * i)
        start += stop
        for feature in listOfFeatures:
            checked += 1
            if feature['mag'] >= 7.0:
                if distance(feature['lat'], feature['long'], lat, long) <= 750.0:
                    tempFileName = int(time.time())
                    tempFileName = str(tempFileName) + ".png"
                    uri = ENDPOINT_URL + "/" + SPACE + "/" + path + "/" + tempFileName
                    saveImageFromAddressSearch(path, tempFileName, latlong, feature)
                    feature['uri'] = uri
                    feature['checked'] = checked
                    feature['distance'] = distance(feature['lat'], feature['long'], lat, long)
                    return feature
            elif feature['mag'] >= 5.5:
                if distance(feature['lat'], feature['long'], lat, long) <= 450.0:
                    tempFileName = int(time.time())
                    tempFileName = str(tempFileName) + ".png"
                    uri = ENDPOINT_URL + "/" + SPACE + "/" + path + "/" + tempFileName
                    saveImageFromAddressSearch(path, tempFileName, latlong, feature)
                    feature['uri'] = uri
                    feature['checked'] = checked
                    feature['distance'] = distance(feature['lat'], feature['long'], lat, long)
                    return feature
            elif feature['mag'] >= 2.5:
                if distance(feature['lat'], feature['long'], lat, long) <= 75.0:
                    tempFileName = int(time.time())
                    tempFileName = str(tempFileName) + ".png"
                    uri = ENDPOINT_URL + "/" + SPACE + "/" + path + "/" + tempFileName
                    saveImageFromAddressSearch(path, tempFileName, latlong, feature)
                    feature['uri'] = uri
                    feature['checked'] = checked
                    feature['distance'] = distance(feature['lat'], feature['long'], lat, long)
                    return feature
            elif feature['mag'] >= 0.1:
                if distance(feature['lat'], feature['long'], lat, long) <= 15.0:
                    tempFileName = int(time.time())
                    tempFileName = str(tempFileName) + ".png"
                    uri = ENDPOINT_URL + "/" + SPACE + "/" + path + "/" + tempFileName
                    saveImageFromAddressSearch(path, tempFileName, latlong, feature)
                    feature['uri'] = uri
                    feature['checked'] = checked
                    feature['distance'] = distance(feature['lat'], feature['long'], lat, long)
                    return feature
    # response = "No Features Nearby! Checked: " + str(checked)
    response = {'lat': 0, 'long': 0, 'checked': checked, 'uri': "test2.png"}
    return response

def convertGeolocationToLatLong(address):
    #convert address received to lat long
    x = GeoCoding()
    latlong = x.addressToLatLong(address)
    # print(latlong)
    return latlong

class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        super().end_headers()

    def handleGetFeatures(self):
        db = FeaturesDB()
        record = db.getFeatures() 
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(record), "utf-8"))

    def handleGetFeatureMember(self, record):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(record), "utf-8"))

    def handleGetFeaturesPresentToDeclared(self, historyTime):
        db = FeaturesDB()
        records = db.getFeaturesFromLast(historyTime)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(records), "utf-8"))

    def handleGetFeaturesFromTo(self, start, stop):
        db = FeaturesDB()
        records = db.getFeaturesFromTo(start, stop)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(records), "utf-8"))

    def handleGetServerUptime(self):
        currentUptime = {}
        currentUptime['serverUptime'] = round(time.time() - SERVERSTARTTIME, 2)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(currentUptime), "utf-8"))


    def handleGetDailyRanking(self):
        record = openOneJSONObjectFromFile("DAILYTOP.txt")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(record), "utf-8"))

    def handelNotAuthorized(self, message):
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def handelNotFound(self, message):
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def handleGetNearest(self, address):
        feature = getNearestFeatureToAddress(address)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(feature), "utf-8"))

    def handleGetGeolocation(self, address):
        feature = convertGeolocationToLatLong(address)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(feature), "utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path_parts = self.path.split('/')
        if len(path_parts) == 3:
            collection_name = path_parts[1]
            address = historyTime = feature_id = path_parts[2]
        else: 
            collection_name = path_parts[1]
            user_email = address = feature_id = None

        if collection_name == 'features':
            if feature_id == None:
                self.handleGetFeatures()
            else:
                db = FeaturesDB()
                record = db.getFeature(feature_id)
                if record != None:
                    self.handleGetFeatureMember(record)
                else:
                    if historyTime.isdigit():
                        self.handleGetFeaturesPresentToDeclared(int(historyTime))
                    else:
                        if ',' in historyTime:
                            listOfHistoryTime = historyTime.split(',')
                            print(listOfHistoryTime)
                            if len(listOfHistoryTime) == 2 and listOfHistoryTime[0].isdigit() and listOfHistoryTime[1].isdigit():
                                self.handleGetFeaturesFromTo(listOfHistoryTime[0], listOfHistoryTime[1])
                            else:
                                self.handelNotFound("Invalid Time formatting!")
                        else:
                            self.handelNotFound("Path not found!")
        elif collection_name == 'locations':
            if address == None or address == "":
                self.handelNotFound("Cant be empty!")
            else:
                self.handleGetNearest(address)
        elif collection_name == 'geos':
            if address == None or address == "":
                self.handelNotFound("Cant be empty!")
            else:
                self.handleGetGeolocation(address)
        elif collection_name == 'rankings':
            if address == None or address =="":
                self.handelNotFound("Cant be empty!")
            elif address == 'daily':
                self.handleGetDailyRanking()
            else:
                self.handelNotFound("Not a Valid Path")
        elif collection_name == 'uptimes':
            if address == None or address =="":
                self.handelNotFound("Cant be empty!")
            elif address == 'server':
                self.handleGetServerUptime()
            else:
                self.handelNotFound("Not a Valid Path")
        # elif collection_name == 'users':
        #     if user_email:
        #         self.handleGetUser(user_email)
        #     else:
        #         self.handle422
        else:
            self.handelNotFound("Path not found!!!!")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    listen =  ("0.0.0.0", 8080)
    server = ThreadedHTTPServer(listen, MyRequestHandler)
    print("USGS Collection server running!")
    thread_1 = threading.Thread(target=getUSGSDataAlways, daemon=True)
    thread_1.start()
    thread_2 = threading.Thread(target=runRanking, daemon=True)
    thread_2.start()
    thread_3 = threading.Thread(target=getCanadaDataAlways, daemon=True)
    thread_3.start()
    server.serve_forever()

if __name__ == '__main__':
    run()

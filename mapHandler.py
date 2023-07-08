import requests

# env variables import
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# GEODATA assign env to global variable
GEOAPIKEY = os.environ.get("geo-neighbor-api-key")
GEOURL = "https://api.geodatasource.com/v2/city"

# GOOGLE assign env to global variable
GOOGLEAPIKEY = os.environ.get("google-api-token")
GOOGLEURLSTATICMAP = "https://maps.googleapis.com/maps/api/staticmap"
GOOGLEURLGEOCODED = "https://maps.googleapis.com/maps/api/geocode/json"
SIZE = "640x640"
SCALE = "2"
MAPTYPE = "satellite"

class GetNearbyCity:
     
    def __init__(self):
          self.url = None

    def getNeighborCity(self, feature):
        lat = feature['lat']
        long = feature['long']
    #  print("near city: " + str(lat) + " , " + str(long))
        try:
            r = requests.get(GEOURL, params=f'key={GEOAPIKEY}&lat={lat}&lng={long}')
        except:
            r = {'latitude': lat - 1, 'longitude': long + 1}
        if r.status_code == 404:
            r = {'latitude': lat - 1, 'longitude': long + 1}
            return r
        return r.json()
         
class GetGoogleMap:

    def __init__(self):
        self.url = None

    def featureOnlyMapFromGoogle(self, feature):
        # Pull lat and long from feature then create payload string for static google map pull
        lat = feature['lat']
        long = feature['long']
        centerPayload = str(lat) + ',' + str(long)
        # Get neighbor city to feature that occured then assemble payload to nearCityMarker for map request
        n = GetNearbyCity()
        n = n.getNeighborCity(feature)
        # print("Neighbor City information:", n)
        nearCityMarker = str(n['latitude']) + ',' + str(n['longitude'])
        x = requests.get(GOOGLEURLSTATICMAP, params=f'center={centerPayload}&key={GOOGLEAPIKEY}&size={SIZE}&scale={SCALE}&maptype={MAPTYPE}&markers=color:red%7Clabel:C%7C{nearCityMarker}&markers=color:blue%7C{centerPayload}&path=color:0x0000ff|weight:5|{centerPayload}|{nearCityMarker}', stream=True ).raw
        return x
    
    def locationToFeatureMap(self, latlong, feature):
        localLat = latlong[0]
        localLong = latlong[1]
        centerPayload = str(localLat) + ',' + str(localLong)
        # Pull lat and long from feature then create payload string for static google map pull
        featureLat = feature['lat']
        featureLong = feature['long']
        featureMarker = str(featureLat) + ',' + str(featureLong)
        x = requests.get(GOOGLEURLSTATICMAP, params=f'center={centerPayload}&key={GOOGLEAPIKEY}&size={SIZE}&scale={SCALE}&maptype={MAPTYPE}&markers=anchor:center%7Cicon:https%3A%2F%2Fquaker.sfo3.cdn.digitaloceanspaces.com%2Fquaker%2Fpublic%2Ficon_target1.png%7C{featureMarker}&markers=anchor:center%7Cicon:https%3A%2F%2Fquaker.sfo3.cdn.digitaloceanspaces.com%2Fquaker%2Fpublic%2Fhome1.png%7C{centerPayload}', stream=True ).raw       #&path=color:0x0000ff|weight:5|{centerPayload}|{featureMarker}
        return x
    
class GeoCoding:
     
     def addressToLatLong(self, address):
        x = requests.get(GOOGLEURLGEOCODED, params=f'address={address}&key={GOOGLEAPIKEY}')
        if x.status_code == 200:
            if len(x.json()['results']) == 0:
                return [1,1]
            else:
                lat = x.json()['results'][0]['geometry']['location']['lat']
                long = x.json()['results'][0]['geometry']['location']['lng']
                return [lat,long]
        else:
            return [5,5]

import sqlite3  
import time

connection = sqlite3.connect("features_db.db")
cursor = connection.cursor()

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class FeaturesDB:

        def __init__(self):
            self.connection = sqlite3.connect("features_db.db")
            #setup row_factory to dict_factory as default
            self.connection.row_factory = dict_factory
            self.cursor = self.connection.cursor()

        def createNewFeature(self, id, mag, place, time, updated, tz, url, detail, felt, cdi, mmi, alert, status, tsunami, sig, net, code, ids, sources, types, nst, dmin, rms, gap, magType, type, lat, long, depth):
             data = [id, mag, place, time, updated, tz, url, detail, felt, cdi, mmi, alert, status, tsunami, sig,
                      net, code, ids, sources, types, nst, dmin, rms, gap, magType, type, lat, long, depth]
             self.cursor.execute("INSERT INTO features (featureID, mag, place, time, updated, tz, url, detail, felt, cdi, mmi, alert, status, tsunami, sig, net, code, ids, sources, types, nst, dmin, rms, gap, magType, type, lat, long, depth) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
             self.connection.commit()
        
        def getFeature(self, id):
             data = [id]
             self.cursor.execute("SELECT * FROM features WHERE featureID = ?", data)
             record = self.cursor.fetchone()
             return record
        
        def getFeatures(self):
            self.cursor.execute("SELECT * FROM features")
            records = self.cursor.fetchall()
            return records
        
        # pull features from current time back to parameter=seconds
        def getFeaturesFromLast(self, diff):
             epoch = time.time()
             data = int(epoch) - diff
             data *= 1000
             self.cursor.execute("SELECT * FROM features WHERE time > ?", [data])
             records = self.cursor.fetchall()
             return records

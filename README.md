# DidIShake.com

## Resource

**Feature**

Attributes:
* feature (string)
* mag (float)
* place (string)
* eqtime (integer)
* updated (integer)
* tz (integer)
* url (string)
* detail (string)
* felt (integer)
* cdi (float)
* mmi (float)
* alert (string)
* status (string)
* tsunami (integer)
* sig (integer)
* net (string)
* code (string)
* ids (string)
* sources (string)
* types (string)
* nst (integer)
* dmin (float)
* rms (float)
* gap (float)
* magType (string)
* type1 (string)
* long (float)
* lat (float)
* depth (float)

**User**

**Notification**

**Session**

## Schema

```sql
CREATE TABLE features (
id INTEGER PRIMARY KEY, 
featureID TEXT, 
mag REAL, 
place TEXT, 
time INTEGER, 
updated TEXT, 
tz INTEGER, 
url TEXT, 
detail TEXT, 
felt INTEGER, 
cdi REAL, 
mmi REAL, 
alert TEXT, 
status TEXT, 
tsunami INTEGER, 
sig INTEGER, 
net TEXT, 
code TEXT, 
ids TEXT, 
sources TEXT, 
types TEXT, 
nst INTEGER, 
dmin REAL, 
rms REAL, 
gap REAL, 
magType TEXT, 
type TEXT, 
lat REAL, 
long REAL, 
depth REAL);
```

```sql
CREATE TABLE users (
id INTEGER PRIMARY KEY,
email TEXT,
password TEXT,
f_name TEXT,
l_name TEXT,
mobile TEXT,
sign_up TEXT,
notifications_setting TEXT,
notifications_IDs TEXT
)
```

```sql
CREATE TABLE notifications (
id INTEGER PRIMARY KEY,
lat REAL,
long REAL,
user_primaryID INTEGER
)
```

## REST Endpoints

Name					                            | Method| Path
----------------------------------------------------|-------|---------------
Retrieve feature collection		                    | GET	| /features
Retrieve feature member                             | GET   | /features/*\<id\>*
Retrieve features current thru seconds              | GET   | /features/*\<seconds\>*
Retrieve features seconds back thru seconds back    | GET   | /features/*\<seconds\>*,*\<seconds\>*
Retrieve nearest feature to address                 | GET   | /locations/*\<address\>* (urlencoded)
Convert address to lat and long                     | GET   | /geos/*\<address\>* (urlencoded)     
Retrieve Daily top feature                          | GET   | /rankings/daily
Retrieve server uptime in seconds                   | GET   | /uptimes/server

## Functions

**getNearestFeatureToAddress**

    Extra Small -   0 <= or <= 2.5 Magnitude
                    <= 10 Miles

    Small -         2.5 <= or <= 5.4 Magnitude
                    <= 75 Miles

    Medium -        5.5 <= or <= 6.9 Magnitude
                    <= 450 Miles
                    
    Large -         >= 7.0 Magnitude
                    <= 750 Miles




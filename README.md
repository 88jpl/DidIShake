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

## REST Endpoints

Name					                | Method| Path
----------------------------------------|-------|---------------
Retrieve feature collection		        | GET	| /features
Retrieve feature member                 | GET   | /features/*\<id\>*
Retrieve feature current thru seconds   | GET   | /features/*\<seconds\>*
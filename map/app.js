var features = [];

var map = L.map('map').setView([37.075247, -113.585698], 5);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
// Marker for location of search
var marker = L.marker([37.075247, -113.585698]).addTo(map);

function loadRecentFeatures(depth) {
    fetch(`http://jpl.hopto.me:53011/features/${depth}`, {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded; utf-8"
        }
    }).then(function (response) {
        if (response.status == 200) {
            console.log(response.status);
            response.json().then(function (data) {
                // console.log(data);
                data.forEach(element => {
                    console.log(element["featureID"]);
                    let date = new Date(element['time']);

                    var featureMarker = L.marker([element["lat"],element["long"]]).addTo(map);
                    featureMarker.bindPopup(`<b>ID: ${element['featureID']}</b><br>Nearby: ${element['place']}<br>Magnitude: ${element['mag']}<br>Occured @ ${date}<br>Distance: ${Math.round(calculateDistance(marker, featureMarker) * 100) / 100} miles`);
                    console.log(element['time']);
                    console.log(date);
                })
            })
        }
    })
}
function calculateDistance(homeObject, featureObject) {
    // Get Home lat/long
    var homeLat = homeObject._latlng["lat"];
    var homeLong = homeObject._latlng["lng"]; 
    // console.log(homeLat + " " + homeLong);
    //  Get Feature lat/long
    var featureLat = featureObject._latlng["lat"];
    var featureLong = featureObject._latlng["lng"];
    // calculate distance
    // Convert decimal degrees to radians
    var pi = Math.PI;
    homeLat = homeLat * (pi/180);
    homeLong = homeLong * (pi/180);
    featureLat = featureLat * (pi/180);
    featureLong = featureLong * (pi/180);
    // Haversine Formula
    distanceLat = homeLat - featureLat;
    distanceLong = homeLong - featureLong;
    a = Math.pow(Math.sin(distanceLat/2), 2) + Math.cos(featureLat) * Math.cos(homeLat) * Math.pow(Math.sin(distanceLong/2), 2);
    c = 2 * Math.asin(Math.sqrt(a));
    // Radius of earth in Kilometers (6371)
    km = 6371 * c;
    miles = km * 0.621371;
    return miles;
}
function msToTime(s) {
    var ms = s % 1000;
    s = (s- ms) / 1000;
    var secs = s % 60;
    s = (s - secs) / 60;
    var mins = s % 60;
    var hrs = (s - mins) / 60;
    // Add leading zero for time of minutes and seconds
    if (mins < 10) {
        mins = "0" + mins.toString();
    }
    if (secs < 10) {
        secs = "0" + secs.toString();
    }
     return hrs + ':' + mins + ':' + secs ;
}

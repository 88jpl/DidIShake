var features = [];
var events = L.layerGroup();
var homeLocationLatLong = null;

var map = L.map('map', {
    center: [0,0],
    zoom: 3,
    layers: events
});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
// Marker for location of search
// var marker = L.marker([37.075247, -113.585698]).addTo(map);

function locationSearch() {
    var homeLocation = document.querySelector("#home-location");
    var address = encodeURIComponent(homeLocation.value);
    fetch(`http://jpl.hopto.me:53011/geos/${address}`, {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded; utf-8"
        }
    }).then(function (response) {
        if (response.status == 200) {
            // console.log(response.json());
            response.json().then(function (data) {
                console.log(data);
                // L.marker(data).addTo(map);
                const myCustomColour = '#583470'

                const markerHtmlStyles = `
                background-color: ${myCustomColour};
                width: 3rem;
                height: 3rem;
                display: block;
                left: -1.5rem;
                top: -1.5rem;
                position: relative;
                border-radius: 3rem 3rem 0;
                transform: rotate(45deg);
                border: 1px solid #FFFFFF`

                const myIcon = L.divIcon({
                className: "my-custom-pin",
                iconAnchor: [0, 24],
                labelAnchor: [-6, 0],
                popupAnchor: [0, -36],
                html: `<span style="${markerHtmlStyles}" />`
                })
                L.marker(data, {icon: myIcon}).addTo(map);
                map.setView(data, 4);
                homeLocationLatLong = L.marker(data);
                // console.log(homeLocationLatLong);
            })
        }
    })
}
// submit the search address when button is clicked
var addressSearchButton = document.querySelector("#submit-home");
addressSearchButton.addEventListener("click", locationSearch);
var addressSearchInput = document.querySelector("#home-location");
addressSearchInput.onkeypress = function (event) {
    if (event.keyCode === 13) {
        locationSearch();
    }
};

function populateMap() {
    // get elements
    var days = document.querySelector("#depth-days");
    var hours = document.querySelector("#depth-hours");
    var mins = document.querySelector("#depth-minutes");

    // console.log("days:" + days.value);
    // convert to seconds
    var daySecs = 86400 * days.value;
    var hourSecs = 3600 * hours.value;
    var minSecs = 60 * mins.value;
    var depthSecs = daySecs + hourSecs + minSecs;
    // return depthSecs;
    loadRecentFeatures(depthSecs)
}

// Submit Interactive Map depth search
var depthSubmitButton = document.querySelector("#submit-depth");

depthSubmitButton.onclick = function () {
    // layerControl.removeLayer("Events");
    populateMap();
}

function loadRecentFeatures(depth) {
    fetch(`http://jpl.hopto.me:53011/features/${depth}`, {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded; utf-8"
        }
    }).then(function (response) {
        
        if (response.status == 200) {
            // console.log(response.status);
            response.json().then(function (data) {
                // console.log(data);
                events.clearLayers();
                data.forEach(element => {
                    // console.log(element["featureID"]);
                    // Convert time from ms to date
                    let date = new Date(element['time']);
                    if (homeLocationLatLong == null) {
                        // console.log("null!");
                        homeLocationLatLong = L.marker([0, 0]).addTo(map);
                    }
                    var featureMarker = L.marker([element["lat"],element["long"]]).addTo(events);
                    var distance = Math.round(calculateDistance(homeLocationLatLong, featureMarker) * 100) / 100;
                    // console.log(distance);
                    featureMarker.bindPopup(`<b>ID: ${element['featureID']}</b><br>Nearby: ${element['place']}<br>Magnitude: ${element['mag']}<br>Occured @ ${date}<br>Distance: ${distance} miles`);
                    // console.log(element['time']);
                    // console.log(date);

                })
                console.log(events);
                var overlays = {
                    'Events': events
                };
                var layerControl = L.control.layers(overlays);
                // layerControl.addOverlay(overlays);
            })
        }
        
    })
}
function addFeaturesOntoMap () {

    
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

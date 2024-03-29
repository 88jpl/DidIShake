DAILYLEADER = {};
UPTIME = {};

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
function timeToMs(time) {

    var splitTime = time.split(":");
    if (splitTime.length == 3) {
        var hours = parseInt(splitTime[0]);
        var mins = parseInt(splitTime[1]);
        var secs = parseInt(splitTime[2]);
        ms = ((hours * 3600) + (mins * 60) + secs) * 1000;
        // console.log(hours, mins, secs);
        return ms
    } else {
        return time
    }
    // console.log("timeSPlits:" , splitTime);
    
}
// Address Search
function mainAddressSearch() {
    var addressSearchInput = document.querySelector("#search-input");
    var address = encodeURIComponent(addressSearchInput.value);
    fetch(`http://jpl.hopto.me:53011/locations/${address}`, {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded; utf-8"
        }
    }).then(function (response) {
        if (response.status == 200) {
            // console.log(response.json());
            response.json().then(function (data) {
                // console.log(data);
                // Clear Daily Top stats
                var heroImage = document.querySelector("#results");
                heroImage.style.backgroundImage=`url(${data['uri']})`
                var nearbyCity = document.querySelector("#stat-nearby-city-data");
                var magnitude = document.querySelector("#stat-magnitude-data");
                var timeOccured = document.querySelector("#stat-time-occured-data");
                var leaderTime = document.querySelector("#stat-time-as-leader-data");
                nearbyCity.innerHTML = magnitude.innerHTML = timeOccured.innerHTML = "";
                leaderTime.remove();
                if (data['lat'] == 0 && data['long'] == 0) {  
                    var dataHeader = document.getElementsByClassName("data-header");
                    // console.log(dataHeader);
                    dataHeader[0].innerHTML = dataHeader[1].innerHTML = dataHeader[2].innerHTML = dataHeader[3].innerHTML = ""; 
                    dataHeader[0].innerHTML = "Searched through ";
                    dataHeader[1].innerHTML = data['checked'];
                    dataHeader[2].innerHTML = " total events.";
                    // Show Signup popup
                }
            })
        } else {
            // Show Signup popup

            console.log("No Data Received");
        }
    })
}
// function being called with interval
const myDailyTopTimer = setInterval(dailyTopTimer, 1000);
const myServerUptime = setInterval(serverCounter, 1000);

function dailyTopTimer() {
    var leaderTime = document.querySelector("#stat-time-as-leader-data");
    leaderTime.innerHTML = msToTime( Date.now() - DAILYLEADER['time']);
}

function serverCounter() {
    var serverUptime = document.querySelector("#server-uptime");
    UPTIME['serverUptime'] =  UPTIME['serverUptime'] + 1;
    // console.log(msToTime(UPTIME['serverUptime'] * 1000));
    serverUptime.innerHTML = msToTime(UPTIME['serverUptime'] * 1000);
}

// submit the search address when button is clicked
var addressSearchButton = document.querySelector("#search-location-btn");
addressSearchButton.addEventListener("click", mainAddressSearch);
// Submit the search address when enter is hit inside the input field
var addressSearchInput = document.querySelector("#search-input");
addressSearchInput.onkeypress = function (event) {
    if (event.keyCode === 13) {
        mainAddressSearch();
    }
};
// Daily top load
function loadLeadingFeatureStats() {
    fetch(`http://jpl.hopto.me:53011/rankings/daily`, {
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
                DAILYLEADER = data;
                var nearbyCity = document.querySelector("#stat-nearby-city-data");
                var magnitude = document.querySelector("#stat-magnitude-data");
                var timeOccured = document.querySelector("#stat-time-occured-data");var 
                leaderTime = document.querySelector("#stat-time-as-leader-data");
                leaderTime.innerHTML = msToTime(Date.now() - data['time']);
                nearbyCity.innerHTML = data['place'];
                magnitude.innerHTML = data['mag'];
                timeOccured.innerHTML = new Date(data['time']);
                // console.log("Time:", Math.floor((new Date()).getTime())
                //     , "Event Time:", data['time'], "=", Math.floor((new Date()).getTime())-data['time']);
        
                // timeAsLeader = Date.now() - data['time'];
                // leaderTime.innerHTML = msToTime(timeAsLeader);
            })
        } else {
            console.log("Error Loading Daily Top Stats From Server!");
        }
    })
}
function loadServerUptime() {
    fetch(`http://jpl.hopto.me:53011/uptimes/server`, {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded; utf-8"
        }
    }).then(function (response) {
        if (response.status == 200) {
            response.json().then(function (data) {
                var serverUptime = document.querySelector("#server-uptime");
                // console.log(serverUptime);
                UPTIME = data
                // console.log("Server Uptime: ", data);
                serverUptime.innerHTML = msToTime(data['serverUptime'] * 1000);
        })
    } else {
        var serverUptime = document.querySelector("#server-uptime");
        serverUptime.innerHTML = "Server Not Awake!";
        console.log("Error Loading Server Uptime!");
    }
    })
}
loadServerUptime();
loadLeadingFeatureStats();
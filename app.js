function msToTime(s) {
    var ms = s % 1000;
    s = (s- ms) / 1000;
    var secs = s % 60;
    s = (s - secs) / 60;
    var mins = s % 60;
    var hrs = (s - mins) / 60;

    return hrs + ':' + mins + ':' + secs + '.' + ms;
}
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
                console.log(data);
                // Clear Daily Top stats
                var heroImage = document.querySelector("#results");
                heroImage.style.backgroundImage=`url(${data['uri']})`
                var nearbyCity = document.querySelector("#stat-nearby-city-data");
                var magnitude = document.querySelector("#stat-magnitude-data");
                var timeOccured = document.querySelector("#stat-time-occured-data");
                var leaderTime = document.querySelector("#stat-time-as-leader-data");
                nearbyCity.innerHTML = magnitude.innerHTML = timeOccured.innerHTML = leaderTime.innerHTML = "";
                if (data['lat'] == 0 && data['long'] == 0) {  
                    var dataHeader = document.getElementsByClassName("data-header");
                    console.log(dataHeader);
                    dataHeader[0].innerHTML = dataHeader[1].innerHTML = dataHeader[2].innerHTML = dataHeader[3].innerHTML = ""; 
                    dataHeader[0].innerHTML = "Searched through ";
                    dataHeader[1].innerHTML = data['checked'];
                    dataHeader[2].innerHTML = " total events.";
                }
            })
        } else {
            console.log("No Data Received");
        }
    })
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
function loadLeadingFeatureStats() {
    fetch(`http://jpl.hopto.me:53011/rankings/daily`, {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded; utf-8"
        }
    }).then(function (response) {
        if (response.status == 200) {
            console.log(response.status);
            response.json().then(function (data) {
                console.log(data);
                var nearbyCity = document.querySelector("#stat-nearby-city-data");
                var magnitude = document.querySelector("#stat-magnitude-data");
                var timeOccured = document.querySelector("#stat-time-occured-data");
                var leaderTime = document.querySelector("#stat-time-as-leader-data");
                nearbyCity.innerHTML = data['place'];
                magnitude.innerHTML = data['mag'];
                timeOccured.innerHTML = new Date(data['time']);
                console.log("Time:", Math.floor((new Date()).getTime())
                    , "Event Time:", data['time'], "=", Math.floor((new Date()).getTime())-data['time']);
                timeAsLeader = Date.now() - data['time'];
                leaderTime.innerHTML = msToTime(timeAsLeader);
            })
        } else {
            console.log("Error Loading Daily Top Stats From Server!");
        }
    })
}
loadLeadingFeatureStats();
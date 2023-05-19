function msToTime(s) {
    var ms = s % 1000;
    s = (s- ms) / 1000;
    var secs = s % 60;
    s = (s - secs) / 60;
    var mins = s % 60;
    var hrs = (s - mins) / 60;

    return hrs + ':' + mins + ':' + secs + '.' + ms;
}
var addressSearchButton = document.querySelector("#search-location-btn");
addressSearchButton.onclick = function () {
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
                var heroImage = document.querySelector("#results");
                heroImage.style.backgroundImage=`url(${data['uri']})`
            })
        } else {
            console.log("No Data Received");
        }
    })
}
function loadLeadingFeatureStats() {
    fetch(`http://localhost:8080/rankings/daily`, {
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
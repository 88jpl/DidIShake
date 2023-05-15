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
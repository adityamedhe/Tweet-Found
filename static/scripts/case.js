/*global $ id location*/

var map, marker;
function initMap(lat, lng) {
    map = new window.google.maps.Map(document.getElementById('map'), {
        center: {lat: lat, lng: lng},
        zoom: 14
    });
    
    marker = new window.google.maps.Marker({
        position: {lat: lat, lng: lng},
        map: map
    });
    
    
    $(window).resize(function() {
        console.log("Resized");
        map.setCenter(new window.google.maps.LatLng(lat, lng));
    });
}


$(document).ready(function() {
    $("#btn-tweet").on('click', function() {
        $.ajax('/case/' + id + '/tweet', {
            method: "POST",
            complete: function(jqXhr) {
                switch (jqXhr.status) {
                    case 200:
                        location.reload();
                        break;
                    
                    case 403:
                        $("#status").show().text("You have tweeted recently. Please wait.");
                        break;
                        
                    case 400:
                        $("#status").show().text("There is a problem with your request.");
                        break;
                        
                    case 500:
                        $("#status").show().text("Some error occured while processing. Please try again.");
                        break;
                }
            }
        });
    });
});

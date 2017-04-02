/*global $ navigator*/
$(document).ready(function() {
    var map = new window.google.maps.Map(document.getElementById('map'), {
        center: {lat: 21.1612315, lng: 79.0024697},
        zoom: 5
    });
    
    var marker = new window.google.maps.Marker(/*{
        position: {lat: 21.1612315, lng: 79.0024697},
        map: map
    }*/);
    
    map.addListener('click', function(e) {
        var lat = e.latLng.lat();
        var lng = e.latLng.lng();
        
        $("#lat").val(lat);
        $("#lng").val(lng);
        
        marker.setMap(map);
        marker.setPosition(new window.google.maps.LatLng(lat, lng));
        
    });
    
    
    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            
            map.setCenter(new window.google.maps.LatLng(lat, lng));
            map.setZoom(15);
            
        });
    } else {
        // couldn't get location
    }
    
});
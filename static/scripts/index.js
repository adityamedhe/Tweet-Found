/*global location $*/
$(document).ready(function() {
    $("#btn-track").on('click', function() {
        location.href = '/case/' + $("#inp-id").val().trim();
    });
    
    $("#btn-new").on('click', function() {
        location.href = '/new_case';
    });
});
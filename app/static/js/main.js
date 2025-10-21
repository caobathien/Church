$(document).ready(function() {
    // Xử lý nút toggle cho sidebar
    $("#menu-toggle").click(function(e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
    });
});
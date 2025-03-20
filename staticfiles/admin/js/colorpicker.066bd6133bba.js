document.addEventListener("DOMContentLoaded", function() {
    let colorFields = document.querySelectorAll("input[name=hex_code]");
    colorFields.forEach(function(field) {
        field.setAttribute("type", "color");
    });
});

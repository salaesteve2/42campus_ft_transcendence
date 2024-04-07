document.addEventListener("DOMContentLoaded", function() {
    // Agrega un evento de clic a un botón (o cualquier elemento) para avanzar en el historial
    document.getElementById("forwardButton").addEventListener("click", function() {
        history.forward();
    });

    // Agrega un evento de clic a un botón (o cualquier elemento) para retroceder en el historial
    document.getElementById("backButton").addEventListener("click", function() {
        history.back();
    });
});

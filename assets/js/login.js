// login.js

function authenticate() {
    // Obtiene los valores de los campos de entrada
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Validación básica de ejemplo (reemplaza esto con la lógica de autenticación real)
    if (username === "admin" && password === "admin123") {
        // Redirige a dashboard.html si la autenticación es exitosa
        location.href = 'dashboard.html';
    } else {
        // Muestra un mensaje de error si la autenticación falla
        alert("Usuario o contraseña incorrectos. Inténtalo de nuevo.");
    }
}

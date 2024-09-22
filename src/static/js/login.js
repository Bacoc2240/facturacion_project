// login.js

function authenticate() {
    // Obtiene los valores de los campos de entrada
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Envía los datos al servidor Flask
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirige a dashboard.html si la autenticación es exitosa
            window.location.href = '/dashboard';
        } else {
            // Muestra un mensaje de error si la autenticación falla
            alert("Usuario o contraseña incorrectos. Inténtalo de nuevo.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al intentar autenticarse. Inténtalo de nuevo.');
    });
}

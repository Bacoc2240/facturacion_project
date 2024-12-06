// login.js

function authenticate() {
    // Obtiene los valores de los campos de entrada
    const nombre_usuario = document.getElementById('nombre_usuario').value;
    const contraseña = document.getElementById('contraseña').value;
    
    // Envía los datos al servidor Flask
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nombre_usuario, contraseña })
    })
    .then(response => response.json())  // Espera respuesta en formato JSON
    .then(data => {
        console.log('Respuesta del servidor:', data);  // Depura si la respuesta es correcta
        if (data.success) {
            // Redirige a dashboard.html si la autenticación es exitosa
            window.location.href = '/dashboard';
        } else {
            // Muestra un mensaje de error si la autenticación falla
            alert(data.message || "Usuario o contraseña incorrectos. Inténtalo de nuevo.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al intentar autenticarse. Inténtalo de nuevo.');
    });
}


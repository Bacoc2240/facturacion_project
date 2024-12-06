// registro.js

function register() {
    // Traemos los valores de los campos de entrada
    const nombre_usuario = document.getElementById('nombre_usuario').value;
    const contraseña = document.getElementById('contraseña').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const rol = document.getElementById('rol').value;
    const id_empleado = document.getElementById('id_empleado').value;

    // Verifica que las contraseñas coincidan
    if (contraseña !== confirm_password) {
        alert('Las contraseñas no coinciden. Inténtalo de nuevo.');
        return;
    }

    // Envía los datos al servidor Flask
    fetch('/auth/registro', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nombre_usuario, contraseña, confirm_password, rol, id_empleado })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        console.log('Respuesta del servidor:', data);  // Depura si la respuesta es correcta
        if (data.success) {
            // Redirige a login.html si el registro es exitoso
            window.location.href = '/login';
        } else {
            // Muestra un mensaje de error si el registro falla
            alert(data.message || "Error al registrar el usuario. Inténtalo de nuevo.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al intentar registrar el usuario. Inténtalo de nuevo.');
    });
}

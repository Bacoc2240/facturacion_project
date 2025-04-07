/**
 * Funciones para manejar la impresión y compartir facturas
 */

// Convertir factura en PDF
function generarPDF() {
    // Opciones de configuración para html2pdf
    const options = {
        margin: [10, 10, 10, 10],
        filename: `factura_${facturaId}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
            scale: 2,
            useCORS: true,
            logging: false
        },
        jsPDF: { 
            unit: 'mm', 
            format: 'a4', 
            orientation: 'portrait' 
        }
    };

    // Elemento que se va a convertir en PDF
    const element = document.getElementById('factura-imprimir');
    
    // Generar el PDF y retornar la promesa
    return html2pdf().set(options).from(element).save();
}

// Imprimir la factura
function imprimirFactura() {
    window.print();
}

// Mostrar modal para compartir factura
function compartirFactura() {
    // Obtener el correo del cliente si existe
    const emailInput = document.getElementById('emailDestinatario');
    
    // Mostrar modal
    $('#compartirModal').modal('show');
}

// Enviar factura por email
async function enviarPorEmail() {
    try {
        // Obtener datos del formulario
        const email = document.getElementById('emailDestinatario').value;
        const asunto = document.getElementById('asuntoEmail').value;
        const mensaje = document.getElementById('mensajeEmail').value;
        
        // Validar email
        if (!email || !validateEmail(email)) {
            mostrarAlerta('Error', 'Por favor ingrese un correo electrónico válido', 'error');
            return;
        }
        
        // Mostrar indicador de carga
        Swal.fire({
            title: 'Enviando...',
            text: 'Estamos enviando la factura por correo electrónico',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Enviar petición al servidor
        const response = await fetch(`/facturas/api/compartir/${facturaId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                asunto: asunto,
                mensaje: mensaje
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Cerrar el modal
            $('#compartirModal').modal('hide');
            
            // Mostrar mensaje de éxito
            Swal.fire({
                title: '¡Enviado!',
                text: 'La factura ha sido enviada correctamente',
                icon: 'success',
                confirmButtonText: 'Aceptar'
            });
        } else {
            throw new Error(data.error || 'Error al enviar la factura');
        }
    } catch (error) {
        console.error('Error enviando email:', error);
        
        Swal.fire({
            title: 'Error',
            text: `No se pudo enviar la factura: ${error.message}`,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    }
}

// Validar formato de email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

// Mostrar alerta con SweetAlert2
function mostrarAlerta(titulo, mensaje, tipo) {
    Swal.fire({
        title: titulo,
        text: mensaje,
        icon: tipo,
        confirmButtonText: 'Aceptar'
    });
}

// Volver a la lista de facturas
function volver() {
    window.location.href = '/facturas/';
}

// Inicialización cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Añadir event listeners si es necesario
    console.log('Factura lista para imprimir/compartir. ID:', facturaId);
});
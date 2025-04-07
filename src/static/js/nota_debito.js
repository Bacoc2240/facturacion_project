/**
 * nota_debito.js - Versión inicial
 * 
 * Este módulo se encarga de la creación y gestión de notas débito.
 * Está adaptado del módulo de notas crédito.
 */

// Variables globales
let numeroNotaDebito = 1; // Valor predeterminado para el número de nota débito

// Funciones globales que exportamos para uso en otros archivos
window.cargarYMostrarModalND = cargarYMostrarModalND;

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('Módulo de nota débito cargado correctamente');
    verificarDependencias();
});

/**
 * Función principal para cargar y mostrar el modal de nota débito
 * @param {number} facturaId - ID de la factura
 */
function cargarYMostrarModalND(facturaId) {
    console.log("cargarYMostrarModalND llamada con ID:", facturaId);
    
    // Por ahora, mostraremos un mensaje indicando que esta funcionalidad está en desarrollo
    Swal.fire({
        title: 'Funcionalidad en desarrollo',
        html: `Se aplicará una nota débito a la factura #${facturaId}<br><br>
               Esta funcionalidad estará disponible próximamente.`,
        icon: 'info',
        confirmButtonText: 'Entendido'
    });
    
    // Código a implementar cuando la funcionalidad esté completa
    /*
    // Mostrar indicador de carga
    Swal.fire({
        title: 'Cargando información de factura',
        text: 'Por favor espere...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Cargar datos de la factura
    fetch(`/facturas/api/facturas/${facturaId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudo cargar la información de la factura');
            }
            return response.json();
        })
        .then(data => {
            Swal.close();
            
            if (data.success && data.factura) {
                console.log("Datos de factura cargados correctamente");
                abrirModalNotaDebito(facturaId, data.factura);
            } else {
                throw new Error('Datos de factura inválidos');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error',
                text: error.message || 'No se pudo cargar la información de la factura',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        });
    */
}

/**
 * Verifica las dependencias necesarias (jQuery, Bootstrap, FontAwesome)
 */
function verificarDependencias() {
    // Verificar si jQuery está disponible
    if (typeof jQuery === 'undefined') {
        console.warn('jQuery no encontrado. Algunas funcionalidades pueden no trabajar correctamente.');
    }
    
    // Verificar si Bootstrap está disponible
    if (typeof bootstrap === 'undefined' && typeof jQuery.fn.modal === 'undefined') {
        console.warn('Bootstrap no encontrado. El modal puede no funcionar correctamente.');
    }
    
    console.log('Verificación de dependencias completada.');
}

// Implementación completa de abrirModalNotaDebito y otras funciones relacionadas
// se agregarán cuando la funcionalidad esté lista para producción
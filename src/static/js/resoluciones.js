// ===============================
// VARIABLES Y CONFIGURACIÓN INICIAL
// ===============================

// Array para almacenar las resoluciones cargadas
let resoluciones = [];
let DOM = {};

// Referencias a elementos del DOM frecuentemente utilizados
function initializeDOMReferences() {
    DOM = {
        resolucionTable: document.getElementById('resolucionTable'),
        searchInput: document.getElementById('search'),
        resolucionForm: document.getElementById('resolucionForm')
    };
}

// ===============================
// GESTIÓN DE RESOLUCIONES DIAN
// ===============================

/**
 * Carga las resoluciones desde el backend y las renderiza en la tabla
 */
async function cargarResoluciones() {
    try {
        // Corrige la ruta base para que coincida con tu controlador
        const response = await fetch('/resoluciondian/api/resoluciones/lista');
        if (!response.ok) {
            throw new Error(`¡Error HTTP! Estado: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        
        resoluciones = data.resoluciones;
        renderResolucionTable(resoluciones);
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar resoluciones: ' + error.message, 'error');
    }
}

/**
 * Renderiza la tabla de resoluciones con los datos proporcionados
 * @param {Array} resolucionesList - Lista de resoluciones a mostrar
 */
function renderResolucionTable(resolucionesList = resoluciones) {
    if (!DOM.resolucionTable) return;

    DOM.resolucionTable.innerHTML = '';
    
    // Si no hay resoluciones, mostrar mensaje
    if (resolucionesList.length === 0) {
        DOM.resolucionTable.innerHTML = `
            <tr>
                <td colspan="8" class="text-center">No hay resoluciones registradas</td>
            </tr>
        `;
        return;
    }
    
    // Renderizar cada resolución
    resolucionesList.forEach((resolucion) => {
        const row = `
            <tr class="${resolucion.activa ? 'table-success' : ''} ${!resolucion.vigente ? 'table-danger' : ''}">
                <td>${resolucion.numero_resolucion || ''}</td>
                <td>${resolucion.rango_inicial || ''} - ${resolucion.rango_final || ''}</td>
                <td>${formatearFecha(resolucion.fecha_inicial)}</td>
                <td>${formatearFecha(resolucion.fecha_final)}</td>
                <td>${resolucion.numero_actual || resolucion.rango_inicial || ''}</td>
                <td>
                    <span class="badge ${resolucion.activa ? 'badge-success' : 'badge-secondary'}">
                        ${resolucion.activa ? 'Activa' : 'Inactiva'}
                    </span>
                </td>
                <td>
                    <span class="badge ${resolucion.vigente ? 'badge-success' : 'badge-danger'}">
                        ${resolucion.vigente ? 'Vigente' : 'Vencida'}
                    </span>
                </td>
                <td>
                    ${!resolucion.activa && resolucion.vigente ? 
                        `<button class="btn btn-primary btn-sm" onclick="activarResolucion(${resolucion.id})">Activar</button>` 
                        : ''}
                </td>
            </tr>
        `;
        DOM.resolucionTable.insertAdjacentHTML('beforeend', row);
    });
}

/**
 * Abre el modal de nueva resolución y reinicia sus campos
 */
function openResolucionModal() {
    if (!DOM.resolucionForm) {
        console.error('No se pudo encontrar el formulario de resolución');
        return;
    }
    
    DOM.resolucionForm.reset();
    
    // Establecer la fecha actual como mínima para las fechas
    const fechaActual = new Date().toISOString().split('T')[0];
    document.getElementById('fechaInicial').min = fechaActual;
    document.getElementById('fechaFinal').min = fechaActual;
    
    $('#resolucionModal').modal('show');
}

/**
 * Guarda una nueva resolución DIAN
 */
async function guardarResolucion(event) {
    if (event) event.preventDefault();
    
    try {
        // Obtener datos del formulario
        const numeroResolucion = document.getElementById('numeroResolucion').value;
        const rangoInicial = parseInt(document.getElementById('rangoInicial').value);
        const rangoFinal = parseInt(document.getElementById('rangoFinal').value);
        const fechaInicial = document.getElementById('fechaInicial').value;
        const fechaFinal = document.getElementById('fechaFinal').value;
        const activar = document.getElementById('activarResolucion').checked;
        
        // Validar campos
        if (!numeroResolucion || !rangoInicial || !rangoFinal || !fechaInicial || !fechaFinal) {
            mostrarNotificacion('Todos los campos son obligatorios', 'warning');
            return;
        }
        
        if (rangoInicial >= rangoFinal) {
            mostrarNotificacion('El rango inicial debe ser menor al rango final', 'warning');
            return;
        }
        
        if (new Date(fechaInicial) > new Date(fechaFinal)) {
            mostrarNotificacion('La fecha inicial debe ser anterior a la fecha final', 'warning');
            return;
        }
        
        // Preparar datos para enviar
        const datosResolucion = {
            numero_resolucion: numeroResolucion,
            rango_inicial: rangoInicial,
            rango_final: rangoFinal,
            fecha_inicial: fechaInicial,
            fecha_final: fechaFinal,
            activar: activar
        };
        
        // Enviar datos al servidor
        // IMPORTANTE: Asegúrate de que esta ruta coincida exactamente con la ruta del controlador
        const response = await fetch('/resoluciondian/api/resoluciones/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datosResolucion)
        });
        
        // Verificar respuesta
        if (!response.ok) {
            // Intentar obtener mensaje de error del servidor
            try {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
            } catch (jsonError) {
                // Si no podemos parsear la respuesta como JSON, usar mensaje genérico
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
        }
        
        const data = await response.json();
        
        // Si todo fue exitoso
        mostrarNotificacion('Resolución DIAN creada exitosamente', 'success');
        $('#resolucionModal').modal('hide');
        
        // Recargar la lista de resoluciones
        await cargarResoluciones();
        
    } catch (error) {
        console.error('Error al guardar resolución:', error);
        mostrarNotificacion('Error al guardar resolución: ' + error.message, 'error');
    }
}

/**
 * Activa una resolución específica
 * @param {number} idResolucion - ID de la resolución a activar
 */
async function activarResolucion(idResolucion) {
    try {
        if (!confirm('¿Está seguro de activar esta resolución? La resolución activa actual será desactivada.')) {
            return;
        }
        
        // Utiliza la ruta correcta que corresponde con tu controlador
        const response = await fetch(`/resoluciondian/api/resoluciones/activar/${idResolucion}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            // Intentar obtener mensaje de error del servidor
            try {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
            } catch (jsonError) {
                // Si no podemos parsear la respuesta como JSON, usar mensaje genérico
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
        }
        
        const data = await response.json();
        
        // Si todo fue exitoso
        mostrarNotificacion('Resolución DIAN activada exitosamente', 'success');
        
        // Recargar la lista de resoluciones
        await cargarResoluciones();
        
    } catch (error) {
        console.error('Error al activar resolución:', error);
        mostrarNotificacion('Error al activar resolución: ' + error.message, 'error');
    }
}

/**
 * Obtiene la resolución activa actual
 */
async function obtenerResolucionActiva() {
    try {
        // Utiliza la ruta correcta que corresponde con tu controlador
        const response = await fetch('/resoluciondian/api/resoluciones/activa');
        
        if (!response.ok) {
            if (response.status === 404) {
                // No hay resolución activa, lo cual es un caso válido
                return null;
            }
            throw new Error(`Error al obtener resolución activa: ${response.status}`);
        }
        
        const data = await response.json();
        return data.resolucion;
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al obtener resolución activa: ' + error.message, 'error');
        return null;
    }
}

// ===============================
// FUNCIONES AUXILIARES
// ===============================

/**
 * Formatea una fecha para mostrarla en la interfaz
 * @param {string} fecha - Fecha en formato ISO 
 * @returns {string} Fecha formateada
 */
function formatearFecha(fecha) {
    if (!fecha) return '';
    return new Date(fecha).toLocaleDateString('es-CO');
}

/**
 * Muestra una notificación usando SweetAlert2 si está disponible, o alert como fallback
 * @param {string} mensaje - El mensaje a mostrar
 * @param {string} tipo - El tipo de notificación ('success', 'error', 'warning', 'info')
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: tipo.charAt(0).toUpperCase() + tipo.slice(1),
            text: mensaje,
            icon: tipo,
            timer: tipo === 'error' ? 0 : 1500,
            showConfirmButton: tipo === 'error'
        });
    } else {
        alert(mensaje);
    }
}

// ===============================
// EVENT LISTENERS
// ===============================

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar referencias DOM
    initializeDOMReferences();
    
    // Verificar que los elementos existan antes de agregar event listeners
    if (!DOM.resolucionForm) {
        console.error('No se pudo encontrar el formulario de resolución');
    } else {
        DOM.resolucionForm.addEventListener('submit', guardarResolucion);
    }
    
    // Evento para el campo de búsqueda
    if (DOM.searchInput) {
        DOM.searchInput.addEventListener('input', () => {
            const searchTerm = DOM.searchInput.value.toLowerCase();
            const filteredResoluciones = resoluciones.filter(resolucion => 
                resolucion.numero_resolucion?.toLowerCase().includes(searchTerm)
            );
            renderResolucionTable(filteredResoluciones);
        });
    }
    
    // Cargar resoluciones al iniciar
    cargarResoluciones();
    
    // Validaciones para el formulario de resolución
    const rangoInicial = document.getElementById('rangoInicial');
    const rangoFinal = document.getElementById('rangoFinal');
    const fechaInicial = document.getElementById('fechaInicial');
    const fechaFinal = document.getElementById('fechaFinal');
    
    if (rangoInicial && rangoFinal) {
        rangoInicial.addEventListener('change', () => {
            if (parseInt(rangoInicial.value) >= parseInt(rangoFinal.value)) {
                mostrarNotificacion('El rango inicial debe ser menor al rango final', 'warning');
                rangoInicial.value = '';
            }
        });
        
        rangoFinal.addEventListener('change', () => {
            if (parseInt(rangoFinal.value) <= parseInt(rangoInicial.value)) {
                mostrarNotificacion('El rango final debe ser mayor al rango inicial', 'warning');
                rangoFinal.value = '';
            }
        });
    }
    
    if (fechaInicial && fechaFinal) {
        fechaInicial.addEventListener('change', () => {
            fechaFinal.min = fechaInicial.value;
            if (fechaFinal.value && new Date(fechaInicial.value) > new Date(fechaFinal.value)) {
                fechaFinal.value = fechaInicial.value;
            }
        });
    }
});
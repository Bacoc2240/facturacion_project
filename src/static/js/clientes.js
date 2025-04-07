// Estado global para los clientes
let clientes = [];
// Variables globales
let editMode = false;
let editClientId = null;

// Función para cargar los clientes desde la API
async function cargarClientes() {
    try {
        console.log('Intentando cargar clientes...');
        const response = await fetch('/clientes/api/lista');
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error del servidor (${response.status}):`, errorText);
            throw new Error(`Error del servidor: ${response.status}`);
        }
        
        clientes = await response.json();
        console.log('Clientes cargados:', clientes);
        actualizarTablaClientes(clientes);
    } catch (error) {
        console.error('Error detallado al cargar clientes:', error);
        mostrarError(`Error al cargar los clientes: ${error.message}`);
    }
}

function formatearHistorial(historialText) {
    if (!historialText || historialText === 'No aplica') {
        return 'No aplica';
    }
    
    // Dividir por líneas
    const lineas = historialText.split('\n');
    let htmlFormateado = '';
    
    lineas.forEach(linea => {
        // Verificar que la línea contenga el formato esperado
        if (linea.includes(':')) {
            // Separar la fecha/factura de los productos
            const [facturaInfo, productosInfo] = linea.split(':');
            
            // Crear contenedor para esta entrada
            htmlFormateado += '<div class="historial-entrada">';
            
            // Formatear la información de la factura
            htmlFormateado += `<div class="historial-factura">${facturaInfo.trim()}</div>`;
            
            // Formatear los productos
            htmlFormateado += '<div class="historial-productos">';
            
            // Dividir y formatear cada producto
            const productos = productosInfo.split(',');
            productos.forEach(producto => {
                htmlFormateado += `<span class="historial-producto-item">${producto.trim()}</span>`;
            });
            
            htmlFormateado += '</div></div>';
        } else {
            // Si la línea no tiene el formato esperado, mostrarla tal cual
            htmlFormateado += `<div class="historial-entrada">${linea}</div>`;
        }
    });
    
    return htmlFormateado;
}

// Añadir esta función a tu JavaScript
function verHistorialCompleto(idCliente) {
    // Obtener el cliente
    fetch(`/clientes/api/clientes/${idCliente}`)
        .then(response => response.json())
        .then(data => {
            // Crear y mostrar un modal con el historial completo
            const historialFormateado = formatearHistorial(data.historial_compras);
            
            // Crear modal
            const modalHTML = `
                <div class="modal fade" id="historialModal" tabindex="-1" role="dialog" aria-labelledby="historialModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="historialModalLabel">Historial de Compras - ${data.nombre_cliente}</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                <div class="historial-container">
                                    ${historialFormateado}
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cerrar</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Añadir el modal al body
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Mostrar el modal
            $('#historialModal').modal('show');
            
            // Eliminar el modal cuando se cierra
            $('#historialModal').on('hidden.bs.modal', function () {
                $(this).remove();
            });
        })
        .catch(error => console.error('Error:', error));
}

// Función para actualizar la tabla de clientes
function actualizarTablaClientes(clientes) {
    const tbody = document.getElementById('clientTable');
    if (!tbody) {
        console.error('No se encontró el elemento clientTable');
        return;
    }
    
    tbody.innerHTML = '';
    
    if (clientes.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="7" class="text-center">No hay clientes registrados</td>';
        tbody.appendChild(tr);
        return;
    }

    clientes.forEach(cliente => {
        // Crear un resumen del historial (mostrar solo la última compra o un conteo)
        let historialResumen = 'No aplica';
        if (cliente.historial_compras && cliente.historial_compras !== 'No aplica') {
            const lineas = cliente.historial_compras.split('\n');
            if (lineas.length > 0) {
                historialResumen = `${lineas.length} compras - Última: ${lineas[lineas.length - 1].split(':')[0].trim()}`;
            }
        }
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${cliente.id_cliente} (${cliente.tipo_documento})</td>
            <td>${cliente.nombre_cliente || ''}</td>
            <td>${cliente.telefono || ''}</td>
            <td>${cliente.correo_electronico || ''}</td>
            <td class="historial-cell">
                ${historialResumen}
                ${cliente.historial_compras && cliente.historial_compras !== 'No aplica' 
                    ? `<button class="btn btn-link btn-sm" onclick="verHistorialCompleto('${cliente.id_cliente}')">Ver historial completo</button>` 
                    : ''}
            </td>
            <td class="preferencias-cell">${cliente.preferencias || 'No aplica'}</td>
            <td>
                <div class="btn-action-container">
                    <button class="btn btn-primary btn-sm" onclick="editarCliente('${cliente.id_cliente}')">
                        Editar
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="eliminarCliente('${cliente.id_cliente}')">
                        Eliminar
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Función para abrir el modal de cliente
function openClientModal() {
    editMode = false;
    editClientId = null;
    document.getElementById('clientForm').reset();
    document.getElementById('clientCedula').disabled = false;
    document.getElementById('clientTipoDoc').disabled = false;
    document.getElementById('clientModalLabel').textContent = 'Añadir Cliente';
    $('#clientModal').modal('show');
}

// Función para cerrar el modal
function closeClientModal() {
    $('#clientModal').modal('hide');
    document.getElementById('clientForm').reset();
}

// Función para guardar un cliente
async function guardarCliente(event) {
    event.preventDefault();
    
    try {
        // Validar que se haya seleccionado un tipo de documento
        const tipoDocumento = document.getElementById('clientTipoDoc').value;
        if (!tipoDocumento) {
            mostrarMensaje('Por favor seleccione un tipo de documento', 'error');
            return;
        }

        // Obtener los datos del formulario
        const formData = {
            id_cliente: document.getElementById('clientCedula').value,
            tipo_documento: tipoDocumento,
            nombre_cliente: document.getElementById('clientName').value,
            telefono: document.getElementById('clientPhone').value,
            correo_electronico: document.getElementById('clientContact').value,
            historial_compras: document.getElementById('clientHistory').value || null,
            preferencias: document.getElementById('clientPreferens').value || null
        };

        console.log('Enviando datos:', formData);  // Para debug

        const url = editMode 
            ? `/clientes/api/clientes/${editClientId}`
            : '/clientes/api/clientes/crear';
            
        const method = editMode ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al procesar la solicitud');
        }

        // Mostrar mensaje de éxito
        mostrarMensaje(data.message || 'Cliente guardado exitosamente', 'success');
        
        // Cerrar el modal y recargar la lista de clientes
        closeClientModal();
        await cargarClientes();
        
    } catch (error) {
        console.error('Error detallado:', error);
        mostrarMensaje(error.message || 'Error al guardar el cliente', 'error');
    }
}

// Función para editar un cliente
async function editarCliente(id) {
    try {
        console.log('Editando cliente:', id);
        const response = await fetch(`/clientes/api/clientes/${id}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al cargar los datos del cliente');
        }

        const cliente = await response.json();
        console.log('Datos del cliente recibidos:', cliente);
        
        // Llenar el formulario con los datos del cliente
        document.getElementById('clientCedula').value = cliente.id_cliente;
        document.getElementById('clientTipoDoc').value = cliente.tipo_documento;
        document.getElementById('clientName').value = cliente.nombre_cliente;
        document.getElementById('clientPhone').value = cliente.telefono || '';
        document.getElementById('clientContact').value = cliente.correo_electronico || '';
        document.getElementById('clientHistory').value = cliente.historial_compras || '';
        document.getElementById('clientPreferens').value = cliente.preferencias || '';

        // Configurar el modo de edición
        editMode = true;
        editClientId = id;
        
        // Deshabilitar campos que no deberían cambiar
        document.getElementById('clientCedula').disabled = true;
        document.getElementById('clientTipoDoc').disabled = true;
        
        // Actualizar el título del modal
        document.getElementById('clientModalLabel').textContent = 'Editar Cliente';
        
        // Mostrar el modal
        $('#clientModal').modal('show');
    } catch (error) {
        console.error('Error al editar cliente:', error);
        mostrarMensaje(error.message || 'Error al cargar los datos del cliente', 'error');
    }
}

// Función para eliminar un cliente
async function eliminarCliente(id) {
    if (!confirm('¿Está seguro de que desea eliminar este cliente?')) {
        return;
    }

    try {
        const response = await fetch(`/clientes/api/clientes/${id}/desactivar`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Error al eliminar el cliente');
        }

        const data = await response.json();
        mostrarMensaje(data.message, 'success');
        await cargarClientes();
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error al eliminar el cliente', 'error');
    }
}

// Función para mostrar mensajes
function mostrarMensaje(mensaje, tipo) {
    console.log(`Mostrando mensaje: ${mensaje} (${tipo})`);  // Para debug
    const alertClase = tipo === 'success' ? 'alert-success' : 'alert-danger';
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClase} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }

    // Eliminar la alerta después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}


// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log('Página cargada, iniciando carga de clientes...');
    cargarClientes();
    
    // Event listener para el formulario de cliente
    const form = document.getElementById('clientForm');
    if (form) {
        form.addEventListener('submit', guardarCliente);
    }
    
    // Event listener para el botón de añadir cliente
    const addButton = document.querySelector('.btn-success');
    if (addButton) {
        addButton.addEventListener('click', openClientModal);
    }
    
    // Event listener para la búsqueda
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#clientTable tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
});
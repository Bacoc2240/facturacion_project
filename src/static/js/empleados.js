// Primero, añadimos la función debounce que faltaba
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Configuración y variables globales
const ROUTES = {
    crear: '/empleados/crear',
    lista: '/empleados/api/lista',
    editar: (id) => `/empleados/editar/${id}`,
    suspender: (id) => `/empleados/suspender/${id}`,
    reactivar: (id) => `/empleados/reactivar/${id}`
};

let editMode = false;
let editEmployeeRef = null;

// Añadimos la función openEmployeeModal que faltaba
function openEmployeeModal() {
    // Resetear el modo de edición
    editMode = false;
    editEmployeeRef = null;
    
    // Limpiar el formulario
    const form = document.getElementById('employeeForm');
    if (form) {
        form.reset();
    }
    
    // Cambiar el título del modal
    const modalTitle = document.querySelector('#employeeModal .modal-title');
    if (modalTitle) {
        modalTitle.textContent = 'Crear Empleado';
    }
    
    // Abrir el modal usando jQuery (Bootstrap 4.3.1)
    $('#employeeModal').modal('show');
}

// Función principal de inicialización
function initializeEmployees() {
    // Cargar empleados iniciales
    cargarEmpleados();
    
    // Inicializar manejadores de eventos
    setupEventListeners();
}

// Configuración de event listeners
function setupEventListeners() {
    // Formulario de creación
    const form = document.getElementById('employeeForm');
    if (form) {
        form.addEventListener('submit', handleSubmit);
    }

    // Búsqueda
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase();
            buscarEmpleados(searchTerm);
        }, 300));
    }

    // Añadir manejador para el botón de añadir empleado
    const addButton = document.querySelector('[onclick="openEmployeeModal()"]');
    if (addButton) {
        // Remover el onclick del HTML y añadirlo aquí
        addButton.removeAttribute('onclick');
        addButton.addEventListener('click', openEmployeeModal);
    }
}
// Función para cargar empleados
async function cargarEmpleados() {
    try {
        const response = await fetch(ROUTES.lista);
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const empleados = await response.json();
        actualizarTablaEmpleados(empleados);
    } catch (error) {
        console.error('Error al cargar empleados:', error);
        mostrarAlerta('Error al cargar la lista de empleados', 'danger');
    }
}

// Función para actualizar la tabla de empleados
function actualizarTablaEmpleados(empleados) {
    const tabla = document.querySelector('#employeeTable');
    if (!tabla) return;

    tabla.innerHTML = empleados.map(empleado => `
        <tr>
            <td>${empleado.id_empleado}</td>
            <td>${empleado.nombre_apellidos}</td>
            <td>${empleado.numero_identificacion}</td>
            <td>${empleado.correo_electronico}</td>
            <td>${empleado.telefono}</td>
            <td>${empleado.cargo}</td>
            <td>${formatearFecha(empleado.fecha_contratacion)}</td>
            <td>${empleado.activo ? 'Sí' : 'No'}</td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="editarEmpleado(${empleado.id_empleado})">
                    Editar
                </button>
                ${empleado.activo ? 
                    `<button class="btn btn-danger btn-sm" onclick="suspenderEmpleado(${empleado.id_empleado})">
                        Suspender
                     </button>` :
                    `<button class="btn btn-success btn-sm" onclick="reactivarEmpleado(${empleado.id_empleado})">
                        Reactivar
                     </button>`
                }
            </td>
        </tr>
    `).join('');
}

// Manejador del formulario de creación
async function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        const response = await fetch(ROUTES.crear, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Error al crear el empleado');
        }

        // Cerrar modal usando jQuery (Bootstrap 4)
        $('#employeeModal').modal('hide');
        
        // Limpiar formulario y recargar datos
        event.target.reset();
        await cargarEmpleados();
        mostrarAlerta('Empleado creado exitosamente', 'success');
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta(error.message, 'danger');
    }
}

// Función para mostrar alertas (Bootstrap 4)
function mostrarAlerta(mensaje, tipo) {
    const alertaHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
            ${mensaje}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    
    const contenedor = document.querySelector('.container-fluid');
    if (contenedor) {
        contenedor.insertAdjacentHTML('afterbegin', alertaHTML);
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            $('.alert').alert('close');
        }, 5000);
    }
}

// Configuración de event listeners
function setupEventListeners() {
    // Formulario de creación
    const form = document.getElementById('employeeForm');
    if (form) {
        form.addEventListener('submit', handleSubmit);
    }

    // Búsqueda
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase();
            buscarEmpleados(searchTerm);
        }, 300));
    }
}

// Función de ayuda para formatear fechas
function formatearFecha(fecha) {
    return new Date(fecha).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeEmployees);
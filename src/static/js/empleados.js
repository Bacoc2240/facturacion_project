// Utilidades
const ROUTES = {
    lista: '/empleados/api/lista',
    obtener: (id) => `/empleados/${id}`,
    editar: (id) => `/empleados/${id}/editar`,
    suspender: (id) => `/empleados/${id}/suspender`,
    reactivar: (id) => `/empleados/${id}/reactivar`,
    crear: '/empleados/crear',
    suspendidos: '/empleados/suspendidos'   

};

// Función de utilidad para retrasar la ejecución de funciones
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// Función para formatear fechas de manera consistente
function formatearFecha(fechaStr) {
    if (!fechaStr) return '';
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Gestión de interfaz de usuario
const UI = {
    // Función para mostrar alertas
    mostrarAlerta(mensaje, tipo) {
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
            setTimeout(() => $('.alert').alert('close'), 5000);
        }
    },

    // Función para abrir el modal de creación
    openEmployeeModal() {
        const form = document.getElementById('employeeForm');
        if (form) form.reset();
        
        const modalTitle = document.querySelector('#employeeModal .modal-title');
        if (modalTitle) modalTitle.textContent = 'Crear Empleado';
        
        $('#employeeModal').modal('show');
    }
};

// Gestión de empleados
const EmpleadosManager = {
    // Cargar empleados
    async cargarEmpleados() {
        try {
            const response = await fetch(ROUTES.lista);
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            
            const empleados = await response.json();
            // Filtrar solo empleados activos
            const empleadosActivos = empleados.filter(e => e.activo);
            this.actualizarTablaEmpleados(empleadosActivos);
        } catch (error) {
            console.error('Error al cargar empleados:', error);
            UI.mostrarAlerta('Error al cargar la lista de empleados', 'danger');
        }
    },

    async cargarEmpleadosSuspendidos() {
        try {
            const response = await fetch(ROUTES.suspendidos);
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            
            const empleados = await response.json();
            this.actualizarTablaEmpleados(empleados, true);
        } catch (error) {
            console.error('Error al cargar empleados suspendidos:', error);
            UI.mostrarAlerta('Error al cargar empleados suspendidos', 'danger');
        }
    },


    // Actualizar tabla de empleados
    actualizarTablaEmpleados(empleados, esSuspendidos = false) {
        const tbody = document.querySelector('table tbody');
        if (!tbody) return;

        tbody.innerHTML = empleados.map(empleado => `
            <tr data-id="${empleado.id_empleado}">
                <td>${empleado.id_empleado}</td>
                <td>${empleado.nombre_apellidos}</td>
                <td>${empleado.numero_identificacion}</td>
                <td>${empleado.correo_electronico}</td>
                <td>${empleado.telefono}</td>
                <td>${empleado.cargo}</td>
                <td>${formatearFecha(empleado.fecha_contratacion)}</td>
                <td>${empleado.activo ? 'Sí' : 'No'}</td>
                <td class="text-center">
                    ${!esSuspendidos ? `
                        <button class="btn btn-warning btn-sm edit-btn" data-id="${empleado.id_empleado}">
                            Editar
                        </button>
                        <button class="btn btn-danger btn-sm suspend-btn" data-id="${empleado.id_empleado}">
                            Suspender
                        </button>
                    ` : `
                        <button class="btn btn-success btn-sm reactivate-btn" data-id="${empleado.id_empleado}">
                            Reactivar
                        </button>
                    `}
                </td>
            </tr>
        `).join('');

        this.setupTableEventListeners();
    },

    // Gestionar búsqueda de empleados
    buscarEmpleados(searchTerm) {
        const rows = document.querySelectorAll('table tbody tr');
        rows.forEach(row => {
            row.style.display = !searchTerm || 
                row.textContent.toLowerCase().includes(searchTerm.toLowerCase()) 
                ? '' : 'none';
        });
    },

    // Configurar event listeners
    setupEventListeners() {
        // Formulario de creación
        const form = document.getElementById('employeeForm');
        if (form) {
            form.removeEventListener('submit', this.handleSubmit);
            form.addEventListener('submit', this.handleSubmit.bind(this));
        }

        // Búsqueda
        const searchInput = document.getElementById('search');
        if (searchInput) {
            const debouncedSearch = debounce(
                (e) => this.buscarEmpleados(e.target.value.toLowerCase()), 
                300
            );
            searchInput.removeEventListener('input', debouncedSearch);
            searchInput.addEventListener('input', debouncedSearch);
        }

        // Botón de añadir empleado
        const addButton = document.querySelector('[data-action="open-modal"]');
        if (addButton) {
            addButton.removeEventListener('click', UI.openEmployeeModal);
            addButton.addEventListener('click', UI.openEmployeeModal);
        }

        // Botones para alternar entre empleados activos y suspendidos
        const btnActivos = document.getElementById('btnEmpleadosActivos');
        const btnSuspendidos = document.getElementById('btnEmpleadosSuspendidos');

        if (btnActivos) {
            btnActivos.addEventListener('click', () => this.cargarEmpleados());
        }

        if (btnSuspendidos) {
            btnSuspendidos.addEventListener('click', () => this.cargarEmpleadosSuspendidos());
        }
    },

    // Configurar event listeners de la tabla
    setupTableEventListeners() {
        // Botones de editar
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.editarEmpleado(button.dataset.id);
            });
        });

        // Botones de suspender
        document.querySelectorAll('.suspend-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.suspenderEmpleado(button.dataset.id);
            });
        });

        // Botones de reactivar
        document.querySelectorAll('.reactivate-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.reactivarEmpleado(button.dataset.id);
            });
        });
        
    },

    // Manejadores de acciones
    async handleSubmit(event) {
        event.preventDefault();
        const formData = new FormData(event.target);

        try {
            const response = await fetch(ROUTES.crear, {
                method: 'POST',
                body: formData,
                headers: { 'Accept': 'application/json' }
            });

            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            $('#employeeModal').modal('hide');
            event.target.reset();
            UI.mostrarAlerta('Empleado creado exitosamente', 'success');
            await this.cargarEmpleados();
        } catch (error) {
            console.error('Error:', error);
            UI.mostrarAlerta(error.message, 'danger');
        }
    },

    // Función para editar empleado
    async editarEmpleado(id) {
        try {
            // Obtener datos del empleado del servidor
            const response = await fetch(ROUTES.obtener(id));
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al obtener datos del empleado');
            }
            
            const empleado = await response.json();
            
            // Obtener referencia al formulario de edición
            const form = document.getElementById('editEmployeeForm');
            if (!form) {
                throw new Error('No se encontró el formulario de edición');
            }

            // Mapeo de campos del empleado a IDs del formulario
            const fields = {
                'edit_id_empleado': empleado.id_empleado,
                'edit_nombre_apellidos': empleado.nombre_apellidos,
                'edit_numero_identificacion': empleado.numero_identificacion,
                'edit_correo_electronico': empleado.correo_electronico,
                'edit_telefono': empleado.telefono,
                'edit_fecha_contratacion': empleado.fecha_contratacion?.split('T')[0] || '',
                'edit_cargo': empleado.cargo
            };

            // Rellenar el formulario con los datos del empleado
            Object.entries(fields).forEach(([fieldId, value]) => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.value = value;
                } else {
                    console.warn(`Campo no encontrado: ${fieldId}`);
                }
            });
            
            // Mostrar el modal de edición
            $('#editEmployeeModal').modal('show');
            
            // Configurar el manejador del formulario de edición
            this.setupEditFormHandler(id);
            
        } catch (error) {
            console.error('Error al editar:', error);
            UI.mostrarAlerta(`Error al cargar datos del empleado: ${error.message}`, 'danger');
        }
    },

    // Configurar el manejador del formulario de edición
    setupEditFormHandler(id) {
        const form = document.getElementById('editEmployeeForm');
        if (!form) return;

        // Remover manejador anterior si existe
        const oldHandler = form._submitHandler;
        if (oldHandler) {
            form.removeEventListener('submit', oldHandler);
        }

        // Crear y asignar nuevo manejador
        const submitHandler = async (event) => {
            event.preventDefault();
            await this.handleEditSubmit(id, new FormData(form));
        };

        form._submitHandler = submitHandler;
        form.addEventListener('submit', submitHandler);
    },

    // Manejar el envío del formulario de edición
    async handleEditSubmit(id, formData) {
        try {
            const response = await fetch(ROUTES.editar(id), {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Error al actualizar empleado');
            }
            
            // Cerrar modal y actualizar datos
            $('#editEmployeeModal').modal('hide');
            await this.cargarEmpleados();
            UI.mostrarAlerta('Empleado actualizado exitosamente', 'success');
            
        } catch (error) {
            console.error('Error:', error);
            UI.mostrarAlerta(error.message, 'danger');
        }
    },

    // Función para suspender empleado
    async suspenderEmpleado(id) {
        try {
            if (!confirm('¿Está seguro que desea suspender este empleado?')) {
                return;
            }

            const response = await fetch(ROUTES.suspender(id), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al suspender el empleado');
            }

            // Recargar solo empleados activos
            await this.cargarEmpleados();
            UI.mostrarAlerta('Empleado suspendido exitosamente', 'success');

        } catch (error) {
            console.error('Error al suspender empleado:', error);
            UI.mostrarAlerta(`Error al suspender empleado: ${error.message}`, 'danger');
        }
    },


    // Función para reactivar empleado
    async reactivarEmpleado(id) {
        try {
            if (!confirm('¿Está seguro que desea reactivar este empleado?')) {
                return;
            }

            const response = await fetch(ROUTES.reactivar(id), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al reactivar el empleado');
            }

            await this.cargarEmpleados();
            UI.mostrarAlerta('Empleado reactivado exitosamente', 'success');

        } catch (error) {
            console.error('Error al reactivar empleado:', error);
            UI.mostrarAlerta(`Error al reactivar empleado: ${error.message}`, 'danger');
        }
    }
};

// Inicialización de la aplicación
document.addEventListener('DOMContentLoaded', () => {
    EmpleadosManager.cargarEmpleados();
    EmpleadosManager.setupEventListeners();
});
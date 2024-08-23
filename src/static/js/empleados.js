// Datos iniciales de clientes (puedes sustituir esto por una fuente de datos real)
let employees = [
    {
        id: 1111900765,
        name: 'Leidy Castillo',
        phone: '3113452244',
        contact: 'leidy.castillo@example.com',
        position: 'vendedor',
    },
    {
        id: 68900321,
        name: 'Julia Parada',
        phone: '3009687854',
        contact: 'julia.parada@example.com',
        position: 'vendedor',
              
    },
    {
        id: 60441678,
        name: 'Johana Sanchez',
        phone: '3017724351',
        contact: 'johana.sanchez@example.com',
        position: 'administrador',
        
    }

];
// Variables globales para el modo de edición y referencia al empleado a editar
let editMode = false;
let editEmployeeRef = null;


// Referencias a elementos del DOM
const employeeTable = document.getElementById('employeeTable');
const employeeForm = document.getElementById('employeeForm');
const searchInput = document.getElementById('search');

// Función para abrir el modal de empleado
function openEmployeeModal() {
    editMode = false;
    editEmployeeRef = null;
    employeeForm.reset(); // Limpiar el formulario
    $('#employeeModal').modal('show'); // Mostrar el modal
}

// Función para renderizar la tabla de empleados
function renderEmployeeTable() {
    employeeTable.innerHTML = '';
    employees.forEach((employee, index) => {
        const row = `
            <tr>
                <td>${employee.id}</td>
                <td>${employee.name}</td>
                <td>${employee.phone}</td>
                <td>${employee.contact}</td>
                <td>${employee.position}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="editEmployee(${index})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteEmployee(${index})">Eliminar</button>
                </td>
            </tr>
        `;
        employeeTable.insertAdjacentHTML('beforeend', row);
    });
}

// Función para agregar un nuevo empleado o editar uno existente
employeeForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const newEmployee = {
        id: document.getElementById('employeeId').value,
        name: document.getElementById('employeeName').value,
        phone: document.getElementById('employeePhone').value,
        contact: document.getElementById('employeeContact').value,
        position: document.getElementById('employeePosition').value,
        
    };

    if (editMode) {
        employees[editEmployeeRef] = newEmployee;
    } else {
        employees.push(newEmployee);
    }

    $('#employeeModal').modal('hide'); // Ocultar el modal
    renderEmployeeTable(); // Renderizar la tabla de empleados
});

// Función para editar un empleado existente
function editEmployee(index) {
    editMode = true;
    editEmployeeRef = index;
    const employee = employees[index];
    document.getElementById('employeeId').value = employee.id;
    document.getElementById('employeeName').value = employee.name;
    document.getElementById('employeePhone').value = employee.phone;
    document.getElementById('employeeContact').value = employee.contact;
    document.getElementById('employeePosition').value = employee.position;
    $('#employeeModal').modal('show'); // Mostrar el modal
}

// Función para eliminar un empleado 
function deleteEmployee(index) {
    if (confirm('¿Estás seguro de que deseas eliminar este empleado?')) {
        employees.splice(index, 1);
        renderEmployeeTable(); // Renderizar la tabla de empleados
    }
}

// Función para filtrar empleados
searchInput.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const filteredEmployees = employees.filter(employee => 
        employee.name.toLowerCase().includes(searchTerm) || 
        employee.id.toString().toLowerCase().includes(searchTerm) ||
        employee.phone.toLowerCase().includes(searchTerm) ||
        employee.contact.toLowerCase().includes(searchTerm) ||
        employee.position.toLowerCase().includes(searchTerm)
    );
    renderEmployeeTable(filteredEmployees);
});


// Función para renderizar la tabla de empleados
function renderEmployeeTable(employeesToRender = employees) {
    employeeTable.innerHTML = '';
    employeesToRender.forEach((employee, index) => {
        const row = `
            <tr>
                <td>${employee.id}</td>
                <td>${employee.name}</td>
                <td>${employee.phone}</td>
                <td>${employee.contact}</td>
                <td>${employee.position}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="editEmployee(${index})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteEmployee(${index})">Eliminar</button>
                </td>
            </tr>
        `;
        employeeTable.insertAdjacentHTML('beforeend', row);
    });
}


// Renderizar la tabla de empleados al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    renderEmployeeTable();
});

// Función para cerrar sesión
function cerrarSesion() {
    // añadir lógica para cerrar sesión
    // como limpiar datos de sesión, cookies, etc.

    // Redirigir al usuario a la página de login
    window.location.href = '/';
}

// Event listener para el enlace de cerrar sesión
$(document).ready(function() {
    $('#logout').on('click', function(e) {
        e.preventDefault(); // Prevenir el comportamiento predeterminado del enlace
        cerrarSesion();
    });
});

// Datos iniciales de clientes (puedes sustituir esto por una fuente de datos real)
let clientes = [
    {
        id: 1115678450,
        nombre: 'Juan Pérez',
        telefono: '3113452244',
        contacto: 'juan.perez@example.com',
        historial: 'Compras recientes: Acqua de Gio -100ml, spirit - 30ml',
        preferencias: 'spirit - 30ml'
    },
    {
        id: 68256442,
        nombre: 'Ana Gómez',
        telefono: '3009687854',
        contacto: 'ana.gomez@example.com',
        historial: 'Compras recientes: 90210 sport - 100ml',
        preferencias: 'idole - 75ml'
        
    },
    {
        id: 80908765,
        nombre: 'Raul Rojas',
        telefono: '3017724351',
        contacto: 'raul.rojas@example.com',
        historial: 'Compras recientes: Antonio - 15ml, spirit - 30ml',
        preferencias: 'idole - 75ml'
    }

];

let editMode = false;
let editClientId = null;

// Inicialización del modal
const clientModal = $('#clientModal');

// Función para generar un ID único basado en la cédula
function generateUniqueId(cedula) {
    // Verificar si ya existe un cliente con esta cédula
    const existingClient = clientes.find(cliente => cliente.id === parseInt(cedula));
    if (existingClient) {
        alert('Ya existe un cliente con esta cédula.');
        return null;
    }
    return parseInt(cedula);
}

// Función para abrir el modal y resetear el formulario
function openClientModal() {
    editMode = false;
    editClientId = null;
    $('#clientForm')[0].reset(); // Limpiar el formulario
    $('#clientCedula').prop('disabled', false);
    $('#clientModalLabel').text('Añadir Cliente');
    clientModal.modal('show');
}

// Función para cerrar el modal
function closeClientModal() {
    clientModal.modal('hide');
}

// Función para listar clientes
function listClients() {
    const clientTable = $('#clientTable');
    clientTable.empty();

    clientes.forEach(cliente => {
        clientTable.append(`
            <tr>
                <td>${cliente.id}</td>
                <td>${cliente.nombre}</td>
                <td>${cliente.telefono}</td>
                <td>${cliente.contacto}</td>
                <td>${cliente.historial}</td>
                <td>${cliente.preferencias}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="editClient(${cliente.id})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteClient(${cliente.id})">Eliminar</button>
                </td>
            </tr>
        `);
    });
}

function saveClient(event) {
    event.preventDefault();

    const cedula = $('#clientCedula').val();
    const nombre = $('#clientName').val();
    const telefono = $('#clientPhone').val();
    const contacto = $('#clientContact').val();
    const historial = $('#clientHistory').val();
    const preferencias = $('#clientPreferens').val();

    if (editMode) {
        // Editar cliente existente
        const cliente = clientes.find(cliente => cliente.id === editClientId);
        cliente.nombre = nombre;
        cliente.telefono = telefono;
        cliente.contacto = contacto;
        cliente.historial = historial;
        cliente.preferencias = preferencias;
    } else {
        // Añadir nuevo cliente
        const newId = generateUniqueId(cedula);
        if (newId === null) {
            return; // Si el ID no es válido, no continuamos
        }
        const newClient = {
            id: newId,
            nombre,
            telefono,
            contacto,
            historial,
            preferencias
        };
        clientes.push(newClient);
    }

    closeClientModal();
    listClients();
}


// Función para editar un cliente
function editClient(id) {
    editMode = true;
    editClientId = id;

    const cliente = clientes.find(cliente => cliente.id === id);

    $('#clientCedula').val(cliente.id);
    $('#clientCedula').prop('disabled', true);
    $('#clientName').val(cliente.nombre);
    $('#clientPhone').val(cliente.telefono);
    $('#clientContact').val(cliente.contacto);
    $('#clientHistory').val(cliente.historial);
    $('#clientPreferens').val(cliente.preferencias);
    $('#clientModalLabel').text('Editar Cliente');
    clientModal.modal('show');
}

// Función para eliminar un cliente con confirmación
function deleteClient(id) {
    if (confirm('¿Estás seguro de que deseas eliminar este cliente?')) {
        clientes = clientes.filter(cliente => cliente.id !== id);
        listClients();
    }
}


// Función para buscar clientes
function searchClients() {
    const searchTerm = $('#search').val().toLowerCase();
    const filteredClients = clientes.filter(cliente =>
        cliente.nombre.toLowerCase().includes(searchTerm) ||
        cliente.telefono.includes(searchTerm) ||
        cliente.contacto.toLowerCase().includes(searchTerm) ||
        cliente.historial.toLowerCase().includes(searchTerm)
    );

    const clientTable = $('#clientTable');
    clientTable.empty();

    filteredClients.forEach(cliente => {
        clientTable.append(`
            <tr>
                <td>${cliente.id}</td>
                <td>${cliente.nombre}</td>
                <td>${cliente.telefono}</td>
                <td>${cliente.contacto}</td>
                <td>${cliente.historial}</td>
                <td>${cliente.preferencias}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="editClient(${cliente.id})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteClient(${cliente.id})">Eliminar</button>
                </td>
            </tr>
        `);
    });
}

// Event listener para el formulario de cliente
$('#clientForm').on('submit', saveClient);

// Event listener para el campo de búsqueda
$('#search').on('input', searchClients);

// Inicializar el listado de clientes al cargar la página
$(document).ready(() => {
    listClients();
});

// Función para cerrar sesión
function cerrarSesion() {
    // añadir lógica para cerrar sesión
    // como limpiar datos de sesión, cookies, etc.

    // Redirigir al usuario a la página de login
    window.location.href = 'login.html';
}

// Event listener para el enlace de cerrar sesión
$(document).ready(function() {
    $('#logout').on('click', function(e) {
        e.preventDefault(); // Prevenir el comportamiento predeterminado del enlace
        cerrarSesion();
    });
});

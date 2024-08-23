// facturas.js

// Datos iniciales de facturas (puedes sustituir esto por una fuente de datos real)
let facturas = [
    {
        id: 'F001',
        fechaPago: '2024-07-22 14:00',
        idCliente: '90208976',
        nombreCliente: 'Juan Perez',
        fechaVencimiento: '2024-07-22',
        nombreVendedor: 'Leidy Castillo',
        formaPago: 'Efectivo',
        productos: [
            { unidades: 2, nombre: 'Antomnio - 15ml', valorIVA: 0, total: 90000 },
            { unidades: 1, nombre: 'Fresh Escape - 50ml', valorIVA: 0, total: 48000 }
        ],
        subtotal: 138000,
        valorIVA: 0,
        descuento: 0,
        total: 138000,
        totalLetras: 'Ciento treinta y ocho mil pesos m/l'
    },
    {
        id: 'F002',
        fechaPago: '2024-07-22 14:50',
        idCliente: '60789123',
        nombreCliente: 'Ana Minta Gómez',
        fechaVencimiento: '2024-07-22',
        nombreVendedor: 'Leidy Castillo',
        formaPago: 'Transferencia',
        productos: [
            { unidades: 1, nombre: 'Love Love Love - 80ml', valorIVA: 0, total: 130000 }
        ],
        subtotal: 130000,
        valorIVA: 0,
        descuento: 0,
        total: 130000,
        totalLetras: 'Ciento treinta mil pesos m/l'
    }
];

// Variables para el modo edición
let editMode = false;
let editFacturaRef = null;

// Referencias a elementos del DOM
const facturaForm = document.getElementById('facturaForm');
const facturaTable = document.getElementById('facturaTable');
const searchInput = document.getElementById('search');

// Función para abrir el modal de creación de factura
function openFacturaModal() {
    editMode = false;
    editFacturaRef = null;
    facturaForm.reset();
    $('#facturaModal').modal('show');
}

// Función para renderizar la tabla de facturas
function renderFacturaTable(filteredFacturas = facturas) {
    facturaTable.innerHTML = '';
    filteredFacturas.forEach((factura) => {
        const row = `
            <tr>
                <td>${factura.id}</td>
                <td>${factura.nombreCliente}</td>
                <td>${factura.fechaPago}</td>
                <td>${factura.total}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="viewFactura('${factura.id}')">Ver</button>
                    <button class="btn btn-warning btn-sm" onclick="editFactura('${factura.id}')">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteFactura('${factura.id}')">Eliminar</button>
                </td>
            </tr>
        `;
        facturaTable.insertAdjacentHTML('beforeend', row);
    });
}

// Función para agregar o editar una factura
facturaForm.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const newFactura = {
        id: document.getElementById('facturaId').value,
        fechaPago: document.getElementById('fechaPago').value,
        idCliente: document.getElementById('idCliente').value,
        nombreCliente: document.getElementById('nombreCliente').value,
        fechaVencimiento: document.getElementById('fechaVencimiento').value,
        nombreVendedor: document.getElementById('nombreVendedor').value,
        formaPago: document.getElementById('formaPago').value,
        productos: [],
        subtotal: parseFloat(document.getElementById('subtotal').value),
        valorIVA: parseFloat(document.getElementById('valorIVA').value),
        descuento: parseFloat(document.getElementById('descuento').value),
        total: parseFloat(document.getElementById('total').value),
        totalLetras: document.getElementById('totalLetras').value
    };

    // Obtener productos del formulario
    document.querySelectorAll('.producto-row').forEach(row => {
        const producto = {
            unidades: parseInt(row.querySelector('.producto-unidades').value),
            nombre: row.querySelector('.producto-nombre').value,
            valorIVA: parseFloat(row.querySelector('.producto-valorIVA').value),
            total: parseFloat(row.querySelector('.producto-total').value)
        };
        newFactura.productos.push(producto);
    });

    if (editMode) {
        const index = facturas.findIndex(f => f.id === editFacturaRef);
        if (index !== -1) {
            facturas[index] = newFactura;
        }
    } else {
        facturas.push(newFactura);
    }

    $('#facturaModal').modal('hide');
    renderFacturaTable();
});

// Función para ver una factura
function viewFactura(id) {
    const factura = facturas.find(f => f.id === id);
    if (factura) {
        // Aquí puedes implementar la lógica para mostrar los detalles de la factura
        console.log('Ver factura:', factura);
        alert(`Detalles de la factura ${factura.id}:\n${JSON.stringify(factura, null, 2)}`);
    }
}

// Función para editar una factura
function editFactura(id) {
    const factura = facturas.find(f => f.id === id);
    if (factura) {
        editMode = true;
        editFacturaRef = id;
        
        // Llenar el formulario con los datos de la factura
        document.getElementById('facturaId').value = factura.id;
        document.getElementById('nombreCliente').value = factura.nombreCliente;
        document.getElementById('idCliente').value = factura.idCliente;
        document.getElementById('fechaPago').value = factura.fechaPago;
        document.getElementById('fechaVencimiento').value = factura.fechaVencimiento;
        document.getElementById('nombreVendedor').value = factura.nombreVendedor;
        document.getElementById('formaPago').value = factura.formaPago;
        document.getElementById('subtotal').value = factura.subtotal;
        document.getElementById('valorIVA').value = factura.valorIVA;
        document.getElementById('descuento').value = factura.descuento;
        document.getElementById('total').value = factura.total;
        document.getElementById('totalLetras').value = factura.totalLetras;

        // Renderizar productos en el formulario
        const productosContainer = document.getElementById('productosContainer');
        productosContainer.innerHTML = '';
        factura.productos.forEach((producto, index) => {
            agregarProducto();
            const row = productosContainer.children[index];
            row.querySelector('.producto-unidades').value = producto.unidades;
            row.querySelector('.producto-nombre').value = producto.nombre;
            row.querySelector('.producto-valorIVA').value = producto.valorIVA;
            row.querySelector('.producto-total').value = producto.total;
        });

        $('#facturaModal').modal('show');
    }
}

// Función para agregar un nuevo producto al formulario
function agregarProducto() {
    const productosContainer = document.getElementById('productosContainer');
    const productoIndex = document.querySelectorAll('.producto-row').length;
    const productoHTML = `
        <div class="form-row producto-row">
            <div class="form-group col-md-3">
                <input type="number" class="form-control producto-unidades" placeholder="Unidades" required>
            </div>
            <div class="form-group col-md-3">
                <input type="text" class="form-control producto-nombre" placeholder="Nombre" required>
            </div>
            <div class="form-group col-md-3">
                <input type="number" class="form-control producto-valorIVA" placeholder="Valor IVA" required>
            </div>
            <div class="form-group col-md-3">
                <input type="number" class="form-control producto-total" placeholder="Total" required>
            </div>
        </div>
    `;
    productosContainer.insertAdjacentHTML('beforeend', productoHTML);
}

// Función para eliminar una factura
function deleteFactura(id) {
    if (confirm('¿Estás seguro de que deseas eliminar esta factura?')) {
        const index = facturas.findIndex(f => f.id === id);
        if (index !== -1) {
            facturas.splice(index, 1);
            renderFacturaTable();
        }
    }
}

// Función para filtrar facturas
searchInput.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const filteredFacturas = facturas.filter(factura => 
        factura.id.toLowerCase().includes(searchTerm) || 
        factura.nombreCliente.toLowerCase().includes(searchTerm)
    );
    renderFacturaTable(filteredFacturas);
});

// Renderizar la tabla de facturas al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    renderFacturaTable();
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



// facturas.js

// Datos iniciales de facturas (puedes sustituir esto por una fuente de datos real)
let facturas = [
    // Ejemplo de una factura
    {
        id: 'F001',
        fechaPago: '2024-07-22 14:00',
        idCliente: 'C001',
        nombreCliente: 'Juan Perez',
        fechaVencimiento: '2024-07-22',
        nombreVendedor: 'Pedro Gomez',
        formaPago: 'Efectivo',
        productos: [
            { unidades: 2, nombre: 'Producto 1', valorIVA: 1000, total: 12000 },
            { unidades: 1, nombre: 'Producto 2', valorIVA: 500, total: 5500 }
        ],
        subtotal: 15000,
        valorIVA: 1500,
        descuento: 0,
        total: 16500,
        totalLetras: 'Dieciséis mil quinientos pesos'
    }
];
// variables para el modo edición
let editMode = false;
let editFacturaRef = null;

// Referencias a elementos del DOM
const facturaForm = document.getElementById('facturaForm');
const facturaTable = document.getElementById('facturaTable');
const searchInput = document.getElementById('search');

// Función para abrir el modal de creación de factura
function openFacturaModal() {
    facturaForm.reset(); // Limpiar el formulario
    $('#facturaModal').modal('show'); // Mostrar el modal
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
        productos: [], // Aquí irán los productos
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
        facturas[editFacturaRef] = newFactura;
    } else {
        facturas.push(newFactura);
    }

    $('#facturaModal').modal('hide'); // Ocultar el modal
    renderFacturaTable(); // Renderizar la tabla de facturas
});

// Función para ver una factura
function viewFactura(id) {
    const factura = facturas.find(f => f.id === id);
    if (factura) {
        // Aquí puedes añadir el código para mostrar los detalles de la factura
        console.log('Ver factura:', factura);
    }
}

// Función para editar una factura
function editFactura(id) {
    const index = facturas.findIndex(f => f.id === id);
    if (index !== -1) {
        editMode = true;
        editFacturaRef = index;
        const factura = facturas[index];
    editMode = true;
    editFacturaRef = index;
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
    }
    // Renderizar productos en el formulario
    const productosContainer = document.getElementById('productosContainer');
    productosContainer.innerHTML = '';
    factura.productos.forEach(producto => {
        const productoRow = `
            <div class="form-group row producto-row">
                <div class="col-md-2">
                    <input type="number" class="form-control producto-unidades" value="${producto.unidades}" required>
                </div>
                <div class="col-md-4">
                    <input type="text" class="form-control producto-nombre" value="${producto.nombre}" required>
                </div>
                <div class="col-md-3">
                    <input type="number" class="form-control producto-valorIVA" value="${producto.valorIVA}" required>
                </div>
                <div class="col-md-3">
                    <input type="number" class="form-control producto-total" value="${producto.total}" required>
                </div>
            </div>
        `;
        productosContainer.insertAdjacentHTML('beforeend', productoRow);
    });

    $('#facturaModal').modal('show'); // Mostrar el modal
}

// Función para eliminar una factura con confirmación
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

// Inicialización de la tabla de facturas
function renderFacturaTable(filteredFacturas = facturas) {
    facturaTable.innerHTML = '';
    filteredFacturas.forEach((factura, index) => {
        const row = `
            <tr>
                <td>${factura.id}</td>
                <td>${factura.nombreCliente}</td>
                <td>${factura.fechaPago}</td>
                <td>${factura.total}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="viewFactura(${index})">Ver</button>
                    <button class="btn btn-warning btn-sm" onclick="editFactura(${index})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteFactura(${index})">Eliminar</button>
                </td>
            </tr>
        `;
        facturaTable.insertAdjacentHTML('beforeend', row);
    });
}

// Renderizar la tabla de facturas al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    renderFacturaTable(facturas);
});



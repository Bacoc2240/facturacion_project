// ===============================
// VARIABLES Y CONFIGURACIÓN INICIAL
// ===============================

// Array para almacenar las facturas cargadas
let DOM = {};
let facturas = [];

// Referencias a elementos del DOM 
function initializeDOMReferences() {
    DOM = {
        facturaForm: document.getElementById('facturaForm'),
        facturaTable: document.getElementById('facturaTable'),
        searchInput: document.getElementById('search'), // Nota: el ID era 'buscar' pero en el HTML es 'search'
        barcodeInput: document.getElementById('barcodeInput')
    };
}

function actualizarIdCliente() {
    const idClienteInput = document.getElementById('idClienteInput');
    const idClienteHidden = document.getElementById('idCliente');
    
    if (idClienteInput && idClienteHidden) {
        idClienteHidden.value = idClienteInput.value;
    }
}

// ===============================
// GESTIÓN DE FACTURAS
// ===============================

/**
 * Carga y muestra las facturas desde el backend 
 */
async function cargarFacturas() {
    try {
        const response = await fetch('/facturas/api/lista');
        if (!response.ok) {
            throw new Error(`¡Error HTTP! Estado: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        facturas = data;
        renderFacturaTable(facturas);
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar facturas: ' + error.message, 'error');
    }
}

/**
 * Renderiza la tabla de facturas con botones para notas crédito y débito
 * @param {Array} facturasList - Lista de facturas a mostrar
 */
function renderFacturaTable(facturasList = facturas) {
    if (!DOM.facturaTable) return;

    DOM.facturaTable.innerHTML = '';
    facturasList.forEach((factura) => {
        // Extraer nombre del cliente de forma segura
        let nombreCliente = 'Cliente no especificado';
        if (factura.cliente && factura.cliente.nombre) {
            nombreCliente = factura.cliente.nombre;
        }
        
        const row = `
            <tr data-factura-id="${factura.id}">
                <td>${factura.numero_factura || ''}</td>
                <td>${nombreCliente}</td>
                <td>${formatearFecha(factura.fecha)}</td>
                <td>${formatearMoneda(factura.total)}</td>
                <td>
                    <button class="btn btn-info btn-sm" onclick="viewFactura(${factura.id})">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                </td>
                <td>
                    <button class="btn btn-outline-danger btn-sm" onclick="iniciarNotaCredito(${factura.id})">
                        <i class="fas fa-file-alt"></i> Nota Crédito
                    </button>
                    <div class="mt-1 resumen-nc" id="resumen-nc-${factura.id}">
                        <!-- El resumen de notas crédito se cargará dinámicamente -->
                    </div>
                </td>
                <td>
                    <button class="btn btn-outline-warning btn-sm" onclick="iniciarNotaDebito(${factura.id})">
                        <i class="fas fa-file-invoice"></i> Nota Débito
                    </button>
                    <div class="mt-1 resumen-nd" id="resumen-nd-${factura.id}">
                        <!-- El resumen de notas débito se cargará dinámicamente -->
                    </div>
                </td>
            </tr>
        `;
        DOM.facturaTable.insertAdjacentHTML('beforeend', row);
    });
    
    // Inicializar los resúmenes de notas
    inicializarResumenesNotas();
}

/**
 * Inicia la carga de resúmenes de notas para todas las facturas
 */
function inicializarResumenesNotas() {
    // Verificar que notas_asociadas.js se haya cargado
    if (typeof window.cargarResumenesNotas === 'function') {
        window.cargarResumenesNotas();
    } else {
        console.warn('El módulo notas_asociadas.js no está cargado correctamente');
        
        // Intentar cargar notas_asociadas.js si no está disponible
        const script = document.createElement('script');
        script.src = '/static/js/notas_asociadas.js';
        script.onload = function() {
            if (typeof window.cargarResumenesNotas === 'function') {
                window.cargarResumenesNotas();
            }
        };
        document.head.appendChild(script);
    }
}

/**
 * Inicia el proceso de creación de una nota crédito
 * @param {number} facturaId - ID de la factura
 */
function iniciarNotaCredito(facturaId) {
    console.log("Iniciando proceso de nota crédito para factura:", facturaId);
    
    // Si el módulo nota_credito.js está cargado, usar su función
    if (typeof window.cargarYMostrarModalNC === 'function') {
        window.cargarYMostrarModalNC(facturaId);
    } else {
        // Si no está cargado, mostrar loader y cargar el script
        Swal.fire({
            title: 'Cargando módulo de nota crédito',
            text: 'Por favor espere...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const script = document.createElement('script');
        script.src = '/static/js/nota_credito.js';
        script.onload = function() {
            Swal.close();
            if (typeof window.cargarYMostrarModalNC === 'function') {
                window.cargarYMostrarModalNC(facturaId);
            } else {
                Swal.fire('Error', 'No se pudo cargar el módulo de notas crédito', 'error');
            }
        };
        script.onerror = function() {
            Swal.fire('Error', 'No se pudo cargar el módulo de notas crédito', 'error');
        };
        document.head.appendChild(script);
    }
}

/**
 * Inicia el proceso de creación de una nota débito
 * @param {number} facturaId - ID de la factura
 */
function iniciarNotaDebito(facturaId) {
    console.log("Iniciando proceso de nota débito para factura:", facturaId);
    
    // Si el módulo nota_debito.js está cargado, usar su función
    if (typeof window.cargarYMostrarModalND === 'function') {
        window.cargarYMostrarModalND(facturaId);
    } else {
        // Por ahora, mostrar mensaje de funcionalidad en desarrollo
        Swal.fire({
            title: 'Funcionalidad en desarrollo',
            text: `Se aplicará una nota débito a la factura #${facturaId}`,
            icon: 'info',
            confirmButtonText: 'Entendido'
        });
        
        // Código para cargar el módulo de nota débito cuando esté disponible
        /*
        const script = document.createElement('script');
        script.src = '/static/js/nota_debito.js';
        script.onload = function() {
            if (typeof window.cargarYMostrarModalND === 'function') {
                window.cargarYMostrarModalND(facturaId);
            }
        };
        document.head.appendChild(script);
        */
    }
}

/**
 * Muestra los detalles de una factura
 * @param {number} facturaId - ID de la factura a visualizar
 */
function viewFactura(facturaId) {
    try {
        // Validar que el ID de factura sea un número válido
        if (!facturaId || isNaN(parseInt(facturaId))) {
            console.error('ID de factura inválido:', facturaId);
            mostrarNotificacion('ID de factura inválido', 'error');
            return;
        }
        
        // Mostrar un indicador de carga
        mostrarNotificacion('Cargando factura...', 'info', 1000);
        
        // Redirigir a la vista de la factura
        window.location.href = `/facturas/ver/${parseInt(facturaId)}`;
    } catch (error) {
        console.error('Error al redirigir a la factura:', error);
        mostrarNotificacion('Error al cargar la factura', 'error');
    }
}

function mostrarDetallesFactura(factura) {
    // Crear la tabla de productos
    let productosHtml = `
        <table class="table table-striped table-sm">
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    // Verificar si hay productos para mostrar
    if (factura.productos && factura.productos.length > 0) {
        factura.productos.forEach(item => {
            productosHtml += `
                <tr>
                    <td>${item.producto.nombre}</td>
                    <td>${item.cantidad}</td>
                    <td>${formatearMoneda(item.precio_unitario)}</td>
                    <td>${formatearMoneda(item.subtotal)}</td>
                </tr>
            `;
        });
    } else {
        productosHtml += `
            <tr>
                <td colspan="4" class="text-center">No hay productos en esta factura</td>
            </tr>
        `;
    }
    
    productosHtml += `
            </tbody>
        </table>
    `;
    
    // Crear HTML para el modal
    const html = `
        <div class="factura-detalle">
            <div class="row">
                <div class="col-md-6">
                    <h5>Información General</h5>
                    <p><strong>Número:</strong> ${factura.numero_factura}</p>
                    <p><strong>Fecha:</strong> ${formatearFecha(factura.fecha)}</p>
                    <p><strong>Cliente:</strong> ${factura.cliente.nombre}</p>
                    <p><strong>Estado:</strong> ${factura.estado}</p>
                </div>
                <div class="col-md-6">
                    <h5>Totales</h5>
                    <p><strong>Subtotal:</strong> ${formatearMoneda(factura.subtotal)}</p>
                    <p><strong>IVA (${factura.iva}%):</strong> ${formatearMoneda(factura.subtotal * factura.iva / 100)}</p>
                    <p><strong>Total:</strong> ${formatearMoneda(factura.total)}</p>
                </div>
            </div>
            
            <h5 class="mt-3">Productos</h5>
            ${productosHtml}
        </div>
    `;
    
    // Mostrar el modal con la información
    Swal.fire({
        title: `Factura #${factura.numero_factura}`,
        html: html,
        width: '800px',
        confirmButtonText: 'Cerrar'
    });
}


// ===============================
// GESTIÓN DEL CARRITO DE FACTURA
// ===============================

class CarritoFactura {
    constructor() {
        this.productos = new Map();
        this.total = 0;
        this.subtotal = 0;
        this.iva = 0;
    }

    /**
     * Agrega un producto al carrito o incrementa su cantidad si ya existe
     */
    /**
     /**
     * Función mejorada para agregar productos al carrito
     * @param {Object} producto - El producto a agregar
     * @param {number} cantidad - La cantidad del producto
     * @param {number} tipoIVA - El porcentaje de IVA (puede ser 0, 5 o 19)
     */
    agregarProducto(producto, cantidad = 1, tipoIVA = null) {
        try {
            console.log("Agregando producto al carrito:", producto);
            console.log("Cantidad:", cantidad);
            console.log("Tipo IVA especificado:", tipoIVA);
            
            // Verificar si el producto tiene ID
            if (!producto || !producto.id) {
                console.error("ERROR: El producto no tiene ID", producto);
                mostrarNotificacion('Error: El producto no tiene ID válido', 'error');
                return;
            }
            
            // Convertir cantidad a número
            cantidad = parseFloat(cantidad) || 1;
            
            // Clonar el producto para evitar referencias
            const productoParaCarrito = { ...producto };
            
            // Establecer la cantidad
            productoParaCarrito.cantidad = cantidad;
            
            // Determinar el IVA basado en el parámetro o establecer uno predeterminado
            // Si se proporciona un IVA específico, usarlo (permitir selección manual)
            if (tipoIVA !== null && !isNaN(tipoIVA)) {
                productoParaCarrito.porcentajeIVA = parseFloat(tipoIVA);
            } 
            // Si no se especifica, usar el predeterminado del producto o 19%
            else if (producto.porcentajeIVA !== undefined) {
                productoParaCarrito.porcentajeIVA = parseFloat(producto.porcentajeIVA);
            } 
            else {
                // Valor predeterminado si no podemos determinar
                productoParaCarrito.porcentajeIVA = 19;
            }
            
            console.log("IVA asignado:", productoParaCarrito.porcentajeIVA);
            
            // Agregar al carrito
            this.productos.set(producto.id, productoParaCarrito);
            
            // Debug del estado del carrito
            console.log("Estado actual del carrito:", this.productos);
            console.log("Número de productos:", this.productos.size);
            
            // Calcular totales y renderizar
            this.calcularTotales();
            this.renderizarProductos();
        } catch (error) {
            console.error("Error al agregar producto al carrito:", error);
            mostrarNotificacion('Error al agregar producto al carrito', 'error');
        }
    }

    /**
     * Elimina un producto del carrito
     */
    eliminarProducto(id) {
        this.productos.delete(id);
        this.calcularTotales();
        this.actualizarVistaProductos();
    }

    /**
     * Función mejorada para calcular los totales del carrito
     * Asegura que se use el porcentajeIVA de cada producto
     */
    calcularTotales() {
        this.subtotal = 0;
        this.iva = 0;
        
        console.log("Calculando totales. Productos:", this.productos);
        
        if (this.productos instanceof Map && this.productos.size > 0) {
            this.productos.forEach((producto, id) => {
                console.log("Procesando producto para totales:", id, producto);
                const precio = parseFloat(producto.precio) || 0;
                const cantidad = parseFloat(producto.cantidad) || 1;
                const porcentajeIVA = parseFloat(producto.porcentajeIVA) || 0;
                
                // Calcular subtotal por producto
                const subtotalProducto = precio * cantidad;
                this.subtotal += subtotalProducto;
                
                // Calcular IVA por producto según su porcentaje específico
                const ivaProducto = (subtotalProducto * porcentajeIVA) / 100;
                this.iva += ivaProducto;
                
                console.log(`Producto ${id}: Subtotal=${subtotalProducto}, IVA(${porcentajeIVA}%)=${ivaProducto}`);
            });
        } else {
            console.warn("No hay productos en el carrito o el formato es incorrecto");
        }
        
        // Calcular total (subtotal + IVA)
        this.total = this.subtotal + this.iva;
        
        // Actualizar campos en el DOM
        const subtotalElement = document.getElementById('subtotal');
        const ivaElement = document.getElementById('valorIVA');
        const totalElement = document.getElementById('total');
        
        if (subtotalElement) subtotalElement.value = this.subtotal.toFixed(2);
        if (ivaElement) ivaElement.value = this.iva.toFixed(2);
        if (totalElement) totalElement.value = this.total.toFixed(2);
        
        console.log("Totales calculados:", {
            subtotal: this.subtotal.toFixed(2),
            iva: this.iva.toFixed(2),
            total: this.total.toFixed(2)
        });
    }


    /**
     * Actualiza la vista de productos en el DOM
     */
    actualizarVistaProductos() {
        const container = document.getElementById('productosContainer');
        container.innerHTML = '';
        
        this.productos.forEach((producto, id) => {
            const productoHTML = `
                <div class="form-row producto-row" data-id="${id}">
                    <div class="form-group col-md-2">
                        <input type="number" class="form-control producto-cantidad" 
                               value="${producto.cantidad}" min="1" 
                               onchange="carritoFactura.actualizarCantidad('${id}', this.value)">
                    </div>
                    <div class="form-group col-md-4">
                        <input type="text" class="form-control" value="${producto.nombre}" readonly>
                    </div>
                    <div class="form-group col-md-2">
                        <input type="number" class="form-control" value="${producto.precio}" readonly>
                    </div>
                    <div class="form-group col-md-2">
                        <input type="number" class="form-control" value="${producto.porcentajeIVA}" readonly>
                    </div>
                    <div class="form-group col-md-2">
                        <button type="button" class="btn btn-danger btn-sm" 
                                onclick="carritoFactura.eliminarProducto('${id}')">
                            Eliminar
                        </button>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', productoHTML);
        });

        // Actualizar totales en el formulario
        document.getElementById('subtotal').value = this.subtotal.toFixed(2);
        document.getElementById('valorIVA').value = this.iva.toFixed(2);
        document.getElementById('total').value = this.total.toFixed(2);
    }

    /**
     * Función mejorada para actualizar el IVA de un producto en el carrito
     * @param {string|number} id - ID del producto
     * @param {string|number} nuevoIVA - Nuevo porcentaje de IVA (0, 5 o 19)
     */
    actualizarIVA(id, nuevoIVA) {
        try {
            // Convertir ID a número
            id = parseInt(id);
            // Convertir IVA a número decimal
            nuevoIVA = parseFloat(nuevoIVA);
            
            console.log(`Actualizando IVA del producto ${id} a ${nuevoIVA}%`);
            
            if (this.productos.has(id)) {
                const producto = this.productos.get(id);
                // Actualizar el porcentaje de IVA
                producto.porcentajeIVA = nuevoIVA;
                // Recalcular totales
                this.calcularTotales();
                // Actualizar la vista
                this.renderizarProductos();
                
                console.log(`IVA actualizado correctamente para producto ${id}`);
                console.log("Producto actualizado:", producto);
            } else {
                console.error(`No se encontró el producto con ID ${id} en el carrito`);
            }
        } catch (error) {
            console.error(`Error al actualizar IVA del producto ${id}:`, error);
        }
    }

    /**
     * Actualiza la cantidad de un producto específico
     */
    actualizarCantidad(id, nuevaCantidad) {
        id = parseInt(id);
        nuevaCantidad = parseFloat(nuevaCantidad) || 1;
        
        if (this.productos.has(id)) {
            const producto = this.productos.get(id);
            producto.cantidad = nuevaCantidad;
            this.calcularTotales();
            this.renderizarProductos();
        }
    }

    /**
     * Limpia todos los productos del carrito
     */
    limpiarCarrito() {
        this.productos.clear();
        this.calcularTotales();
        this.actualizarVistaProductos();
    }

    /**
     * Renderiza los productos en la tabla
     */
    renderizarProductos() {
        // Get reference to the container
        const contenedor = document.getElementById('productosContainer');
        
        // Clear existing content
        if (contenedor) {
            contenedor.innerHTML = '';
        } else {
            console.error("No se encontró el contenedor de productos");
            return;
        }
        
        // Check if there are products
        if (this.productos.size === 0) {
            // Show empty message
            const filaSinProductos = document.createElement('tr');
            filaSinProductos.innerHTML = `
                <td colspan="7" class="text-center py-3">
                    <em>No hay productos agregados</em>
                </td>
            `;
            contenedor.appendChild(filaSinProductos);
            return;
        }
        
        // Add debug logging
        console.log("Renderizando " + this.productos.size + " productos");
        console.log("Productos:", Array.from(this.productos.entries()));
        
        // Render each product
        for (const [id, producto] of this.productos) {
            // Debug log for each product
            console.log("Renderizando producto:", id, producto);
            
            // Calculate product subtotal
            const subtotalProducto = parseFloat(producto.precio || 0) * parseFloat(producto.cantidad || 0);
            
            // Create a new row
            const fila = document.createElement('tr');
            
            // Set the HTML for the row - IMPORTANTE: mantenemos la estructura de columnas
            fila.innerHTML = `
                <td>${producto.codigo_barras || '-'}</td>
                <td>${producto.nombre || 'Producto'}</td>
                <td>
                    <input type="number" 
                        class="form-control form-control-sm" 
                        value="${producto.cantidad || 1}" 
                        min="0.1" 
                        step="0.1"
                        onchange="carritoFactura.actualizarCantidad(${id}, this.value)">
                </td>
                <td>${parseFloat(producto.precio || 0).toFixed(2)}</td>
                <td>
                    <select class="form-control form-control-sm" 
                        onchange="carritoFactura.actualizarIVA(${id}, this.value)">
                        <option value="0" ${(producto.porcentajeIVA == 0) ? 'selected' : ''}>0%</option>
                        <option value="5" ${(producto.porcentajeIVA == 5) ? 'selected' : ''}>5%</option>
                        <option value="19" ${(producto.porcentajeIVA == 19 || producto.porcentajeIVA === undefined) ? 'selected' : ''}>19%</option>
                    </select>
                </td>
                <td>${subtotalProducto.toFixed(2)}</td>
                <td>
                    <button type="button" 
                        class="btn btn-sm btn-danger" 
                        onclick="carritoFactura.eliminarProducto(${id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            // Append the row to the container
            contenedor.appendChild(fila);
        }
        
        // Debug check after rendering
        console.log("Rendering complete, container has " + contenedor.children.length + " rows");
    }
}

// Instancia global del carrito
const carritoFactura = new CarritoFactura();



// ===============================
// MANEJO DE EVENTOS Y FUNCIONES DE UI
// ===============================

/**
 * Maneja el escaneo de código de barras y agrega el producto automáticamente.
 * Incluye prevención de duplicados y actualización sincronizada de campos.
 */
let isProcessing = false; // Bandera para evitar ejecuciones duplicadas

async function handleBarcodeScan(event) {
    // Prevenir el comportamiento por defecto
    event.preventDefault();
    
    // Solo procesar el evento keydown cuando sea Enter o el evento blur
    if ((event.type === 'keydown' && event.keyCode === 13) || event.type === 'blur') {
        // Si ya se está procesando, salir para evitar duplicados
        if (isProcessing) return;
        
        // Marcar como en proceso
        isProcessing = true;
        
        const barcode = event.target.value.trim();
        if (!barcode) {
            isProcessing = false; // Restablecer la bandera
            return;
        }
        
        try {
            // Deshabilitar el input mientras se procesa
            event.target.disabled = true;
            
            const response = await fetch(`/facturas/api/productos/barcode/${barcode}`);
            const data = await response.json();
            
            if (response.ok && data.success && data.producto) {
                // Actualizar el campo de búsqueda por nombre sin disparar eventos innecesarios
                const productSearchInput = document.getElementById('productSearch');
                if (productSearchInput) {
                    productSearchInput.value = data.producto.nombre;
                    // Limpiar cualquier sugerencia visible
                    const suggestionContainer = document.getElementById('productSuggestions');
                    if (suggestionContainer) {
                        suggestionContainer.style.display = 'none';
                    }
                }
                
                // Agregar el producto al carrito
                carritoFactura.agregarProducto(data.producto);
                mostrarNotificacion(`Producto agregado: ${data.producto.nombre}`, 'success');
                event.target.value = '';
            } else {
                throw new Error(data.error || 'Producto no encontrado');
            }
        } catch (error) {
            console.error('Error al procesar código de barras:', error);
            mostrarNotificacion(`Error: ${error.message}`, 'error');
            event.target.value = '';
            
            // Limpiar también el campo de búsqueda por nombre en caso de error
            const productSearchInput = document.getElementById('productSearch');
            if (productSearchInput) {
                productSearchInput.value = '';
            }
        } finally {
            // Rehabilitar el input y devolverle el foco
            event.target.disabled = false;
            event.target.focus();
            isProcessing = false; // Restablecer la bandera
        }
    }
}

/**
 * Abre el modal de factura y reinicia sus campos
 */
function openFacturaModal() {
    if (!DOM.facturaForm) {
        console.error('No se pudo encontrar el formulario de factura');
        return;
    }
    
    DOM.facturaForm.reset();
    carritoFactura.limpiarCarrito();
    
    if (DOM.barcodeInput) {
        DOM.barcodeInput.focus();
    }
    
    $('#facturaModal').modal('show');
}

// ===============================
// OPERACIONES CON EL BACKEND
// ===============================

/**
 * Busca un producto por su código de barras
 */
async function buscarProductoPorCodigo(codigo) {
    try {
        const response = await fetch(`/facturas/api/productos/barcode/${codigo}`);
        if (!response.ok) throw new Error('Producto no encontrado');
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Error al obtener el producto');
        }
        
        carritoFactura.agregarProducto(data.producto);
        mostrarNotificacion('Producto agregado', 'success');
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al buscar producto: ' + error.message, 'error');
    }
}

/**
 * Maneja la búsqueda en tiempo real de productos por nombre
 * @param {HTMLInputElement} inputElement - El campo de búsqueda
 */
let searchTimeout = null;

/**
 * Maneja la búsqueda en tiempo real de productos por nombre
 * @param {HTMLInputElement|string} input - El campo de búsqueda o el valor de búsqueda
 */
async function buscarProductos(input) {
    try {
        // Determinar el valor de búsqueda dependiendo del tipo de entrada
        let inputElement;
        let query = '';

        if (typeof input === 'string') {
            // Si es una cadena, buscar el elemento y usar la cadena como valor
            inputElement = document.getElementById('productSearch');
            query = input.trim();
        } else if (input instanceof HTMLInputElement) {
            // Si es un elemento, usarlo directamente
            inputElement = input;
            query = inputElement.value.trim();
        } else if (!input) {
            // Si no hay entrada, intentar obtener el elemento por ID
            inputElement = document.getElementById('productSearch');
            if (inputElement) {
                query = inputElement.value.trim();
            }
        }
        
        // Obtener el contenedor de sugerencias
        const suggestionContainer = document.getElementById('productSuggestions');
        if (!suggestionContainer) {
            console.error('No se pudo encontrar el contenedor de sugerencias');
            return;
        }
        
        // Limpiar timeout anterior
        if (searchTimeout) clearTimeout(searchTimeout);
        
        // Si no hay consulta, limpiar sugerencias
        if (!query) {
            suggestionContainer.innerHTML = '';
            suggestionContainer.style.display = 'none';
            return;
        }
        
        // Esperar 300ms después de que el usuario deje de escribir
        searchTimeout = setTimeout(async () => {
            try {
                // Mostrar indicador de carga
                suggestionContainer.innerHTML = '<div class="searching">Buscando...</div>';
                suggestionContainer.style.display = 'block';
                
                // Realizar la búsqueda
                const response = await fetch(`/facturas/api/productos/buscar/${encodeURIComponent(query)}`);
                
                // Verificar si la respuesta es exitosa
                if (!response.ok) {
                    throw new Error('Error al buscar productos');
                }
                
                const data = await response.json();
                
                // Mostrar resultados
                if (data.success && data.productos && data.productos.length > 0) {
                    suggestionContainer.innerHTML = data.productos
                        .map(producto => {
                            // Escapar JSON para evitar problemas con comillas
                            const productoJSON = JSON.stringify(producto)
                                .replace(/"/g, '&quot;')
                                .replace(/'/g, "\\'");
                            
                            return `
                                <div class="sugerencia-producto" onclick="seleccionarProducto(${productoJSON})">
                                    <strong>${producto.nombre}</strong>
                                    <br>
                                    <small>Código: ${producto.codigo_barras || 'N/A'} - Stock: ${producto.stock || 0}</small>
                                </div>
                            `;
                        })
                        .join('');
                    suggestionContainer.style.display = 'block';
                } else {
                    suggestionContainer.innerHTML = '<div class="no-resultados">No se encontraron productos</div>';
                    suggestionContainer.style.display = 'block';
                }
            } catch (error) {
                console.error('Error en búsqueda de productos:', error);
                suggestionContainer.innerHTML = '<div class="error-busqueda">Error al buscar productos</div>';
                suggestionContainer.style.display = 'block';
            }
        }, 300);
    } catch (error) {
        console.error('Error general en búsqueda de productos:', error);
    }
}

/**
 * Selecciona un producto y lo agrega al carrito
 * @param {Object} producto - Datos del producto
 */
function seleccionarProducto(producto) {
    console.log('Producto seleccionado:', producto);
    
    try {
        // Validar que el producto sea un objeto válido con ID
        if (!producto || !producto.id) {
            console.error('Producto inválido:', producto);
            mostrarNotificacion('Producto inválido', 'error');
            return;
        }

        // Determinar la unidad basada en la categoría del producto
        const unidad = producto.categoria === 'Accesorios' ? 'UND' : 'ml';
        
        // Añadir la unidad al producto
        producto.unidad = unidad;
        
        // Verificar que carritoFactura existe y es una instancia válida
        if (!carritoFactura || typeof carritoFactura.agregarProducto !== 'function') {
            console.error('Error: carritoFactura no está inicializado correctamente');
            mostrarNotificacion('Error en el sistema de facturación', 'error');
            return;
        }
        
        // Agregar el producto al carrito
        carritoFactura.agregarProducto(producto);
        
        // Cerrar el contenedor de sugerencias de productos
        const productSuggestions = document.getElementById('productSuggestions');
        if (productSuggestions) {
            productSuggestions.style.display = 'none';
        }
        
        // Limpiar el campo de búsqueda
        const searchInput = document.getElementById('productSearch');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Mostrar notificación de éxito
        mostrarNotificacion(`Producto "${producto.nombre}" agregado`, 'success');
    } catch (error) {
        console.error('Error al seleccionar producto:', error);
        mostrarNotificacion('Error al agregar el producto', 'error');
    }
}

/**
 * Agrega un producto a la tabla de la factura
 * @param {Object} producto - El producto a agregar
 */
function agregarProductoATabla(producto) {
    const tablaBody = document.getElementById('productosContainer');
    if (!tablaBody) {
        console.error('No se encontró el contenedor de productos');
        return;
    }
    
    // Verificar si el producto ya existe en la tabla
    const productoExistente = document.querySelector(`tr[data-producto-id="${producto.id}"]`);
    if (productoExistente) {
        // Si existe, incrementar la cantidad
        const inputCantidad = productoExistente.querySelector('.cantidad-producto');
        if (inputCantidad) {
            const cantidadActual = parseInt(inputCantidad.value) || 0;
            inputCantidad.value = cantidadActual + 1;
            // Actualizar subtotal
            actualizarSubtotalProducto(productoExistente);
        }
    } else {
        // Si no existe, crear una nueva fila
        const fila = document.createElement('tr');
        fila.setAttribute('data-producto-id', producto.id);
        
        const subtotal = producto.precio;
        
        fila.innerHTML = `
            <td>${producto.codigo_barras || 'N/A'}</td>
            <td>${producto.nombre}</td>
            <td>
                <input type="number" 
                       class="form-control form-control-sm cantidad-producto" 
                       value="1" 
                       min="1" 
                       onchange="actualizarSubtotalProducto(this.parentNode.parentNode)">
            </td>
            <td>$${producto.precio.toLocaleString()}</td>
            <td>${producto.porcentajeIVA || 0}%</td>
            <td class="subtotal-producto">$${subtotal.toLocaleString()}</td>
            <td>
                <button type="button" class="btn btn-sm btn-danger" onclick="eliminarProducto(this.parentNode.parentNode)">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tablaBody.appendChild(fila);
    }
    
    // Actualizar totales de la factura
    actualizarTotalesFactura();
}

/**
 * Actualiza el subtotal de un producto basado en su cantidad
 * @param {HTMLElement} fila - La fila de la tabla que contiene el producto
 */
function actualizarSubtotalProducto(fila) {
    const cantidadInput = fila.querySelector('.cantidad-producto');
    const subtotalCell = fila.querySelector('.subtotal-producto');
    
    if (!cantidadInput || !subtotalCell) return;
    
    const cantidad = parseInt(cantidadInput.value) || 0;
    const precio = parseFloat(fila.cells[3].textContent.replace('$', '').replace(',', '')) || 0;
    
    const subtotal = cantidad * precio;
    subtotalCell.textContent = `$${subtotal.toLocaleString()}`;
    
    // Actualizar totales de la factura
    actualizarTotalesFactura();
}

/**
 * Elimina un producto de la tabla
 * @param {HTMLElement} fila - La fila de la tabla que contiene el producto
 */
function eliminarProducto(fila) {
    if (fila && fila.parentNode) {
        fila.parentNode.removeChild(fila);
        actualizarTotalesFactura();
    }
}

/**
 * Actualiza el IVA de un producto específico en el carrito
 * @param {string|number} id - ID del producto
 * @param {string|number} nuevoIVA - Nuevo valor de IVA a aplicar
 */
function actualizarIVA(id, nuevoIVA) {
    if (carritoFactura.productos.has(Number(id))) {
        const producto = carritoFactura.productos.get(Number(id));
        producto.porcentajeIVA = parseFloat(nuevoIVA);
        
        // Recalcular totales después de actualizar el IVA
        carritoFactura.calcularTotales();
        // Renderizar los productos nuevamente
        carritoFactura.renderizarProductos();
        
        console.log(`IVA del producto ${id} actualizado a ${nuevoIVA}%`);
    } else {
        console.error(`No se encontró el producto con ID ${id} en el carrito`);
    }
}


/**
 * Actualiza los totales de la factura
 */
function actualizarTotalesFactura() {
    let subtotal = 0;
    let iva = 0;
    
    // Recorrer todas las filas de productos
    const filas = document.querySelectorAll('#productosContainer tr');
    filas.forEach(fila => {
        // Obtener valores de la fila
        let cantidad, precio, porcentajeIVA;
        
        // Intentar obtener cantidad de un input si existe
        const cantidadInput = fila.querySelector('.cantidad-producto');
        if (cantidadInput) {
            cantidad = parseFloat(cantidadInput.value) || 0;
        } else {
            // Intentar obtener de la celda
            const cantidadCell = fila.cells[3]; // Ajustar el índice según tu tabla
            if (cantidadCell) {
                cantidad = parseFloat(cantidadCell.textContent) || 0;
            } else {
                cantidad = 0;
            }
        }
        
        // Intentar obtener precio
        const precioCell = fila.cells[4]; // Ajustar el índice según tu tabla
        if (precioCell) {
            precio = parseFloat(precioCell.textContent.replace(/[^\d.-]/g, '')) || 0;
        } else {
            precio = 0;
        }
        
        // Intentar obtener IVA
        const ivaCell = fila.cells[5]; // Ajustar el índice según tu tabla
        if (ivaCell) {
            porcentajeIVA = parseFloat(ivaCell.textContent.replace(/[^\d.-]/g, '')) || 0;
        } else {
            porcentajeIVA = 0;
        }
        
        // Calcular valores
        const subtotalProducto = cantidad * precio;
        const ivaProducto = subtotalProducto * (porcentajeIVA / 100);
        
        // Acumular totales
        subtotal += subtotalProducto;
        iva += ivaProducto;
    });
    
    // Calcular total
    const total = subtotal + iva;
    
    // Actualizar los campos en el formulario
    const subtotalElement = document.getElementById('subtotal');
    const ivaElement = document.getElementById('valorIVA');
    const totalElement = document.getElementById('total');
    
    if (subtotalElement) subtotalElement.value = subtotal.toFixed(2);
    if (ivaElement) ivaElement.value = iva.toFixed(2);
    if (totalElement) totalElement.value = total.toFixed(2);
    
    // Logging para depuración
    console.log("Totales calculados:", {
        subtotal: subtotal.toFixed(2),
        iva: iva.toFixed(2),
        total: total.toFixed(2)
    });
}

/**
 * Maneja la búsqueda en tiempo real de clientes
 */
let timeoutId = null;
let seleccionEnProceso = false;

async function buscarClientes(inputElement, event) {
    const query = inputElement.value.trim();
    const sugerenciasContainer = document.getElementById('clienteSugerencias');
    
    if (timeoutId) clearTimeout(timeoutId);
    
    if (!query) {
        sugerenciasContainer.innerHTML = '';
        sugerenciasContainer.style.display = 'none';
        return;
    }
    
    // Función auxiliar para verificar si es una búsqueda completa
    const esConsultaCompleta = (event) => {
        return event && (
            event.key === 'Enter' || 
            event.type === 'blur' ||
            event.type === 'change'
        );
    };
    
    // Para eventos específicos (Enter, blur, change)
    if (event && esConsultaCompleta(event) && !seleccionEnProceso) {
        try {
            // Usar SIEMPRE la ruta de búsqueda
            const response = await fetch(`/facturas/api/clientes/buscar/${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`Error en la búsqueda: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.clientes && data.clientes.length > 0) {
                // Mostrar sugerencias para selección
                sugerenciasContainer.innerHTML = data.clientes
                    .map(cliente => `
                        <div class="sugerencia-cliente"
                             onclick="event.stopPropagation();
                                     seleccionEnProceso = true;
                                     seleccionarCliente('${cliente.id}', '${cliente.nombre}')">
                            <strong>${cliente.id}</strong> - ${cliente.nombre}
                        </div>
                    `).join('');
                
                sugerenciasContainer.style.display = 'block';
            } else {
                // Si no hay resultados, mostrar modal de confirmación
                sugerenciasContainer.style.display = 'none';
                
                if (!seleccionEnProceso) {
                    seleccionEnProceso = true;
                    try {
                        await confirmarRegistroCliente(query);
                    } finally {
                        setTimeout(() => {
                            seleccionEnProceso = false;
                        }, 300);
                    }
                }
            }
        } catch (error) {
            console.error('Error al buscar cliente:', error);
            sugerenciasContainer.style.display = 'none';
        }
        return;
    }

    // Para la búsqueda en tiempo real (al escribir)
    timeoutId = setTimeout(async () => {
        try {
            if (inputElement.value.trim() !== query) return;
            
            if (query.length < 2) {
                sugerenciasContainer.style.display = 'none';
                return;
            }
            
            // Usar SIEMPRE la ruta de búsqueda
            const response = await fetch(`/facturas/api/clientes/buscar/${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`Error en la búsqueda: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.clientes && data.clientes.length > 0) {
                sugerenciasContainer.innerHTML = data.clientes
                    .map(cliente => `
                        <div class="sugerencia-cliente"
                             onclick="event.stopPropagation();
                                     seleccionEnProceso = true;
                                     seleccionarCliente('${cliente.id}', '${cliente.nombre}')">
                            <strong>${cliente.id}</strong> - ${cliente.nombre}
                        </div>
                    `).join('');
                
                sugerenciasContainer.style.display = 'block';
            } else {
                sugerenciasContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error en búsqueda en tiempo real:', error);
            sugerenciasContainer.style.display = 'none';
        }
    }, 300);
}

/**
 * Función auxiliar para realizar la búsqueda de clientes
 */
async function realizarBusqueda(query, inputElement, sugerenciasContainer) {
    try {
        if (inputElement.value.trim() !== query) return;
        
        // *** MODIFICACIÓN IMPORTANTE ***
        // Siempre usamos la ruta de búsqueda para evitar errores 404
        // cuando estamos buscando por texto
        const response = await fetch(`/facturas/api/clientes/buscar/${query}`);
        const data = await response.json();
        
        if (!response.ok) {
            sugerenciasContainer.style.display = 'none';
            // Si no hay resultados y es una búsqueda completa, mostramos el modal
            if (query.length >= 2) {
                const deseaRegistrar = await confirmarRegistroCliente(query);
                if (!deseaRegistrar) {
                    await cargarMenorCuantia();
                }
            }
            return;
        }
        
        if (data?.success && Array.isArray(data.clientes)) {
            if (data.clientes.length === 0 && query.length >= 2) {
                // Si no hay resultados y es una búsqueda completa, mostramos el modal
                const deseaRegistrar = await confirmarRegistroCliente(query);
                if (!deseaRegistrar) {
                    await cargarMenorCuantia();
                }
                return;
            }

            sugerenciasContainer.innerHTML = data.clientes
                .filter(c => c.id && c.nombre)
                .map(cliente => `
                    <div class="sugerencia-cliente"
                         onclick="event.stopPropagation();
                                 seleccionEnProceso = true;
                                 seleccionarCliente('${cliente.id}', '${cliente.nombre}')">
                        <strong>${cliente.id}</strong> - ${cliente.nombre}
                    </div>
                `).join('');
            
            sugerenciasContainer.style.display = data.clientes.length ? 'block' : 'none';
        } else {
            sugerenciasContainer.style.display = 'none';
        }
    } catch (error) {
        console.error('Error en búsqueda:', error);
        sugerenciasContainer.style.display = 'none';
    }
}

/**
 * Selecciona un cliente de las sugerencias y lo establece en el formulario
 */
async function seleccionarCliente(id, nombre) {
    try {
        // Marcamos que estamos en proceso de selección
        seleccionEnProceso = true;
        
        if (!id || !nombre) {
            mostrarNotificacion('Datos de cliente inválidos', 'error');
            seleccionEnProceso = false;
            return;
        }
        
        // Establecer directamente los valores sin validaciones adicionales
        document.getElementById('idClienteInput').value = id;
        document.getElementById('idCliente').value = id;
        document.getElementById('nombreCliente').value = nombre;
        
        // Cerrar el contenedor de sugerencias
        const sugerenciasContainer = document.getElementById('clienteSugerencias');
        if (sugerenciasContainer) {
            sugerenciasContainer.innerHTML = '';
            sugerenciasContainer.style.display = 'none';
        }
        
        // Mostrar notificación de éxito
        mostrarNotificacion(`Cliente seleccionado: ${nombre}`, 'success');
        
        // Desactivar cualquier listener de eventos temporalmente para evitar validaciones adicionales
        const idClienteInput = document.getElementById('idClienteInput');
        if (idClienteInput) {
            const originalValue = idClienteInput.value;
            // Guardar el listener original
            const originalOnChange = idClienteInput.onchange;
            // Desactivar temporalmente
            idClienteInput.onchange = null;
            
            // Disparar un evento change manualmente si es necesario
            // pero sin el listener que podría causar la validación adicional
            const event = new Event('change', { bubbles: true });
            idClienteInput.dispatchEvent(event);
            
            // Restaurar el listener después de un breve retraso
            setTimeout(() => {
                idClienteInput.onchange = originalOnChange;
                seleccionEnProceso = false;
            }, 500);
        } else {
            seleccionEnProceso = false;
        }
    } catch (error) {
        console.error('Error en seleccionarCliente:', error);
        mostrarNotificacion('Error al seleccionar cliente', 'error');
        seleccionEnProceso = false;
    }
}

/**
 * Actualiza los campos ocultos del cliente a partir del input visible
 */
function actualizarIdCliente() {
    const idClienteInput = document.getElementById('idClienteInput');
    const idClienteHidden = document.getElementById('idCliente');
    
    // Si el input visible tiene valor pero el campo oculto no, copiamos el valor
    if (idClienteInput && idClienteInput.value && 
        idClienteHidden && !idClienteHidden.value) {
        idClienteHidden.value = idClienteInput.value;
    }
    
    return !!idClienteHidden.value;
}

/**
 * Limpia los campos del cliente en el formulario
 */
function limpiarCamposCliente() {
    document.getElementById('idClienteInput').value = '';
    document.getElementById('idCliente').value = '';
    document.getElementById('nombreCliente').value = '';
}

/**
 * Abre el modal de nuevo cliente 
 * @param {string} idPropuesto - ID sugerido para el nuevo cliente
 */
function abrirModalNuevoCliente(idPropuesto = '') {
    try {
        // Guardamos el estado actual de la factura para no perderlo
        const estadoFactura = {
            productos: carritoFactura.productos,
            formaPago: document.getElementById('formaPago').value
        };
        
        // Guardamos el estado en sessionStorage
        sessionStorage.setItem('estadoFacturaTemporal', JSON.stringify(estadoFactura));

        // Cerramos el modal de confirmación primero
        $('#modalConfirmacion').modal('hide');

        // Hacemos una petición para cargar el contenido del modal de clientes
        fetch('/clientes')
            .then(response => response.text())
            .then(html => {
                // Extraemos el modal del HTML de clientes
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                const modalClientes = tempDiv.querySelector('#clientModal');

                // Si el modal ya existe en el DOM, lo removemos
                const modalExistente = document.querySelector('#clientModal');
                if (modalExistente) {
                    modalExistente.remove();
                }

                // Agregamos el modal al body
                document.body.appendChild(modalClientes);

                // Establecemos el ID propuesto si existe
                if (idPropuesto) {
                    const cedulaInput = document.querySelector('#clientCedula');
                    if (cedulaInput) {
                        cedulaInput.value = idPropuesto;
                    }
                }

                // Inicializamos el modal con jQuery y lo mostramos
                $('#clientModal').modal('show');

                // Configuramos el formulario para manejar el submit
                const formulario = document.querySelector('#clientForm');
                formulario.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const datosCliente = {
                        id_cliente: document.querySelector('#clientCedula').value,
                        tipo_documento: document.querySelector('#clientTipoDoc').value,
                        nombre_cliente: document.querySelector('#clientName').value,
                        telefono: document.querySelector('#clientPhone').value,
                        correo_electronico: document.querySelector('#clientContact').value
                    };

                    try {
                        const response = await fetch('/clientes/api/clientes/crear', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(datosCliente)
                        });

                        const data = await response.json();

                        if (data.success) {
                            // Cerramos el modal
                            $('#clientModal').modal('hide');
                            
                            // Seleccionamos el cliente recién creado
                            seleccionarCliente(data.cliente.id_cliente, data.cliente.nombre_cliente);
                            
                            // Mostramos notificación de éxito
                            mostrarNotificacion('Cliente creado exitosamente', 'success');
                            
                            // Recuperamos el estado de la factura
                            const estadoGuardado = JSON.parse(sessionStorage.getItem('estadoFacturaTemporal'));
                            if (estadoGuardado) {
                                carritoFactura.productos = estadoGuardado.productos;
                                document.getElementById('formaPago').value = estadoGuardado.formaPago;
                            }
                        } else {
                            mostrarNotificacion(data.error || 'Error al crear el cliente', 'error');
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        mostrarNotificacion('Error al crear el cliente', 'error');
                    }
                });
            })
            .catch(error => {
                console.error('Error al cargar el modal de clientes:', error);
                mostrarNotificacion('Error al abrir el formulario de nuevo cliente', 'error');
            });
    } catch (error) {
        console.error('Error al abrir modal de nuevo cliente:', error);
        mostrarNotificacion('Error al abrir el formulario de nuevo cliente', 'error');
    }
}

/**
 * Función para guardar la factura
 * @param {Event} event - Evento del formulario
 */
async function guardarFactura(event) {
    event.preventDefault();
    
    // Actualizar el ID del cliente antes de la validación
    actualizarIdCliente();
    
    // Obtener y validar ID del cliente
    const idCliente = document.getElementById('idCliente').value;
    if (!idCliente) {
        mostrarNotificacion('Por favor, ingrese un ID de cliente válido', 'warning');
        return;
    }

   

    // Verificar productos y preparar datos para enviar
    let productosArray = [];
    
    console.log("Tipo de carritoFactura.productos:", typeof carritoFactura.productos);
    console.log("Es Map?", carritoFactura.productos instanceof Map);
    console.log("Tamaño:", carritoFactura.productos.size);
    
    // Obtener los productos según el tipo de datos
    if (carritoFactura.productos instanceof Map) {
        productosArray = Array.from(carritoFactura.productos.values());
    } else if (Array.isArray(carritoFactura.productos)) {
        productosArray = carritoFactura.productos;
    } else if (typeof carritoFactura.productos === 'object' && carritoFactura.productos !== null) {
        productosArray = Object.values(carritoFactura.productos);
    }
    
    // Verificar si hay productos
    if (productosArray.length === 0) {
        mostrarNotificacion('Agregue al menos un producto', 'warning');
        return;
    }

    // DEBUG: Mostrar los productos que se enviarán
    console.log("Productos a enviar:", productosArray);
    
    // Verificar que cada producto tenga un IVA válido
    for (const producto of productosArray) {
        // Si el porcentajeIVA es indefinido, establecer un valor predeterminado
        if (producto.porcentajeIVA === undefined || producto.porcentajeIVA === null) {
            console.warn(`Producto ${producto.id} sin IVA definido. Estableciendo IVA predeterminado 19%`);
            producto.porcentajeIVA = 19;
        }
    }

    // Preparar los datos de la factura para enviar al servidor
    const datosFactura = {
        id_cliente: idCliente,
        productos: productosArray.map(p => ({
            id: p.id,
            cantidad: p.cantidad,
            precio: p.precio,
            iva: p.porcentajeIVA
        })),
        subtotal: carritoFactura.subtotal,
        iva: carritoFactura.iva,
        total: carritoFactura.total,
        forma_pago: document.getElementById('formaPago').value.toUpperCase()
    };

    // Log para depuración
    console.log("Datos de factura a enviar:", JSON.stringify(datosFactura, null, 2));

    try {
        // Envío de datos al servidor
        const response = await fetch('/facturas/api/facturas/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datosFactura)
        });
    
        // Verificar respuesta...
        const contentType = response.headers.get('content-type');
        
        if (!response.ok) {
            // Manejo de error (código existente)...
        }
        
        // Verificar respuesta JSON
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Respuesta del servidor no es JSON válido');
        }
        
        const data = await response.json();
        
        mostrarNotificacion('Factura guardada exitosamente', 'success');

        // Redirección a la página de la factura
        setTimeout(() => {
            window.location.href = `/facturas/ver/${data.factura.id}?print=true`;
        }, 1500);

        // Limpiar carrito y cerrar modal
        carritoFactura.limpiarCarrito();
        $('#facturaModal').modal('hide');
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al guardar factura: ' + error.message, 'error');
    }
}

// ===============================
// FUNCIONES AUXILIARES
// ===============================

function formatearFecha(fecha) {
    if (!fecha) return '';
    return new Date(fecha).toLocaleDateString('es-CO');
}

function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
    }).format(valor || 0);
}

// Función para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'info') {
    const notificacion = document.createElement('div');
    notificacion.className = `alert alert-${tipo} alert-dismissible fade show notification`;
    notificacion.innerHTML = `
        ${mensaje}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    document.body.appendChild(notificacion);
    
    setTimeout(() => {
        notificacion.remove();
    }, 3000);
}

/**
 * Muestra el modal de confirmación para registrar un nuevo cliente
 * @param {string} identificacionCliente - Identificación del cliente no encontrado
 * @returns {Promise} Resuelve true si el usuario decide registrar el cliente
 */
function confirmarRegistroCliente(identificacionCliente) {
    console.log("Iniciando confirmarRegistroCliente con ID:", identificacionCliente);
    
    return new Promise((resolve) => {
        // Actualizar el mensaje en el modal
        const mensajeElement = document.getElementById('mensajeConfirmacion');
        if (mensajeElement) {
            mensajeElement.textContent = `No se encontró el cliente "${identificacionCliente}". ¿Desea registrarlo como nuevo cliente?`;
        }
        
        // Obtener el modal usando jQuery
        const $modal = $('#modalConfirmacion');
        
        // Variables para rastrear si ya se hizo clic en un botón
        let buttonClicked = false;
        
        // Eliminar event listeners previos para evitar duplicación
        $modal.find('.btn-secondary').off('click');
        $modal.find('.btn-primary').off('click');
        $modal.off('hidden.bs.modal');
        
        // Configurar el botón "No, usar Menor Cuantía"
        $modal.find('.btn-secondary').on('click', function() {
            console.log("Botón 'Usar Menor Cuantía' presionado");
            buttonClicked = true;
            $modal.modal('hide');
            
            // Pequeño retraso para asegurar que el modal se cierre completamente
            setTimeout(() => {
                cargarMenorCuantia().then(() => {
                    resolve(false);
                }).catch(error => {
                    console.error('Error al cargar menor cuantía:', error);
                    mostrarNotificacion('Error al cargar menor cuantía', 'error');
                    resolve(false);
                });
            }, 300);
        });
        
        // Configurar el botón "Sí, registrar nuevo cliente"
        $modal.find('.btn-primary').on('click', function() {
            console.log("Botón 'Registrar nuevo cliente' presionado");
            buttonClicked = true;
            $modal.modal('hide');
            
            // Pequeño retraso para asegurar que el modal se cierre completamente
            setTimeout(() => {
                abrirModalNuevoCliente(identificacionCliente);
                resolve(true);
            }, 300);
        });
        
        // Manejar el cierre del modal (X o clic fuera)
        $modal.on('hidden.bs.modal', function() {
            console.log("Modal oculto, buttonClicked =", buttonClicked);
            
            // Solo resolver si no se hizo clic en un botón
            // Esto evita resoluciones duplicadas
            if (!buttonClicked) {
                console.log("Modal cerrado sin hacer clic en botones, resolviendo promesa");
                resolve(false);
            }
        });
        
        // Mostrar el modal
        console.log("Mostrando modal de confirmación");
        $modal.modal('show');
    });
}

/**
 * Carga los datos para cliente de menor cuantía
 */
async function cargarMenorCuantia() {
    try {
        console.log('Intentando cargar cliente de menor cuantía...');
        const response = await fetch('/facturas/api/clientes/menor-cuantia');
        
        if (!response.ok) {
            console.error('Error en la respuesta:', response.status, response.statusText);
            throw new Error(`Error al obtener cliente de menor cuantía: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Respuesta del servidor:', data);
        
        if (data.success && data.cliente && data.cliente.id && data.cliente.nombre) {
            console.log('Actualizando campos con cliente de menor cuantía:', data.cliente);
            
            // Actualizamos los campos del formulario
            const idClienteInput = document.getElementById('idClienteInput');
            const idCliente = document.getElementById('idCliente');
            const nombreCliente = document.getElementById('nombreCliente');
            
            if (!idClienteInput || !idCliente || !nombreCliente) {
                throw new Error('No se encontraron los campos del formulario');
            }
            
            idClienteInput.value = data.cliente.id;
            idCliente.value = data.cliente.id;
            nombreCliente.value = data.cliente.nombre;
            
            // Notificamos al usuario
            mostrarNotificacion('Cliente de menor cuantía cargado: ' + data.cliente.nombre, 'success');
            
            // Si existe la función para actualizar el ID del cliente, la llamamos
            if (typeof actualizarIdCliente === 'function') {
                actualizarIdCliente();
            }
        } else {
            throw new Error('Los datos del cliente de menor cuantía no son válidos');
        }
    } catch (error) {
        console.error('Error detallado al cargar menor cuantía:', error);
        mostrarNotificacion('Error al cargar cliente de menor cuantía: ' + error.message, 'error');
        
        // Mostramos información adicional en la consola para depuración
        console.log('Estado de los elementos del formulario:');
        console.log('idClienteInput:', document.getElementById('idClienteInput'));
        console.log('idCliente:', document.getElementById('idCliente'));
        console.log('nombreCliente:', document.getElementById('nombreCliente'));
    }
}

// Función auxiliar para limpiar campos
function limpiarCamposCliente() {
    document.getElementById('idClienteInput').value = '';
    document.getElementById('idCliente').value = '';
    document.getElementById('nombreCliente').value = '';
}

/**
 * Muestra una notificación usando SweetAlert2 o alert como fallback
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

    // Solución para el problema de aria-hidden
    const ariaHiddenElements = document.querySelectorAll('[aria-hidden="true"]');
    
     // Función para remover aria-hidden del main container
     function removeAriaHiddenFromMain() {
        const mainContainer = document.querySelector('main.container-fluid[aria-hidden="true"]');
        if (mainContainer) {
            mainContainer.removeAttribute('aria-hidden');
            console.log('Se ha removido el atributo aria-hidden del contenedor principal');
            return true;
        }
        return false;
    }
    
    // Eliminar inmediatamente al cargar
    removeAriaHiddenFromMain();
    
    // Configurar un MutationObserver para monitorear cambios en los atributos
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && 
                mutation.attributeName === 'aria-hidden' &&
                mutation.target.tagName.toLowerCase() === 'main') {
                removeAriaHiddenFromMain();
            }
        });
    });
    
    // Observar cambios en el main container y sus atributos
    const mainContainer = document.querySelector('main.container-fluid');
    if (mainContainer) {
        observer.observe(mainContainer, { 
            attributes: true,
            attributeFilter: ['aria-hidden']
        });
    }
    
    // También observar el body para detectar cambios en la estructura
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['aria-hidden']
    });
    
    // Adicionalmente, monitorear el evento 'focus' para detectar cuándo
    // un elemento dentro de main recibe el foco
    document.addEventListener('focus', function(e) {
        const mainContainer = document.querySelector('main.container-fluid[aria-hidden="true"]');
        if (mainContainer && mainContainer.contains(e.target)) {
            mainContainer.removeAttribute('aria-hidden');
            console.log('Se ha removido aria-hidden del main porque un elemento interno recibió el foco');
        }
    }, true);
    
    // Monitorear los eventos de modal de Bootstrap
    if (typeof $ !== 'undefined') {
        $(document).on('shown.bs.modal', function() {
            // Cuando se muestra un modal, verificar el main
            setTimeout(removeAriaHiddenFromMain, 0);
        });
        
        $(document).on('hidden.bs.modal', function() {
            // Cuando se oculta un modal, verificar nuevamente
            setTimeout(removeAriaHiddenFromMain, 0);
        });
    }

    
    // Verificar que los elementos existan antes de agregar event listeners
    if (!DOM.facturaForm || !DOM.searchInput) {
        console.error('No se pudieron encontrar elementos DOM necesarios');
        return;
    }

    cargarFacturas();

    // Eventos para el código de barras
    if (DOM.barcodeInput) {
        // Manejar tanto el Enter como cuando el input pierde el foco
        DOM.barcodeInput.addEventListener('keydown', handleBarcodeScan);
        DOM.barcodeInput.addEventListener('blur', handleBarcodeScan);
    }

    DOM.facturaForm.addEventListener('submit', guardarFactura);

    DOM.searchInput.addEventListener('input', () => {
        const searchTerm = DOM.searchInput.value.toLowerCase();
        const filteredFacturas = facturas.filter(factura => 
            factura.numero_factura?.toString().includes(searchTerm) || 
            factura.cliente?.nombre.toLowerCase().includes(searchTerm)
        );
        renderFacturaTable(filteredFacturas);
    });

    
    // Evento para el input del cliente
    const idClienteInput = document.getElementById('idClienteInput');
    if (idClienteInput) {
        // Eliminar todos los event listeners anteriores
        idClienteInput.replaceWith(idClienteInput.cloneNode(true));
    
        // Obtener la nueva referencia
        const newIdClienteInput = document.getElementById('idClienteInput');
    
        // Agregar un único listener
        newIdClienteInput.addEventListener('change', async (e) => {
            // Si hay una selección en proceso, no hacer nada
            if (seleccionEnProceso) {
                return;
            }
            
            const clienteId = e.target.value;
            if (clienteId) {
                try {
                    // Usar la ruta de búsqueda
                    const response = await fetch(`/facturas/api/clientes/buscar/${encodeURIComponent(clienteId)}`);
                    
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error('Respuesta del servidor no válida');
                    }
                    
                    const data = await response.json();
                    
                    if (data.success && data.clientes && data.clientes.length > 0) {
                        // Si encontramos al menos un cliente que coincida exactamente, seleccionarlo
                        const clienteExacto = data.clientes.find(c => 
                            c.id === clienteId || c.id.toLowerCase() === clienteId.toLowerCase()
                        );
                        
                        if (clienteExacto) {
                            document.getElementById('idCliente').value = clienteExacto.id;
                            document.getElementById('nombreCliente').value = clienteExacto.nombre;
                            mostrarNotificacion('Cliente seleccionado correctamente', 'success');
                        } else {
                            // No mostrar advertencia aquí, esperar a que el usuario termine de escribir
                            // o buscar coincidencias parciales
                            const mejorCoincidencia = data.clientes[0];
                            document.getElementById('idCliente').value = mejorCoincidencia.id;
                            document.getElementById('nombreCliente').value = mejorCoincidencia.nombre;
                            mostrarNotificacion('Cliente seleccionado (coincidencia parcial)', 'info');
                        }
                    } else {
                        // Solo mostrar advertencia y limpiar campos si no estamos en medio de una búsqueda
                        if (e.type === 'blur' || e.key === 'Enter') {
                            e.target.value = '';
                            document.getElementById('idCliente').value = '';
                            document.getElementById('nombreCliente').value = '';
                            mostrarNotificacion('Cliente no encontrado', 'warning');
                        }
                    }
                } catch (error) {
                    console.error('Error al validar cliente:', error);
                    if (e.type === 'blur' || e.key === 'Enter') {
                        e.target.value = '';
                        document.getElementById('idCliente').value = '';
                        document.getElementById('nombreCliente').value = '';
                        mostrarNotificacion('Error al validar el cliente', 'error');
                    }
                }
            }
        });
    }

    const productSearch = document.getElementById('productSearch');
    if (productSearch) {
        productSearch.addEventListener('input', (e) => buscarProductos(e.target));
        // Ocultar sugerencias cuando el campo pierde el foco
        productSearch.addEventListener('blur', () => {
            setTimeout(() => {
                document.getElementById('productSuggestions').style.display = 'none';
            }, 200);
        });
    }

    // parámetro para aplicar nota crédito
    const urlParams = new URLSearchParams(window.location.search);
    const aplicarNC = urlParams.get('aplicar_nc');

    if (aplicarNC && typeof abrirModalNotaCredito === 'function') {
        // Si existe el parámetro y la función, abrir el modal
        setTimeout(() => {
            abrirModalNotaCredito(parseInt(aplicarNC));
        }, 500); // Pequeño retraso para asegurar que todos los datos estén cargados
    }
});

    

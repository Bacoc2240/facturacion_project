/**
 * nota_credito.js 
 * 
 * Este módulo se encarga exclusivamente de la creación y gestión de notas crédito.
 * NO incluye funciones para visualizar notas existentes, ya que esa funcionalidad
 * está en notas_asociadas.js.
 */

// Variables globales
let numeroNotaCredito = 1; // Valor predeterminado para el número de nota crédito

// Funciones globales que exportamos para uso en otros archivos
window.cargarYMostrarModalNC = cargarYMostrarModalNC;

// Evento personalizado que podría ser disparado por facturas.js
document.addEventListener('facturaCargada', function(event) {
    const facturaData = event.detail;
    if (facturaData && facturaData.id) {
        abrirModalNotaCredito(facturaData.id, facturaData);
    }
});

// Ejecutar verificación de dependencias cuando se carga el script
document.addEventListener('DOMContentLoaded', function() {
    console.log('Módulo de nota crédito cargado correctamente');
    verificarDependencias();
});

/**
 * Función principal para cargar y mostrar el modal de nota crédito
 * @param {number} facturaId - ID de la factura
 */
function cargarYMostrarModalNC(facturaId) {
    console.log("cargarYMostrarModalNC llamada con ID:", facturaId);
    
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
                abrirModalNotaCredito(facturaId, data.factura);
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
    
    // Verificar y cargar FontAwesome si es necesario
    asegurarIconosFontAwesome();
    
    console.log('Verificación de dependencias completada.');
}

/**
 * Asegura que se carguen correctamente los íconos de FontAwesome
 */
function asegurarIconosFontAwesome() {
    // Verificar si ya está cargado Font Awesome
    const fontAwesomeLoaded = document.querySelector('link[href*="font-awesome"]') !== null ||
                              document.querySelector('script[src*="fontawesome"]') !== null;
    
    if (!fontAwesomeLoaded) {
        console.log('FontAwesome no detectado, cargando dinámicamente...');
        
        // Crear elemento link para cargar Font Awesome desde CDN
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
        
        // Añadir al head del documento
        document.head.appendChild(link);
        
        // Definir estilos de respaldo para el ícono de papelera por si acaso
        const style = document.createElement('style');
        style.textContent = `
            .btn-outline-danger.eliminar-item {
                color: #dc3545;
                border-color: #dc3545;
                background-color: transparent;
            }
            .btn-outline-danger.eliminar-item:hover {
                color: white;
                background-color: #dc3545;
            }
            /* Estilo de respaldo para el ícono de papelera */
            .fa-trash::before {
                content: "🗑";
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Abre el modal para crear una nota crédito
 * @param {number} facturaId - ID de la factura
 * @param {Object} facturaData - Datos de la factura (opcional)
 */
function abrirModalNotaCredito(facturaId, facturaData = null) {
    console.log("abrirModalNotaCredito llamada con ID:", facturaId);
    
    // Si no tenemos los datos de la factura, necesitamos cargarlos
    if (!facturaData) {
        cargarYMostrarModalNC(facturaId); // Esto ya maneja la carga de datos
        return;
    }
    
    // Si ya tenemos los datos, mostramos el modal directamente
    (async function() {
        try {
            // Obtener el número de nota crédito
            let numeroNC;
            try {
                numeroNC = await obtenerSiguienteNumeroNC();
                console.log("Número de nota crédito obtenido:", numeroNC);
            } catch (error) {
                console.warn("No se pudo obtener el número de nota crédito, usando valor predeterminado:", error);
                numeroNC = numeroNotaCredito;
                
                await Swal.fire({
                    title: 'Advertencia',
                    text: 'No se pudo obtener el número de nota crédito automáticamente. Se usará un valor predeterminado.',
                    icon: 'warning',
                    confirmButtonText: 'Continuar'
                });
            }
            
            // Crear el contenido del modal
            const modalContent = crearContenidoModalNotaCredito(facturaId, facturaData, numeroNC);
            
            // Asegurarse de que el modal existe en el DOM
            crearModalSiNoExiste();
            
            // Mostrar el modal
            document.getElementById('notaCreditoModalContent').innerHTML = modalContent;
            
            // Usar Bootstrap para mostrar el modal
            const modalElement = document.getElementById('notaCreditoModal');
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            
            // Inicializar eventos del formulario
            inicializarEventosNotaCredito(facturaId, facturaData);
            
        } catch (error) {
            console.error('Error al mostrar el modal:', error);
            Swal.fire({
                title: 'Error',
                text: 'No se pudo abrir el formulario de nota crédito',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        }
    })();
}

/**
 * Asegura que el modal existe en el DOM
 */
function crearModalSiNoExiste() {
    // Crear el modal si no existe
    if (!document.getElementById('notaCreditoModal')) {
        console.log("Creando el modal en el DOM");
        const modalDiv = document.createElement('div');
        modalDiv.className = 'modal fade';
        modalDiv.id = 'notaCreditoModal';
        modalDiv.tabIndex = '-1';
        modalDiv.setAttribute('aria-labelledby', 'notaCreditoModalLabel');
        modalDiv.setAttribute('aria-hidden', 'true');
        
        modalDiv.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content" id="notaCreditoModalContent">
                <!-- El contenido se generará dinámicamente -->
            </div>
        </div>
        `;
        
        document.body.appendChild(modalDiv);
    }
}

/**
 * Obtiene el siguiente número de nota crédito
 * @returns {Promise<number>} Promesa que resuelve al próximo número de nota crédito
 */
function obtenerSiguienteNumeroNC() {
    // Ruta correcta según el controlador
    const ruta = '/notacredito/api/notas-credito/siguiente-numero';
    console.log(`Solicitando número de nota crédito a: ${ruta}`);
    
    return fetch(ruta)
        .then(response => {
            console.log(`Respuesta para ${ruta}:`, response.status);
            
            if (!response.ok) {
                throw new Error(`Error en la respuesta: ${response.status} ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log(`Datos recibidos de ${ruta}:`, data);
            
            if (data.success && data.numero) {
                return data.numero;
            } else if (data.success && typeof data.siguiente_numero !== 'undefined') {
                return data.siguiente_numero;
            } else {
                throw new Error('Formato de respuesta inválido al obtener número de nota crédito');
            }
        })
        .catch(error => {
            console.error(`Error al obtener número de nota crédito:`, error);
            throw error;
        });
}

/**
 * Crea el contenido HTML para el modal de nota crédito
 * @param {number} facturaId - ID de la factura
 * @param {Object} factura - Datos de la factura
 * @param {string} numeroNC - Número de la nota crédito
 * @returns {string} HTML del contenido del modal
 */
function crearContenidoModalNotaCredito(facturaId, factura, numeroNC) {
    // Usar la fecha de la factura como fecha de emisión NC según requisito DIAN
    const fechaEmisionNC = factura.fecha || new Date().toISOString().split('T')[0];
    
    // Lista de motivos DIAN
    const motivosDIAN = [
        { id: 1, descripcion: 'Devolución parcial de los bienes y/o no aceptación parcial del servicio' },
        { id: 2, descripcion: 'Anulación de factura electrónica' },
        { id: 3, descripcion: 'Rebaja o descuento parcial o total' },
        { id: 4, descripcion: 'Ajuste de precio' },
        { id: 5, descripcion: 'Descuento comercial por pronto pago' },
        { id: 6, descripcion: 'Descuento comercial por volumen de ventas' }
    ];
    
    // Opciones para el select de motivos
    const opcionesMotivos = motivosDIAN.map(motivo => 
        `<option value="${motivo.id}">${motivo.descripcion}</option>`
    ).join('');
    
    // Extraer datos del cliente con validación para evitar errores
    const cliente = factura.cliente || {};
    
    // Obtener el nombre del vendedor/empleado
    let nombreVendedor = 'No especificado';
    
    // 1. Verificar en factura.empleado
    if (factura.empleado) {
        if (typeof factura.empleado === 'object') {
            nombreVendedor = factura.empleado.nombre || 
                            factura.empleado.nombre_completo ||
                            factura.empleado.nombre_apellidos || 
                            factura.empleado.nombre_empleado ||
                            factura.empleado.nombre_usuario ||
                            nombreVendedor;
        } else if (typeof factura.empleado === 'string') {
            nombreVendedor = factura.empleado;
        }
    } 
    // 2. Verificar en factura.vendedor
    else if (factura.vendedor) {
        if (typeof factura.vendedor === 'object') {
            nombreVendedor = factura.vendedor.nombre || 
                            factura.vendedor.nombre_completo ||
                            factura.vendedor.nombre_apellidos || 
                            factura.vendedor.nombre_vendedor ||
                            nombreVendedor;
        } else if (typeof factura.vendedor === 'string') {
            nombreVendedor = factura.vendedor;
        }
    }
    // 3. Verificar en factura.id_empleado
    else if (factura.id_empleado && nombreVendedor === 'No especificado') {
        nombreVendedor = `Empleado ID: ${factura.id_empleado}`;
    }
    
    // Los productos vienen en factura.productos
    const detalles = factura.productos || [];
    
    // Crear filas de productos
    let filasProductos = '<tr><td colspan="8" class="text-center">No hay productos en esta factura</td></tr>';
    
    if (detalles && Array.isArray(detalles) && detalles.length > 0) {
        filasProductos = detalles.map((detalle, index) => {
            // Asegurarnos de que detalle.producto existe
            const producto = detalle.producto || {};
            
            // Extraer datos del detalle y producto
            const codigo = producto.codigo_barras || 'N/A';
            const nombre = producto.nombre || 'Producto no encontrado';
            
            // Determinar la unidad basada en la categoría del producto
            let unidad = 'UND'; // valor por defecto
            if (producto.categoria) {
                // Convertir a minúsculas para hacer la comparación insensible a mayúsculas
                const categoria = producto.categoria.toLowerCase();
                if (categoria.includes('perfume') || categoria.includes('ambientador')) {
                    unidad = 'ml';
                } else if (categoria.includes('accesorio')) {
                    unidad = 'UND';
                }
            }
            
            // Valores para los campos
            const precioUnitario = parseFloat(detalle.precio_unitario || 0);
            const cantidad = parseFloat(detalle.cantidad || 0);
            const porcentajeIva = detalle.porcentaje_iva || 19.0;
            const subtotal = precioUnitario * cantidad;
            
            // Opciones de IVA según el valor original
            const ivaOptions = `
                <option value="0" ${porcentajeIva === 0 ? 'selected' : ''}>0%</option>
                <option value="5" ${porcentajeIva === 5 ? 'selected' : ''} ${porcentajeIva < 5 ? 'disabled' : ''}>5%</option>
                <option value="19" ${porcentajeIva === 19 ? 'selected' : ''} ${porcentajeIva < 19 ? 'disabled' : ''}>19%</option>
            `;
            
            return `
            <tr data-producto-id="${producto.id || ''}" data-detalle-id="${detalle.id || ''}" data-original-iva="${porcentajeIva}">
                <td>${codigo}</td>
                <td>${nombre}</td>
                <td>${unidad}</td>
                <td>
                    <input type="number" class="form-control item-cantidad" 
                           value="${cantidad}" 
                           max="${cantidad}" 
                           min="0" 
                           data-original="${cantidad}">
                </td>
                <td class="text-right">
                    <input type="number" class="form-control item-precio" 
                           value="${precioUnitario.toFixed(2)}" 
                           step="0.01">
                </td>
                <td class="text-right">
                    <select class="form-control item-iva">
                        ${ivaOptions}
                    </select>
                </td>
                <td class="text-right subtotal-item" data-subtotal="${subtotal.toFixed(2)}">${subtotal.toFixed(2)}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger eliminar-item">
                        <i class="fa fa-trash"></i>
                    </button>
                </td>
            </tr>
            `;
        }).join('');
    }
    
    // Construir el HTML completo del modal
    return `
    <div class="modal-header">
        <h5 class="modal-title">NOTA CRÉDITO DE LA FACTURA ELECTRÓNICA DE VENTA N° ${factura.prefijo || ''}${factura.numero_factura || ''}</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
    <div class="modal-body">
        <form id="formNotaCredito">
            <input type="hidden" name="factura_id" value="${facturaId}">
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="form-group mb-2">
                        <label>Número Nota Crédito:</label>
                        <input type="text" class="form-control" value="NC${numeroNC}" readonly>
                        <input type="hidden" name="numero" value="${numeroNC}">
                    </div>
                    <div class="form-group mb-2">
                        <label>Cliente:</label>
                        <input type="text" class="form-control" value="${cliente.nombre || 'No especificado'}" readonly>
                    </div>
                    <div class="form-group mb-2">
                        <label>NIT:</label>
                        <input type="text" class="form-control" value="${cliente.id || 'N/A'}" readonly>
                    </div>
                    <div class="form-group mb-2">
                        <label>Dirección:</label>
                        <input type="text" class="form-control" value="${cliente.direccion || 'N/A'}" readonly>
                    </div>
                    <div class="form-group mb-2">
                        <label>Ciudad:</label>
                        <input type="text" class="form-control" value="${cliente.ciudad || 'PAMPLONA'}" readonly>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group mb-2">
                        <label>Fecha Factura:</label>
                        <input type="date" class="form-control" value="${factura.fecha || ''}" readonly>
                    </div>
                    <div class="form-group mb-2">
                        <label>Fecha Emisión NC:</label>
                        <input type="date" name="fecha_emision_nc" class="form-control" value="${fechaEmisionNC}" required>
                    </div>
                    <div class="form-group mb-2">
                        <label>Forma de Pago:</label>
                        <input type="text" class="form-control" value="${factura.metodo_pago || factura.forma_pago || 'CRÉDITO'}" readonly>
                    </div>
                    <div class="form-group mb-2">
                        <label>Vendedor:</label>
                        <input type="text" name="vendedor" class="form-control" value="${nombreVendedor}" readonly>
                    </div>
                    <div class="form-group mb-2">
                        <label>Motivo DIAN: <span class="text-danger">*</span></label>
                        <select name="motivo_dian" class="form-control" required>
                            <option value="">Seleccione un motivo</option>
                            ${opcionesMotivos}
                        </select>
                    </div>
                </div>
            </div>
            
            <h5 class="mt-4">Detalle de la Nota Crédito Electrónica</h5>
            <div class="table-responsive">
                <table class="table table-bordered table-sm">
                    <thead class="table-light">
                        <tr>
                            <th>Código</th>
                            <th>Descripción</th>
                            <th>Unid</th>
                            <th>Cant</th>
                            <th>V. Unit</th>
                            <th>IVA</th>
                            <th>Valor Total</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody id="detalleProductosNC">
                        ${filasProductos}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="5"></td>
                            <td class="text-right"><strong>Subtotal:</strong></td>
                            <td class="text-right" id="subtotalNC">${factura.subtotal ? parseFloat(factura.subtotal).toFixed(2) : '0.00'}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td colspan="5"></td>
                            <td class="text-right"><strong>IVA:</strong></td>
                            <td class="text-right" id="ivaNC">${factura.iva ? parseFloat(factura.iva).toFixed(2) : '0.00'}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td colspan="5"></td>
                            <td class="text-right"><strong>Total:</strong></td>
                            <td class="text-right" id="totalNC">${factura.total ? parseFloat(factura.total).toFixed(2) : '0.00'}</td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div class="form-group mt-3">
                <label>Observaciones (máx. 500 caracteres):</label>
                <textarea name="observaciones" class="form-control" rows="3" maxlength="500"></textarea>
                <small class="text-muted caracteres-restantes">500 caracteres restantes</small>
            </div>
            
            <div class="form-group mt-3">
                <label>Adjuntar archivo:</label>
                <input type="file" name="archivo_soporte" class="form-control">
                <small class="text-muted">Opcional: documento escaneado, correo electrónico, etc.</small>
            </div>
            
            <!-- Campos ocultos para el formulario -->
            <input type="hidden" name="detalles" id="detallesNCJSON" value="[]">
            <input type="hidden" name="subtotal" id="subtotalNCValue" value="${factura.subtotal || '0.00'}">
            <input type="hidden" name="iva" id="ivaNCValue" value="${factura.iva || '0.00'}">
            <input type="hidden" name="total" id="totalNCValue" value="${factura.total || '0.00'}">
        </form>
    </div>
    <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
        <button type="button" class="btn btn-primary" id="btnGuardarEnviarNC">Guardar y Enviar</button>
    </div>
    `;
}

/**
 * Inicializa los eventos del formulario de nota crédito
 * @param {number} facturaId - ID de la factura
 * @param {Object} factura - Datos de la factura
 */
function inicializarEventosNotaCredito(facturaId, factura) {
    console.log('Inicializando eventos del formulario de nota crédito');
    
    // Restringir IVA a no más del original
    document.querySelectorAll('.item-iva').forEach(select => {
        select.addEventListener('change', function() {
            const tr = this.closest('tr');
            const originalIva = parseFloat(tr.dataset.originalIva || 19);
            const selectedIva = parseFloat(this.value);
            
            if (selectedIva > originalIva) {
                this.value = originalIva;
                // Si hay función de notificación
                if (typeof mostrarNotificacion === 'function') {
                    mostrarNotificacion('No puede seleccionar un IVA mayor al original', 'warning');
                } else if (typeof Swal !== 'undefined') {
                    Swal.fire('Advertencia', 'No puede seleccionar un IVA mayor al original', 'warning');
                } else {
                    alert('No puede seleccionar un IVA mayor al original');
                }
            }
            
            actualizarTotalesNotaCredito();
        });
    });

    // Eliminar fila de producto (mediante botón trash icon)
    document.querySelectorAll('.eliminar-item').forEach(button => {
        button.addEventListener('click', function() {
            const fila = this.closest('tr');
            // En lugar de remover la fila, la ocultamos y ponemos cantidad a 0
            fila.classList.add('d-none');
            const cantidadInput = fila.querySelector('.item-cantidad');
            if (cantidadInput) {
                cantidadInput.value = 0;
            }
            actualizarTotalesNotaCredito();
        });
    });
    
    // Manejar cambios en cantidades y precios
    document.querySelectorAll('.item-cantidad, .item-precio').forEach(input => {
        input.addEventListener('change', function() {
            actualizarTotalesNotaCredito();
        });
        
        input.addEventListener('input', function() {
            actualizarTotalesNotaCredito();
        });
    });
    
    // Contador de caracteres en observaciones
    const observacionesTextarea = document.querySelector('textarea[name="observaciones"]');
    if (observacionesTextarea) {
        observacionesTextarea.addEventListener('input', function() {
            const caracteresRestantes = 500 - this.value.length;
            document.querySelector('.caracteres-restantes').textContent = `${caracteresRestantes} caracteres restantes`;
        });
    }
    
    // Evento para el cambio de motivo (anulación total)
    const motivoSelect = document.querySelector('select[name="motivo_dian"]');
    if (motivoSelect) {
        motivoSelect.addEventListener('change', function() {
            // Si se selecciona "Anulación de factura electrónica" (2), marcar todos los productos
            if (this.value === '2') {
                document.querySelectorAll('.item-cantidad').forEach(input => {
                    input.value = input.getAttribute('data-original');
                });
                actualizarTotalesNotaCredito();
            }
        });
    }
    
    // Botón Guardar y Enviar
    const btnGuardar = document.getElementById('btnGuardarEnviarNC');
    if (btnGuardar) {
        btnGuardar.addEventListener('click', function() {
            validarYEnviarNotaCredito(facturaId);
        });
    }
    
    // Inicializar totales
    actualizarTotalesNotaCredito();
}

/**
 * Actualiza los totales de la nota crédito basado en las cantidades
 */
function actualizarTotalesNotaCredito() {
    let subtotal = 0;
    let iva = 0;
    const detalles = [];
    
    // Verificar si el elemento existe antes de procesar
    const filas = document.querySelectorAll('#detalleProductosNC tr:not(.d-none)');
    if (!filas || filas.length === 0) {
        // Si no hay filas, establecer totales en cero
        if (document.getElementById('subtotalNC')) document.getElementById('subtotalNC').textContent = '0.00';
        if (document.getElementById('ivaNC')) document.getElementById('ivaNC').textContent = '0.00';
        if (document.getElementById('totalNC')) document.getElementById('totalNC').textContent = '0.00';
        
        // Actualizar campo oculto con array vacío
        const detallesInput = document.getElementById('detallesNCJSON');
        if (detallesInput) detallesInput.value = '[]';
        
        return;
    }
    
    filas.forEach(fila => {
        const cantidadInput = fila.querySelector('.item-cantidad');
        const precioInput = fila.querySelector('.item-precio');
        const ivaInput = fila.querySelector('.item-iva');
        
        // Verificar si los inputs existen
        if (!cantidadInput || !precioInput || !ivaInput) return;
        
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const precioUnitario = parseFloat(precioInput.value) || 0;
        const porcentajeIva = parseFloat(ivaInput.value) || 0;
        
        const subtotalItem = cantidad * precioUnitario;
        const ivaItem = subtotalItem * (porcentajeIva / 100);
        
        // Actualizar el subtotal en la fila
        const subtotalElement = fila.querySelector('.subtotal-item');
        if (subtotalElement) {
            subtotalElement.textContent = subtotalItem.toFixed(2);
            subtotalElement.dataset.subtotal = subtotalItem;
        }
        
        // Acumular totales
        subtotal += subtotalItem;
        iva += ivaItem;
        
        // Agregar al array de detalles si hay cantidad
        if (cantidad > 0) {
            detalles.push({
                detalle_id: fila.dataset.detalleId || '',
                producto_id: fila.dataset.productoId || '',
                cantidad: cantidad,
                precio_unitario: precioUnitario,
                porcentaje_iva: porcentajeIva
            });
        }
    });
    
    const total = subtotal + iva;
    
    // Actualizar los elementos en el formulario
    const subtotalElement = document.getElementById('subtotalNC');
    const ivaElement = document.getElementById('ivaNC');
    const totalElement = document.getElementById('totalNC');
    
    if (subtotalElement) subtotalElement.textContent = subtotal.toFixed(2);
    if (ivaElement) ivaElement.textContent = iva.toFixed(2);
    if (totalElement) totalElement.textContent = total.toFixed(2);
    
    // Actualizar campos ocultos para el formulario
    const detallesInput = document.getElementById('detallesNCJSON');
    if (detallesInput) detallesInput.value = JSON.stringify(detalles);
    
    // Actualizar campos ocultos para subtotal, iva y total si existen
    const subtotalInput = document.getElementById('subtotalNCValue');
    const ivaInput = document.getElementById('ivaNCValue');
    const totalInput = document.getElementById('totalNCValue');
    
    if (subtotalInput) subtotalInput.value = subtotal.toFixed(2);
    if (ivaInput) ivaInput.value = iva.toFixed(2);
    if (totalInput) totalInput.value = total.toFixed(2);
}

/**
 * Valida el formulario y muestra confirmación antes de enviar
 * @param {number} facturaId - ID de la factura
 */
function validarYEnviarNotaCredito(facturaId) {
    const form = document.getElementById('formNotaCredito');
    
    // Validar que el formulario sea válido
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Verificar que al menos un producto tenga cantidad mayor a cero
    const hayProductos = Array.from(document.querySelectorAll('.item-cantidad')).some(
        input => parseFloat(input.value) > 0
    );
    
    if (!hayProductos) {
        Swal.fire({
            title: 'Error',
            text: 'Debe incluir al menos un producto en la nota crédito',
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
        return;
    }
    
    // Mostrar confirmación
    Swal.fire({
        title: 'Confirmar envío',
        html: 'Al enviar la nota crédito electrónica, <strong>no podrá ser editada, anulada o borrada</strong>. ¿Desea continuar?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Guardar y enviar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            enviarNotaCredito(facturaId);
        }
    });
}

/**
 * Envía la nota crédito al servidor
 * @param {number} facturaId - ID de la factura
 */
function enviarNotaCredito(facturaId) {
    // Mostrar indicador de carga
    Swal.fire({
        title: 'Procesando',
        text: 'Guardando nota crédito...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Crear objeto FormData con los datos del formulario
    const form = document.getElementById('formNotaCredito');
    const formData = new FormData(form);
    
    // Ruta correcta según el controlador
    const ruta = '/notacredito/api/notas-credito';
    console.log(`Enviando nota crédito a: ${ruta}`);
    
    fetch(ruta, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log(`Respuesta para ${ruta}:`, response.status);
        
        if (!response.ok) {
            throw new Error(`Error en la respuesta: ${response.status} ${response.statusText}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log(`Datos recibidos de ${ruta}:`, data);
        
        if (!data.success && data.error) {
            throw new Error(data.error);
        }
        
        // Incrementar el número local para futuras notas crédito
        numeroNotaCredito++;
        
        // Cerrar el indicador de carga
        Swal.close();
        
        // Cerrar el modal
        try {
            const modalElement = document.getElementById('notaCreditoModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
        } catch (error) {
            console.warn('Error al cerrar el modal:', error);
            // Si falla con Bootstrap 5, intentar con Bootstrap 4
            $('#notaCreditoModal').modal('hide');
        }
        
        // Si tenemos un ID de nota crédito, mostrar confirmación de envío por correo
        if (data.nota_credito_id) {
            mostrarConfirmacionEnvioCorreo(data.nota_credito_id);
        } else {
            // Si no tenemos ID, solo mostrar mensaje de éxito
            Swal.fire({
                title: 'Nota Crédito Guardada',
                text: 'La nota crédito se ha guardado correctamente',
                icon: 'success',
                confirmButtonText: 'Aceptar'
            }).then(() => {
                window.location.reload();
            });
        }
    })
    .catch(error => {
        console.error('Error al guardar la nota crédito:', error);
        Swal.fire({
            title: 'Error',
            text: error.message || 'Ocurrió un error al procesar la nota crédito',
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    });
}

/**
 * Muestra modal para confirmar envío por correo
 * @param {number} notaCreditoId - ID de la nota crédito creada
 */
function mostrarConfirmacionEnvioCorreo(notaCreditoId) {
    // Mostrar mensaje de éxito antes
    Swal.fire({
        title: 'Nota Crédito Guardada',
        text: 'La nota crédito se ha creado exitosamente',
        icon: 'success',
        confirmButtonText: 'Continuar'
    }).then(() => {
        // Lista de posibles rutas para obtener datos del cliente
        const rutas = [
            `/notas-credito/api/notas-credito/${notaCreditoId}/cliente`,
            `/notacredito/api/notas-credito/${notaCreditoId}/cliente`,
            `/api/notas-credito/${notaCreditoId}/cliente`,
            `/api/notacredito/${notaCreditoId}/cliente`
        ];
        
        // Función para intentar cada ruta
        async function intentarObtenerCliente(index = 0) {
            if (index >= rutas.length) {
                // Si todas las rutas fallan, devolver un objeto vacío
                return { cliente: {} };
            }
            
            const ruta = rutas[index];
            console.log(`Intentando obtener datos del cliente con ruta: ${ruta}`);
            
            try {
                const response = await fetch(ruta);
                console.log(`Respuesta para ${ruta}:`, response.status);
                
                if (!response.ok) {
                    // Si falla, intentar con la siguiente ruta
                    return intentarObtenerCliente(index + 1);
                }
                
                const data = await response.json();
                console.log(`Datos recibidos de ${ruta}:`, data);
                return data;
            } catch (error) {
                console.error(`Error con ruta ${ruta}:`, error);
                // Si hay un error, intentar con la siguiente ruta
                return intentarObtenerCliente(index + 1);
            }
        }
        
        // Intentar obtener datos del cliente
        intentarObtenerCliente()
            .then(data => {
                const cliente = data.cliente || {};
                
                Swal.fire({
                    title: 'Enviar Nota Crédito por Correo',
                    html: `
                        <p>Confirma los datos del contacto para enviar la nota crédito:</p>
                        <div class="form-group mb-2">
                            <label>Correo electrónico:</label>
                            <input id="emailCliente" class="form-control" value="${cliente.correo_electronico || ''}">
                        </div>
                    `,
                    showCancelButton: true,
                    confirmButtonText: 'Enviar',
                    cancelButtonText: 'No enviar',
                    preConfirm: () => {
                        const email = document.getElementById('emailCliente').value;
                        if (!email || !email.includes('@')) {
                            Swal.showValidationMessage('Por favor ingrese un correo electrónico válido');
                            return false;
                        }
                        return { email };
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        enviarCorreoNotaCredito(notaCreditoId, result.value.email);
                    } else {
                        // Si se cancela, solo mostrar mensaje y recargar
                        Swal.fire({
                            title: 'Completado',
                            text: 'La nota crédito ha sido guardada sin enviar correo',
                            icon: 'info',
                            confirmButtonText: 'Aceptar'
                        }).then(() => {
                            // Recargar la página o actualizar la tabla de facturas
                            window.location.reload();
                        });
                    }
                });
            });
    });
}

/**
 * Envía la nota crédito por correo electrónico
 * @param {number} notaCreditoId - ID de la nota crédito
 * @param {string} email - Correo electrónico del destinatario
 */
function enviarCorreoNotaCredito(notaCreditoId, email) {
    Swal.fire({
        title: 'Enviando correo',
        text: 'Por favor espere...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Ruta correcta según el controlador
    const ruta = `/notacredito/api/notas-credito/${notaCreditoId}/enviar-correo`;
    console.log(`Enviando correo a: ${ruta}`);
    
    fetch(ruta, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
    })
    .then(response => {
        console.log(`Respuesta para ${ruta}:`, response.status);
        
        if (!response.ok) {
            throw new Error(`Error en la respuesta: ${response.status} ${response.statusText}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log(`Datos recibidos de ${ruta}:`, data);
        
        if (!data.success && data.error) {
            throw new Error(data.error);
        }
        
        Swal.fire({
            title: 'Correo Enviado',
            text: 'La nota crédito ha sido enviada correctamente por correo electrónico',
            icon: 'success',
            confirmButtonText: 'Aceptar'
        }).then(() => {
            // Recargar la página o actualizar la tabla de facturas
            window.location.reload();
        });
    })
    .catch(error => {
        console.error('Error al enviar el correo:', error);
        Swal.fire({
            title: 'Error',
            text: error.message || 'Error al enviar el correo electrónico',
            icon: 'error',
            confirmButtonText: 'Aceptar'
        }).then(() => {
            window.location.reload();
        });
    });
}
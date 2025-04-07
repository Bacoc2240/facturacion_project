/**
 * notas_asociadas.js - Versión reorganizada
 * 
 * Este módulo se encarga exclusivamente de mostrar las notas crédito y débito
 * existentes asociadas a las facturas.
 */

// Funciones globales que exportamos para uso en otros archivos
window.cargarResumenesNotas = cargarResumenesNotas;
window.mostrarModalNotasCredito = mostrarModalNotasCredito;
window.mostrarModalNotasDebito = mostrarModalNotasDebito;
window.verDetalleNota = verDetalleNota;
window.imprimirNota = imprimirNota;

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('Notas Asociadas - DOM cargado');
    cargarResumenesNotas();
});

/**
 * Carga los resúmenes de notas para todas las facturas en la tabla
 */
function cargarResumenesNotas() {
    console.log('Inicializando resúmenes de notas');
    
    // Buscar todas las filas de factura
    const facturaRows = document.querySelectorAll('tr[data-factura-id]');
    facturaRows.forEach(row => {
        const facturaId = row.getAttribute('data-factura-id');
        if (facturaId) {
            const resumenNCContainer = row.querySelector('#resumen-nc-' + facturaId) || 
                                       row.querySelector('.resumen-nc');
            const resumenNDContainer = row.querySelector('#resumen-nd-' + facturaId) || 
                                       row.querySelector('.resumen-nd');
            
            if (resumenNCContainer) {
                cargarResumenNotasCredito(facturaId, resumenNCContainer);
            }
            
            if (resumenNDContainer) {
                cargarResumenNotasDebito(facturaId, resumenNDContainer);
            }
        }
    });
}

/**
 * Carga el resumen de notas crédito para una factura
 * @param {number} facturaId - ID de la factura
 * @param {HTMLElement} container - Contenedor para mostrar el resumen
 */
function cargarResumenNotasCredito(facturaId, container) {
    // Mostrar indicador de carga
    container.innerHTML = '<small class="text-muted">Cargando...</small>';
    
    // Lista de posibles rutas a probar
    const rutas = [
        '/notacredito/api/factura/' + facturaId + '/asociadas',
        '/notas-credito/api/factura/' + facturaId + '/asociadas',
        '/api/notas-credito/factura/' + facturaId,
        '/notacredito/api/factura/' + facturaId + '/notas'
    ];
    
    // Intentar cargar desde alguna ruta válida
    intentarCargarDesdeRutas(rutas, 0, function(data) {
        if (data && data.notas && data.notas.length > 0) {
            // Mostrar conteo con badge y enlace para ver detalles
            container.innerHTML = `
                <small>
                    <span class="badge badge-danger">${data.notas.length}</span>
                    <a href="#" onclick="mostrarModalNotasCredito(${facturaId}); return false;">
                        Ver notas
                    </a>
                </small>
            `;
        } else {
            // Si no hay notas, limpiar el contenedor
            container.innerHTML = '';
        }
    });
}

/**
 * Carga el resumen de notas débito para una factura
 * @param {number} facturaId - ID de la factura
 * @param {HTMLElement} container - Contenedor para mostrar el resumen
 */
function cargarResumenNotasDebito(facturaId, container) {
    // Mostrar indicador de carga
    container.innerHTML = '<small class="text-muted">Cargando...</small>';
    
    // Lista de posibles rutas a probar
    const rutas = [
        '/notadebito/api/factura/' + facturaId + '/asociadas',
        '/notas-debito/api/factura/' + facturaId + '/asociadas',
        '/api/notas-debito/factura/' + facturaId,
        '/notadebito/api/factura/' + facturaId + '/notas'
    ];
    
    // Intentar cargar desde alguna ruta válida
    intentarCargarDesdeRutas(rutas, 0, function(data) {
        if (data && data.notas && data.notas.length > 0) {
            // Mostrar conteo con badge y enlace para ver detalles
            container.innerHTML = `
                <small>
                    <span class="badge badge-warning">${data.notas.length}</span>
                    <a href="#" onclick="mostrarModalNotasDebito(${facturaId}); return false;">
                        Ver notas
                    </a>
                </small>
            `;
        } else {
            // Si no hay notas, limpiar el contenedor
            container.innerHTML = '';
        }
    });
}

/**
 * Intenta cargar datos desde múltiples rutas hasta que una funcione
 * @param {Array} rutas - Lista de rutas a probar
 * @param {number} indice - Índice actual en la lista de rutas
 * @param {Function} callback - Función a llamar con los datos cuando se carguen
 */
function intentarCargarDesdeRutas(rutas, indice, callback) {
    // Si ya no hay más rutas que probar
    if (indice >= rutas.length) {
        console.warn('No se pudo cargar información de ninguna ruta');
        callback(null);
        return;
    }
    
    const ruta = rutas[indice];
    console.log('Intentando cargar desde:', ruta);
    
    fetch(ruta)
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP Error ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            callback(data);
        })
        .catch(function(error) {
            console.warn('Error con ruta ' + ruta + ':', error.message);
            // Intentar con la siguiente ruta
            intentarCargarDesdeRutas(rutas, indice + 1, callback);
        });
}

/**
 * Muestra un modal con las notas crédito asociadas a una factura
 * @param {number} facturaId - ID de la factura
 */
function mostrarModalNotasCredito(facturaId) {
    // Mostrar indicador de carga
    Swal.fire({
        title: 'Cargando notas crédito',
        text: 'Por favor espere...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Lista de posibles rutas a probar
    const rutas = [
        '/notacredito/api/factura/' + facturaId + '/asociadas',
        '/notas-credito/api/factura/' + facturaId + '/asociadas',
        '/api/notas-credito/factura/' + facturaId,
        '/notacredito/api/factura/' + facturaId + '/notas'
    ];
    
    // Intentar cargar desde alguna ruta válida
    intentarCargarDesdeRutas(rutas, 0, function(data) {
        Swal.close();
        
        if (data && data.notas && data.notas.length > 0) {
            mostrarTablaNotas(data.notas, 'crédito', facturaId);
        } else {
            Swal.fire('Información', 'No hay notas crédito asociadas a esta factura.', 'info');
        }
    });
}

/**
 * Muestra un modal con las notas débito asociadas a una factura
 * @param {number} facturaId - ID de la factura
 */
function mostrarModalNotasDebito(facturaId) {
    // Mostrar indicador de carga
    Swal.fire({
        title: 'Cargando notas débito',
        text: 'Por favor espere...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Lista de posibles rutas a probar
    const rutas = [
        '/notadebito/api/factura/' + facturaId + '/asociadas',
        '/notas-debito/api/factura/' + facturaId + '/asociadas',
        '/api/notas-debito/factura/' + facturaId,
        '/notadebito/api/factura/' + facturaId + '/notas'
    ];
    
    // Intentar cargar desde alguna ruta válida
    intentarCargarDesdeRutas(rutas, 0, function(data) {
        Swal.close();
        
        if (data && data.notas && data.notas.length > 0) {
            mostrarTablaNotas(data.notas, 'débito', facturaId);
        } else {
            Swal.fire('Información', 'No hay notas débito asociadas a esta factura.', 'info');
        }
    });
}

/**
 * Muestra una tabla con las notas en un modal
 * @param {Array} notas - Lista de notas
 * @param {string} tipo - Tipo de nota ('crédito' o 'débito')
 * @param {number} facturaId - ID de la factura asociada
 */
function mostrarTablaNotas(notas, tipo, facturaId) {
    if (!notas || notas.length === 0) {
        Swal.fire('Información', `No hay notas ${tipo} asociadas a esta factura.`, 'info');
        return;
    }
    
    // Determinar el título y clases según el tipo de nota
    const titulo = `Notas de ${tipo} - Factura #${facturaId}`;
    const badgeClass = tipo === 'crédito' ? 'badge-danger' : 'badge-warning';
    const tipoAbrev = tipo === 'crédito' ? 'NC' : 'ND';
    const tipoFuncion = tipo === 'crédito' ? 'notasCredito' : 'notasDebito';

    // Crear filas de la tabla
    let filasHTML = '';
    
    notas.forEach(nota => {
        const numero = nota.numero || nota.numero_nota || nota.id || 'N/A';
        const fecha = formatearFecha(nota.fecha || nota.fecha_emision || new Date().toISOString());
        const total = formatearMoneda(nota.total || nota.monto_total || 0);
        const estado = nota.estado || 'Procesada';
        const motivo = nota.motivo || nota.concepto || nota.motivo_dian || 'No especificado';
        const id = nota.id || '';
        
        filasHTML += `
            <tr>
                <td><span class="${badgeClass}">${tipoAbrev}</span> ${numero}</td>
                <td>${fecha}</td>
                <td>${total}</td>
                <td>${estado}</td>
                <td>${motivo}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-info" 
                            onclick="verDetalleNota('${tipoFuncion}', ${id})">
                        <i class="fa fa-eye"></i> Ver
                    </button>
                </td>
            </tr>
        `;
    });
    
    // Crear HTML para el modal
    const modalHTML = `
        <div class="table-responsive">
            <table class="table table-striped table-hover table-sm">
                <thead>
                    <tr>
                        <th>Número</th>
                        <th>Fecha</th>
                        <th>Total</th>
                        <th>Estado</th>
                        <th>Motivo</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${filasHTML}
                </tbody>
            </table>
        </div>
    `;
    
    // Mostrar modal usando SweetAlert2
    Swal.fire({
        title: titulo,
        html: modalHTML,
        width: '850px',
        confirmButtonText: 'Cerrar'
    });
}

function verDetalleNota(tipoNota, notaId) {
    console.log(`Mostrando detalle de ${tipoNota} con ID: ${notaId}`);
    
    // Mostrar indicador de carga
    Swal.fire({
        title: 'Cargando detalle',
        text: 'Por favor espere...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // URL para cargar la plantilla ver.html en el iframe
    const url = tipoNota === 'notasCredito' 
        ? `/notacredito/ver/${notaId}?modal=true`
        : `/notadebito/ver/${notaId}?modal=true`;
    
    // Altura calculada para el iframe (ajusta según necesites)
    const height = Math.max(600, window.innerHeight * 0.8);
    
    // Mostrar modal con iframe
    Swal.close(); // Cerrar el modal de carga
    
    Swal.fire({
        title: null,
        html: `<iframe src="${url}" style="width: 100%; height: ${height}px; border: none;"></iframe>`,
        width: '90%',
        padding: 0,
        background: '#fff',
        showConfirmButton: false,
        showCloseButton: false, // Ocultar la X en la esquina superior
        allowOutsideClick: false,
        customClass: {
            container: 'swal-wide',
            popup: 'swal-wide-popup'
        }
    });
}

// Añadir detector de eventos para mensajes desde el iframe
window.addEventListener('message', function(event) {
    if (event.data === 'closeModal') {
        if (Swal.isVisible()) {
            Swal.close();
        }
    }
});

/**
 * Muestra un modal con los detalles completos de una nota en formato similar a factura
 * @param {Object} data - Datos de la nota
 * @param {string} tipo - Tipo de nota ('crédito' o 'débito')
 * @param {number} notaId - ID de la nota
 */
function mostrarModalDetalle(data, tipo, notaId) {
    // Obtener la nota del formato de respuesta
    let nota = null;
    if (data.nota_credito) {
        nota = data.nota_credito;
    } else if (data.nota_debito) {
        nota = data.nota_debito;
    } else if (data.nota) {
        nota = data.nota;
    } else if (Array.isArray(data.notas) && data.notas.length > 0) {
        nota = data.notas[0];
    } else if (data.success && data.data) {
        nota = data.data;
    } else {
        nota = data;
    }
    
    if (!nota) {
        Swal.fire('Error', 'No se encontraron datos de la nota', 'error');
        return;
    }
    
    // Obtener información de la nota
    const numero = nota.numero || nota.numero_nota || nota.id || 'N/A';
    const fecha = formatearFecha(nota.fecha_emision || nota.fecha || new Date().toISOString());
    const tipoTexto = tipo === 'crédito' ? 'NOTA CRÉDITO' : 'NOTA DÉBITO';
    const tipoAbrev = tipo === 'crédito' ? 'NC' : 'ND';
    const facturaNumero = nota.factura_numero || (nota.factura && nota.factura.numero_factura) || 'N/A';
    const clienteNombre = nota.cliente_nombre || 'Cliente no especificado';
    const clienteNit = nota.cliente_nit || 'N/A';
    const subtotal = formatearMoneda(nota.subtotal || 0);
    const iva = formatearMoneda(nota.iva || 0);
    const total = formatearMoneda(nota.total || 0);
    const motivo = nota.motivo_descripcion || nota.motivo_dian || nota.concepto || nota.motivo || 'No especificado';
    
    // Determinar si tenemos información detallada de los ítems
    const items = nota.items || nota.detalles || [];
    
    // Crear filas de productos
    let itemsHTML = '';
    items.forEach(item => {
        const cantidad = item.cantidad || 0;
        const precioUnitario = formatearMoneda(item.precio_unitario || item.valor_unitario || 0);
        const porcentajeIva = item.porcentaje_iva || 0;
        const subtotalItem = formatearMoneda(item.subtotal || 0);
        
        itemsHTML += `
            <tr>
                <td>${item.producto_codigo || 'N/A'}</td>
                <td>${item.producto_nombre || 'Producto no especificado'}</td>
                <td>UND</td>
                <td>${cantidad}</td>
                <td class="text-right">${precioUnitario}</td>
                <td class="text-right">${porcentajeIva}%</td>
                <td class="text-right">${subtotalItem}</td>
            </tr>
        `;
    });
    
    // Determinar clase de badge según el tipo
    const badgeClass = tipo === 'crédito' ? 'badge-danger' : 'badge-warning';
    
    // Crear HTML para el modal usando las clases CSS de factura_print.css
    const modalHTML = `
        <div class="factura-container" id="nota-credito-imprimir">
            <!-- Encabezado de la nota -->
            <div class="factura-header">
                <div class="row">
                    <div class="col-6 logo-container">
                        <img src="/static/images/Ellas_&_Ellos.jpeg" alt="Logo" class="factura-logo" style="max-height: 180px; max-width: 360px;">
                    </div>
                    <div class="col-6 empresa-info">
                        <h3>PERFUMERÍA ELLAS & ELLOS</h3>
                        <p>NIT: 800.100.200-1</p>
                        <p>CC PLAZA REAL LOCAL 13</p>
                        <p>PAMPLONA - NORTE DE SANTANDER</p>
                        <p>ellasyellos@gmail.com</p>
                        <p>6337150</p>
                    </div>
                </div>
            </div>

            <!-- Título de la nota -->
            <div class="factura-titulo nota-credito-titulo">
                <div class="row">
                    <div class="col-8">
                        <h2>${tipoTexto} DE LA FACTURA ELECTRÓNICA DE VENTA N°</h2>
                        <p class="factura-original">${facturaNumero}</p>
                    </div>
                    <div class="col-4">
                        <div class="numero-factura numero-nc">
                            <span class="prefijo">${tipoAbrev}</span>
                            <span class="numero">${numero}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Información del cliente -->
            <div class="factura-cliente">
                <div class="row">
                    <div class="col-md-6">
                        <table class="table-info">
                            <tr>
                                <td class="label">Cliente:</td>
                                <td>${clienteNombre}</td>
                            </tr>
                            <tr>
                                <td class="label">Nit:</td>
                                <td>${clienteNit}</td>
                            </tr>
                            <tr>
                                <td class="label">Dirección:</td>
                                <td>${nota.cliente_direccion || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="label">Ciudad:</td>
                                <td>${nota.cliente_ciudad || 'PAMPLONA'}</td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <table class="table-info">
                            <tr>
                                <td class="label">Fecha Factura:</td>
                                <td>${nota.factura_fecha || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="label">Fecha Emisión NC:</td>
                                <td>${fecha}</td>
                            </tr>
                            <tr>
                                <td class="label">Forma de pago:</td>
                                <td>${nota.forma_pago || 'CRÉDITO'}</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Motivo DIAN -->
            <div class="motivo-dian">
                <strong>Motivo DIAN:</strong> ${motivo}
            </div>

            <!-- Tabla de productos -->
            <div class="factura-productos">
                <table class="table-productos">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Descripción</th>
                            <th>Unid</th>
                            <th>Cant</th>
                            <th>V. Unit</th>
                            <th>IVA</th>
                            <th>Valor Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsHTML}
                    </tbody>
                </table>
            </div>

            <!-- Pie de nota con totales -->
            <div class="factura-totales">
                <div class="row">
                    <div class="col-7">
                        <div class="valor-letras">
                            <p><strong>VALOR EN LETRAS:</strong> ${nota.valor_letras || 'No especificado'}</p>
                        </div>
                        <div class="factura-nota">
                            {% if nota.observaciones %}
                            <div class="observaciones">
                                <p><strong>Observaciones:</strong> ${nota.observaciones || 'No hay observaciones'}</p>
                            </div>
                            {% endif %}
                            <p><strong>Autorización de facturación No.</strong> 00165 <strong>aprobado en</strong> 2025-03-14 <strong>prefijo NC desde el número</strong> 1 <strong>al</strong> 1000</p>
                            <p>Régimen Común - Actividad Económica 4773</p>
                            <p>No somos Agentes de Retención de IVA</p>
                            <p>No somos Grandes Contribuyentes</p>
                        </div>
                    </div>
                    <div class="col-5">
                        <div class="totales-box">
                            <h4>Totales</h4>
                            <table class="table-totales">
                                <tr>
                                    <td>Total Bruto</td>
                                    <td class="text-right">${subtotal}</td>
                                </tr>
                                <tr>
                                    <td>IVA</td>
                                    <td class="text-right">${iva}</td>
                                </tr>
                                <tr class="total-pagar">
                                    <td>Total a Pagar</td>
                                    <td class="text-right">${total}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Firmas -->
            <div class="factura-firmas">
                <div class="row">
                    <div class="col-6 text-center">
                        <div class="firma-box">
                            <div class="firma-linea"></div>
                            <p>Elaborado por</p>
                        </div>
                    </div>
                    <div class="col-6 text-center">
                        <div class="firma-box">
                            <div class="firma-linea"></div>
                            <p>Firma Recibido</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pie de página -->
            <div class="factura-footer">
                <p class="original">ORIGINAL</p>
                <p class="pagina">Página: 1 de 1</p>
            </div>
        </div>
        
        <!-- Botones de acción (no se imprimirán) -->
        <div class="row mt-3 mb-3 no-print">
            <div class="col-md-12">
                <div class="d-flex justify-content-center">
                    <div class="btn-group">
                        <button class="btn btn-primary mr-2" onclick="window.print()">
                            <i class="fas fa-print"></i> Imprimir
                        </button>
                        <button class="btn btn-success mr-2" onclick="compartirNota(${notaId})">
                            <i class="fas fa-share-alt"></i> Compartir
                        </button>
                        <button class="btn btn-secondary" onclick="Swal.close()">
                            <i class="fas fa-arrow-left"></i> Volver
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Mostrar modal usando SweetAlert2
    Swal.fire({
        title: null,
        html: modalHTML,
        width: '850px',
        padding: '10px',
        background: '#fff',
        showConfirmButton: false,
        showCloseButton: true
    });
}

// Función para compartir la nota por correo
function compartirNota(notaId) {
    Swal.fire({
        title: 'Compartir Nota Crédito',
        html: `
            <div class="alert alert-info">
                <strong>Importante:</strong> Para compartir esta nota crédito, puede guardarla como PDF desde la opción "Imprimir" y luego enviarla por correo.
            </div>
            <ol>
                <li>Haga clic en el botón "Imprimir"</li>
                <li>En el diálogo de impresión, seleccione "Guardar como PDF"</li>
                <li>Guarde el archivo y adjúntelo a su correo electrónico</li>
            </ol>
        `,
        showCancelButton: true,
        confirmButtonText: 'Imprimir ahora',
        cancelButtonText: 'Cerrar',
    }).then((result) => {
        if (result.isConfirmed) {
            window.print();
        }
    });
}


/**
 * Crea una tabla HTML con los ítems de una nota
 * @param {Array} items - Lista de ítems
 * @returns {string} HTML de la tabla
 */
function crearTablaItems(items) {
    if (!items || items.length === 0) {
        return '<p>No hay ítems para mostrar</p>';
    }
    
    // Determinar las columnas a mostrar según la estructura del primer ítem
    const primerItem = items[0];
    const tieneProducto = primerItem.producto || primerItem.producto_id;
    const tieneDescripcion = primerItem.descripcion !== undefined;
    const tienePrecio = primerItem.precio_unitario !== undefined || primerItem.precio !== undefined;
    const tieneIva = primerItem.porcentaje_iva !== undefined || primerItem.iva !== undefined;
    
    let html = `
        <div class="table-responsive">
            <table class="table table-striped table-sm">
                <thead>
                    <tr>
                        ${tieneProducto ? '<th>Producto</th>' : ''}
                        ${tieneDescripcion ? '<th>Descripción</th>' : ''}
                        <th>Cantidad</th>
                        ${tienePrecio ? '<th>Precio Unitario</th>' : ''}
                        ${tieneIva ? '<th>IVA</th>' : ''}
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    items.forEach(item => {
        // Extraer datos del ítem
        let nombreProducto = 'N/A';
        if (item.producto) {
            nombreProducto = typeof item.producto === 'object' ? 
                (item.producto.nombre || 'Sin nombre') : item.producto;
        }
        
        const descripcion = item.descripcion || 'No especificado';
        const cantidad = item.cantidad || 0;
        const precioUnitario = item.precio_unitario || item.precio || 0;
        const porcentajeIva = item.porcentaje_iva || item.iva || 0;
        const subtotal = item.subtotal || (cantidad * precioUnitario) || 0;
        
        html += `
            <tr>
                ${tieneProducto ? `<td>${nombreProducto}</td>` : ''}
                ${tieneDescripcion ? `<td>${descripcion}</td>` : ''}
                <td>${cantidad}</td>
                ${tienePrecio ? `<td>${formatearMoneda(precioUnitario)}</td>` : ''}
                ${tieneIva ? `<td>${porcentajeIva}%</td>` : ''}
                <td>${formatearMoneda(subtotal)}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

function imprimirNota(tipoNota, notaId) {
    // Utilizar las URLs reales que funcionan en tu sistema
    const urlImpresion = tipoNota === 'notasCredito' 
        ? `/notacredito/ver/${notaId}?print=true`  // Cambiar a la ruta real que funciona
        : `/notadebito/ver/${notaId}?print=true`;  // Cambiar a la ruta real que funciona
        
    window.open(urlImpresion, '_blank');
}

/**
 * Formatea una fecha a un formato legible
 * @param {string} fecha - Fecha a formatear
 * @returns {string} Fecha formateada
 */
function formatearFecha(fecha) {
    if (!fecha) return 'N/A';
    
    try {
        const date = new Date(fecha);
        return date.toLocaleDateString('es-CO', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (e) {
        console.error('Error al formatear fecha:', e);
        return fecha;
    }
}

/**
 * Formatea un número como moneda
 * @param {number} valor - Valor a formatear
 * @returns {string} Valor formateado como moneda
 */
function formatearMoneda(valor) {
    const monto = parseFloat(valor);
    if (isNaN(monto)) return '$0';
    
    try {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 2
        }).format(monto);
    } catch (e) {
        console.error('Error al formatear moneda:', e);
        return '$' + monto.toFixed(2);
    }
}
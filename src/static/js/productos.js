document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    console.log('Rutas configuradas:', ROUTES);
    const productTable = document.querySelector('table tbody');
    const searchInput = document.getElementById('search');
    const generoFilter = document.getElementById('generoFilter');
    const categoriaFilter = document.getElementById('categoriaFilter');
    const activoFilter = document.getElementById('activoFilter');
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', handleSubmit);
        console.log('Event listener de creación registrado');
    }
    const editModal = document.getElementById('editProductModal');
    const editProductForm = document.getElementById('editProductForm');
    if (editProductForm) {
        editProductForm.addEventListener('submit', handleEditSubmit);
        console.log('Event listener de edición registrado'); // Para debugging
    }

    const cancelButton = document.querySelector('#editProductModal .btn-secondary');
    cancelButton.addEventListener('click', function() {
        $('#editProductModal').modal('hide');
        // Opcionalmente, limpiar el formulario
        document.getElementById('editProductForm').reset();
    });

   
    

    // Función para construir URLs
    function buildUrl(action, id) {
        return `${ROUTES.base}/${id}/${action}`;
    }

    // Función para mostrar alertas
    function mostrarAlerta(mensaje, tipo) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${mensaje}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `;
        const container = document.querySelector('.container-fluid');
        const firstChild = container.firstChild;
        container.insertBefore(alertDiv, firstChild);
        
        // Remover la alerta después de 3 segundos
        setTimeout(() => {
            $(alertDiv).fadeOut('slow', function() {
                $(this).remove();
            });
        }, 3000);
    }

    // Función para renderizar la tabla
    function renderTable(products, showSuspendedOptions = false) {
        console.log('Iniciando renderizado de tabla con productos:', products);
        productTable.innerHTML = '';
        
        products.forEach(product => {
            const row = document.createElement('tr');
            row.setAttribute('data-id', product.id);
            
            const formattedPrice = (product.precio !== null && !isNaN(product.precio)) 
                ? Number(product.precio).toFixed(2) 
                : '0.00';
            
            // Agregamos una clase especial para productos suspendidos
            if (!product.activo) {
                row.classList.add('table-secondary');
            }
    
            row.innerHTML = `
                <td>${product.codigo_barras}</td>
                <td>${product.nombre}</td>
                <td>${product.genero}</td>
                <td>${product.descripcion}</td>
                <td>${product.stock}</td>
                <td>${formattedPrice}</td>
                <td>${product.categoria || 'Sin categoría'}</td>
                <td>${product.activo ? 'Sí' : 'No'}</td>
                <td class="text-center">
                    <button class="btn btn-warning btn-sm edit-btn" data-id="${product.id}">
                        Editar
                    </button>
                    ${showSuspendedOptions ? 
                        `<button class="btn btn-success btn-sm reactivate-btn" data-id="${product.id}">
                            Reactivar
                        </button>` :
                        product.activo ? 
                            `<button class="btn btn-danger btn-sm suspend-btn" data-id="${product.id}">
                                Suspender
                            </button>` : 
                            `<button class="btn btn-success btn-sm reactivate-btn" data-id="${product.id}">
                                Reactivar
                            </button>`
                    }
                </td>
            `;
            productTable.appendChild(row);
        });
        console.log('Tabla renderizada exitosamente');
    }

    // Función para cargar los productos
    async function loadProducts() {
        try {
            console.log('Iniciando carga de productos...');
            console.log('URL de carga:', ROUTES.api.lista);
            
            const response = await fetch(ROUTES.api.lista);
            console.log('Estado de la respuesta:', response.status);
    
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
    
            const products = await response.json();
            console.log('Datos recibidos:', products);
            
            // Ahora renderTable debería estar definida y disponible
            renderTable(products);
            return true;
        } catch (error) {
            console.error('Error al cargar productos:', error);
            mostrarAlerta('Error al cargar los productos', 'danger');
            return false;
        }
    }

    // Función para manejar la creación de un producto
    async function handleSubmit(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        
        // Debug: Mostrar datos del formulario
        console.log('Datos del formulario de creación:');
        for (let [key, value] of formData.entries()) {
            console.log(key, ':', value);
        }
        
        try {
            console.log('Iniciando petición a:', ROUTES.crear);
            const response = await fetch(ROUTES.crear, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  // Indicador de petición AJAX
                }
            });
    
            // Verificar el tipo de contenido de la respuesta
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('La respuesta del servidor no es JSON válido');
            }
    
            const data = await response.json();
            console.log('Respuesta del servidor:', data);
    
            if (!data.success) {
                throw new Error(data.error || 'Error al crear el producto');
            }
    
            // Cerrar el modal usando jQuery
            const $modal = $('#productModal');
            $modal.modal('hide');
            
            // Esperar a que el modal se cierre completamente antes de continuar
            await new Promise(resolve => {
                $modal.on('hidden.bs.modal', function () {
                    resolve();
                });
            });
    
            // Limpiar el formulario
            event.target.reset();
    
            // Actualizar la tabla de productos
            const productsLoaded = await loadProducts();
            if (!productsLoaded) {
                throw new Error('Error al actualizar la lista de productos');
            }
    
            // Mostrar mensaje de éxito
            mostrarAlerta('Producto creado exitosamente', 'success');
    
        } catch (error) {
            console.error('Error en la creación:', error);
            mostrarAlerta(error.message || 'Error al crear el producto', 'danger');
            
            // Si hay un modal abierto, mantenerlo abierto para que el usuario pueda corregir los datos
            const $modal = $('#productModal');
            if ($modal.hasClass('show')) {
                $modal.modal('show');
            }
        }
    }

    // Función para editar producto
    async function editProduct(id) {
        try {
            // Primero obtenemos los datos del producto
            const response = await fetch(`${ROUTES.base}/${id}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al obtener datos del producto');
            }
            
            const producto = await response.json();
            console.log('Datos del producto recibidos:', producto);
    
            // Llenamos el formulario
            document.getElementById('edit_id').value = producto.id;
            document.getElementById('edit_nombre').value = producto.nombre || '';
            document.getElementById('edit_categoria').value = producto.categoria || '';
            document.getElementById('edit_stock').value = producto.stock || 0;
            document.getElementById('edit_genero').value = producto.genero || '';
            document.getElementById('edit_precio').value = producto.precio ? 
                Number(producto.precio).toFixed(2) : '0.00';
            document.getElementById('edit_descripcion').value = producto.descripcion || '';
    
            // Mostramos el modal usando jQuery (Bootstrap 4.3.1)
            $('#editProductModal').modal('show');
        } catch (error) {
            console.error('Error al cargar producto:', error);
            mostrarAlerta('Error al cargar los datos del producto', 'danger');
        }
    }
    
    // Función para manejar el envío del formulario de edición
    async function handleEditSubmit(event) {
        event.preventDefault();
        const id = document.getElementById('edit_id').value;
        const formData = new FormData(event.target);
    
        console.log('ID del producto a editar:', id);
        console.log('Datos del formulario:');
        for (let [key, value] of formData.entries()) {
            console.log(key, ':', value);
        }
    
        try {
            const url = buildUrl('editar', id);
            console.log('URL de edición:', url);
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
    
            const data = await response.json();
            console.log('Respuesta del servidor:', data);
            
            if (!response.ok) {
                throw new Error(data.error || 'Error al actualizar el producto');
            }
    
            // Cerrar el modal usando jQuery (Bootstrap 4.3.1)
            $('#editProductModal').modal('hide');
    
            // Actualizar la tabla
            await loadProducts();
    
            // Mostrar mensaje de éxito
            mostrarAlerta('Producto actualizado exitosamente', 'success');
    
            // Limpiar el formulario
            event.target.reset();
    
        } catch (error) {
            console.error('Error en la actualización:', error);
            mostrarAlerta(error.message || 'Error al actualizar el producto', 'danger');
        }
    }
    // Eventos para suspender/reactivar producto
    async function suspendProduct(id) {
        if (confirm('¿Estás seguro de que quieres suspender este producto?')) {
            try {
                const response = await fetch(buildUrl('suspender', id), {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Error al suspender el producto');
                await loadProducts();
                mostrarAlerta('Producto suspendido exitosamente', 'success');
            } catch (error) {
                mostrarAlerta('Error al suspender el producto', 'danger');
            }
        }
    }

    async function reactivateProduct(id) {
        if (confirm('¿Estás seguro de que quieres reactivar este producto?')) {
            try {
                const response = await fetch(buildUrl('reactivar', id), {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Error al reactivar el producto');
                await loadProducts();
                mostrarAlerta('Producto reactivado exitosamente', 'success');
            } catch (error) {
                mostrarAlerta('Error al reactivar el producto', 'danger');
            }
        }
    }

    // Función para filtrar productos
    async function filterProducts(event) {
        // Prevenir el envío del formulario si existe el evento
        if (event) {
            event.preventDefault();
        }
    
        try {
            const filtroForm = document.getElementById('filtroProductosForm');
            if (!filtroForm) {
                console.error('No se encontró el formulario de filtro');
                return;
            }
    
            // Obtener los valores de los filtros
            const nombreValue = filtroForm.querySelector('input[name="nombre"]')?.value?.toLowerCase() || '';
            const generoValue = filtroForm.querySelector('select[name="genero"]')?.value || '';
            const categoriaValue = filtroForm.querySelector('select[name="categoria"]')?.value || '';
            const activoValue = filtroForm.querySelector('select[name="activo"]')?.value || '';
    
            console.log('Aplicando filtros:', {
                nombre: nombreValue,
                genero: generoValue,
                categoria: categoriaValue,
                activo: activoValue
            });
    
            // Construir la URL base para la API
            let apiUrl = ROUTES.api.lista;
            
            // Si estamos filtrando específicamente por productos inactivos,
            // usamos un endpoint específico para productos suspendidos
            if (activoValue === '0') {
                apiUrl = `${ROUTES.base}/suspendidos`;
                console.log('Consultando productos suspendidos...');
            }
    
            // Construir parámetros de consulta
            const params = new URLSearchParams();
            if (nombreValue) params.append('nombre', nombreValue);
            if (generoValue) params.append('genero', generoValue);
            if (categoriaValue) params.append('categoria', categoriaValue);
            if (activoValue) params.append('activo', activoValue);
    
            // Agregar parámetros a la URL si existen
            const finalUrl = params.toString() ? `${apiUrl}?${params.toString()}` : apiUrl;
            console.log('URL de consulta:', finalUrl);
    
            // Realizar la petición al servidor
            const response = await fetch(finalUrl, {
                method: 'GET',
                credentials: 'same-origin',  // Incluir cookies y credenciales de sesión
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',  // Identificar como petición AJAX
                    'Accept': 'application/json'
                }
            });
    
            if (!response.ok) {
                if (response.status === 403) {
                    throw new Error('No tienes permiso para acceder a esta información');
                }
                throw new Error(`Error HTTP: ${response.status}`);
            }
    
            
    
            let products = await response.json();
            console.log('Productos recibidos:', products.length);
    
            // Si no estamos usando el endpoint específico de suspendidos,
            // aplicamos los filtros en el cliente
            if (activoValue !== '0') {
                products = products.filter(product => {
                    const nombreMatch = !nombreValue || 
                        String(product.nombre || '').toLowerCase().includes(nombreValue);
                    const generoMatch = !generoValue || 
                        String(product.genero || '').toLowerCase() === generoValue.toLowerCase();
                    const categoriaMatch = !categoriaValue || 
                        String(product.categoria || '').toLowerCase() === categoriaValue.toLowerCase();
                    const activoMatch = !activoValue || 
                        (activoValue === '1' && product.activo) || 
                        (activoValue === '0' && !product.activo);
    
                    return nombreMatch && generoMatch && categoriaMatch && activoMatch;
                });
            }
    
            // Renderizar resultados
            if (products.length === 0) {
                productTable.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center">
                            No se encontraron productos que coincidan con los criterios de búsqueda
                        </td>
                    </tr>
                `;
            } else {
                // Modificamos renderTable para manejar productos suspendidos
                renderTable(products, activoValue === '0');
            }
    
        } catch (error) {
            console.error('Error al filtrar productos:', error);
            mostrarAlerta('Error al aplicar los filtros', 'danger');
        }
    }

    // Configurar event listeners para filtrado en tiempo real
    const filtroForm = document.getElementById('filtroProductosForm');
    if (filtroForm) {
        // Event listener para el envío del formulario
        filtroForm.addEventListener('submit', filterProducts);

        // Event listeners para filtrado en tiempo real
        const nombreInput = filtroForm.querySelector('input[name="nombre"]');
        const generoSelect = filtroForm.querySelector('select[name="genero"]');
        const categoriaSelect = filtroForm.querySelector('select[name="categoria"]');
        const activoSelect = filtroForm.querySelector('select[name="activo"]');

        if (nombreInput) nombreInput.addEventListener('input', filterProducts);
        if (generoSelect) generoSelect.addEventListener('change', filterProducts);
        if (categoriaSelect) categoriaSelect.addEventListener('change', filterProducts);
        if (activoSelect) activoSelect.addEventListener('change', filterProducts);
    }
    // Event Listeners
    document.querySelector('table').addEventListener('click', function(e) {
        const target = e.target;
        if (target.matches('.edit-btn')) {
            editProduct(target.dataset.id);
        } else if (target.matches('.suspend-btn')) {
            suspendProduct(target.dataset.id);
        } else if (target.matches('.reactivate-btn')) {
            reactivateProduct(target.dataset.id);
        }
    });

    searchInput?.addEventListener('input', filterProducts);
    generoFilter?.addEventListener('change', filterProducts);
    categoriaFilter?.addEventListener('change', filterProducts);
    productForm?.addEventListener('submit', handleSubmit);
    editProductForm?.addEventListener('submit', handleEditSubmit);

    // Inicializar
    loadProducts();
});
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const productTable = document.querySelector('table tbody');
    const searchInput = document.getElementById('search');
    const generoFilter = document.getElementById('generoFilter');
    const priceFilter = document.getElementById('priceFilter');
    const productForm = document.getElementById('productForm');
    const productModal = $('#productModal');

    let editMode = false;
    let editProductId = null;

    // Función para cargar los productos desde el servidor
    async function loadProducts() {
        try {
            const response = await fetch('/api/productos');
            const products = await response.json();
            renderTable(products);
        } catch (error) {
            console.error('Error al cargar productos:', error);
            alert('Error al cargar los productos');
        }
    }

    // Función para renderizar la tabla de productos
    function renderTable(products) {
        productTable.innerHTML = ''; // Limpiar la tabla
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.id}</td>
                <td>${product.nombre}</td>
                <td>${product.genero}</td>
                <td>${product.descripcion}</td>
                <td>${product.stock}</td>
                <td>${product.precio}</td>
                <td>${product.categoria}</td>
                <td class="text-center">
                    <button class="btn btn-warning btn-sm" onclick="editProduct(${product.id})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="suspendProduct(${product.id})">Suspender</button>
                </td>
            `;
            productTable.appendChild(row);
        });
    }

    // Función para manejar el envío del formulario
    async function handleSubmit(event) {
        event.preventDefault();
        const formData = new FormData(productForm);
        const productData = Object.fromEntries(formData.entries());

        try {
            const url = editMode ? `/api/productos/${editProductId}` : '/api/productos';
            const method = editMode ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message);
            }

            productModal.modal('hide');
            loadProducts();
            productForm.reset();
            editMode = false;
            editProductId = null;
            
        } catch (error) {
            alert(error.message);
        }
    }

    // Función para editar un producto
    async function editProduct(id) {
        try {
            const response = await fetch(`/api/productos/${id}`);
            const product = await response.json();
            
            // Rellenar el formulario con los datos del producto
            for (const [key, value] of Object.entries(product)) {
                const input = document.getElementById(`product${key.charAt(0).toUpperCase() + key.slice(1)}`);
                if (input) input.value = value;
            }
            
            editMode = true;
            editProductId = id;
            productModal.modal('show');
        } catch (error) {
            console.error('Error al cargar el producto:', error);
            alert('Error al cargar el producto');
        }
    }

    // Función para suspender un producto
    async function suspendProduct(id) {
        if (confirm('¿Estás seguro de que quieres suspender este producto?')) {
            try {
                const response = await fetch(`/api/productos/${id}/suspender`, {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Error al suspender el producto');
                
                loadProducts();
            } catch (error) {
                console.error('Error:', error);
                alert('Error al suspender el producto');
            }
        }
    }

    // Filtrado de productos
    function filterProducts() {
        const searchTerm = searchInput.value.toLowerCase();
        const genero = generoFilter.value;
        const price = priceFilter.value;

        const rows = productTable.getElementsByTagName('tr');
        Array.from(rows).forEach(row => {
            let show = true;
            const cells = row.getElementsByTagName('td');
            
            // Filtrar por búsqueda
            if (searchTerm) {
                show = false;
                Array.from(cells).forEach(cell => {
                    if (cell.textContent.toLowerCase().includes(searchTerm)) {
                        show = true;
                    }
                });
            }

            // Filtrar por género
            if (show && genero && cells[2].textContent !== genero) {
                show = false;
            }

            // Filtrar por precio
            if (show && price) {
                const productPrice = parseFloat(cells[5].textContent);
                switch (price) {
                    case 'low':
                        show = productPrice < 50000;
                        break;
                    case 'medium':
                        show = productPrice >= 50000 && productPrice <= 100000;
                        break;
                    case 'high':
                        show = productPrice > 100000;
                        break;
                }
            }

            row.style.display = show ? '' : 'none';
        });
    }

    // Event Listeners
    searchInput.addEventListener('input', filterProducts);
    generoFilter.addEventListener('change', filterProducts);
    priceFilter.addEventListener('change', filterProducts);
    productForm.addEventListener('submit', handleSubmit);

    // Inicializar
    loadProducts();

    // Exponer funciones globalmente
    window.editProduct = editProduct;
    window.suspendProduct = suspendProduct;
});




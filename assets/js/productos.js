document.addEventListener('DOMContentLoaded', function() {
    // Datos de ejemplo (en una aplicación real, estos datos vendrían del servidor)
    const products = [
        { ref: 'P001', name: 'Antonio - 15ml', genero: 'Hombre', price: 45000, stock: 100 },
        { ref: 'P002', name: 'U Mujer - 75ml', genero: 'Mujer', price: 80000, stock: 18 },
        { ref: 'P003', name: 'Fresh Escape - 50ml', genero: 'Mujer', price: 48000, stock: 22 },
        { ref: 'P004', name: 'The Secret - 50ml', genero: 'Hombre', price: 95000, stock: 9 },
        { ref: 'P005', name: 'Love Love Love - 80ml', genero: 'Mujer', price: 130000, stock: 4 },
        // Agregar más productos según sea necesario
    ];


    function openProductModal() {
        editMode = false;
        editProductRef = null;
        productForm.reset(); // Limpiar el formulario
        $('#productModal').modal('show');
    }

    // Referencias a elementos del DOM
    const productTable = document.getElementById('productTable');
    const searchInput = document.getElementById('search');
    const generoFilter = document.getElementById('generoFilter');
    const priceFilter = document.getElementById('priceFilter');
    const productForm = document.getElementById('productForm');
    const productModal = $('#productModal');
    const productFormSubmitButton = document.getElementById('productFormSubmit');

    let editMode = false;
    let editProductRef = null;

    // Función para renderizar la tabla de productos
    function renderTable(products) {
        productTable.innerHTML = ''; // Limpiar la tabla
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.ref}</td>
                <td>${product.name}</td>
                <td>${product.genero}</td>
                <td>${product.price.toFixed(2)}</td>
                <td>${product.stock}</td>
                <td class="text-center">
                    <button class="btn btn-warning btn-sm" onclick="editProduct('${product.ref}')">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteProduct('${product.ref}')">Eliminar</button>
                </td>
            `;
            productTable.appendChild(row);
        });
    }

    

    // Función para añadir un producto
    function addProduct() {
        const newProduct = {
            ref: document.getElementById('productRef').value,
            name: document.getElementById('productName').value,
            genero: document.getElementById('productGenero').value,
            price: parseFloat(document.getElementById('productPrice').value),
            stock: parseInt(document.getElementById('productStock').value, 10),
        };

        // Comprobar si el producto ya existe
        const existingProduct = products.find(p => p.ref === newProduct.ref || p.name === newProduct.name);
        if (existingProduct) {
            alert('El producto con esta referencia o nombre ya existe.');
            return;
        }

        products.push(newProduct);
        renderTable(products);
        productModal.modal('hide'); // Ocultar el modal después de añadir
        productForm.reset(); // Limpiar el formulario
    }

    // Función para editar un producto
    function editProduct(ref) {
        const product = products.find(p => p.ref === ref);
        if (product) {
            document.getElementById('productRef').value = product.ref;
            document.getElementById('productName').value = product.name;
            document.getElementById('productGenero').value = product.genero;
            document.getElementById('productPrice').value = product.price;
            document.getElementById('productStock').value = product.stock;
            
            editMode = true;
            editProductRef = ref;
            $('#productModal').modal('show');
        }
    }

    // Función para actualizar un producto
    function updateProduct() {
        const updatedProduct = {
            ref: document.getElementById('productRef').value,
            name: document.getElementById('productName').value,
            genero: document.getElementById('productGenero').value,
            price: parseFloat(document.getElementById('productPrice').value),
            stock: parseInt(document.getElementById('productStock').value, 10),
        };

        const index = products.findIndex(p => p.ref === editProductRef);
        if (index !== -1) {
            products[index] = updatedProduct;
            renderTable(products);
            productModal.modal('hide'); // Ocultar el modal después de actualizar
            productForm.reset(); // Limpiar el formulario
            editMode = false;
            editProductRef = null;
        }
    }

    // Función para eliminar un producto
    function deleteProduct(ref) {
        if (confirm('¿Estás seguro de que quieres eliminar este producto?')) {
            const index = products.findIndex(p => p.ref === ref);
            if (index !== -1) {
                products.splice(index, 1);
                renderTable(products);
            }
        }
    }

    // Función para filtrar los productos
    function filterProducts() {
        let filteredProducts = products;

        // Filtrar por búsqueda
        const searchTerm = searchInput.value.toLowerCase();
        if (searchTerm) {
            filteredProducts = filteredProducts.filter(p => 
                p.name.toLowerCase().includes(searchTerm) || 
                p.ref.toLowerCase().includes(searchTerm)
            );
        }

        // Filtrar por género
        const genero = generoFilter.value;
        if (genero) {
            filteredProducts = filteredProducts.filter(p => p.genero.toLowerCase() === genero.toLowerCase());
        }

        // Filtrar por precio
        const price = priceFilter.value;
        if (price) {
            switch (price) {
                case 'low':
                    filteredProducts = filteredProducts.filter(p => p.price < 50000);
                    break;
                case 'medium':
                    filteredProducts = filteredProducts.filter(p => p.price >= 50000 && p.price <= 100000);
                    break;
                case 'high':
                    filteredProducts = filteredProducts.filter(p => p.price > 100000);
                    break;
            }
        }

        renderTable(filteredProducts);
    }

    // Eventos
    searchInput.addEventListener('input', filterProducts);
    generoFilter.addEventListener('change', filterProducts);
    priceFilter.addEventListener('change', filterProducts);

    productForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevenir el comportamiento por defecto del formulario
        if (editMode) {
            updateProduct();
        } else {
            addProduct();
        }
    });

    // Inicializar la tabla con los productos
    renderTable(products);

    window.openProductModal = openProductModal;
    window.editProduct = editProduct;
    window.deleteProduct = deleteProduct;
    // Asegurarse de que la función cerrarSesion esté disponible globalmente
    window.cerrarSesion = cerrarSesion;

    // Añadir event listeners para los enlaces de navegación
    document.addEventListener('DOMContentLoaded', function() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                if (this.getAttribute('href') !== '#') {
                    e.preventDefault();
                    window.location.href = this.getAttribute('href');
                }
            });
        });
    });
});




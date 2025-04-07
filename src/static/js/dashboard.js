// dashboard.js

// Espera a que el documento esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos canvas
    const dailySalesElement = document.getElementById('dailySalesChart');
    const topProductsElement = document.getElementById('topProductsChart');
    
    // Variables para las gráficas
    let dailySalesChart, topProductsChart;
    
    // Crear gráfica de ventas diarias si el elemento existe
    if (dailySalesElement) {
        const ctxDailySales = dailySalesElement.getContext('2d');
        dailySalesChart = new Chart(ctxDailySales, {
            type: 'line', // Tipo de gráfica
            data: {
                labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'], // Etiquetas del eje X
                datasets: [{
                    label: 'Ventas Diarias', // Etiqueta del conjunto de datos
                    data: [120, 150, 170, 90, 130, 180, 210], // Datos de ventas
                    backgroundColor: 'rgba(54, 162, 235, 0.2)', // Color de fondo
                    borderColor: 'rgba(54, 162, 235, 1)', // Color del borde
                    borderWidth: 1 // Grosor del borde
                }]
            },
            options: {
                responsive: true, // Hacer la gráfica responsive
                maintainAspectRatio: false, // No mantener relación de aspecto
                scales: {
                    y: {
                        beginAtZero: true // Comenzar el eje Y en cero
                    }
                }
            }
        });
    } else {
        console.error('Elemento canvas "dailySalesChart" no encontrado');
    }

    // Crear gráfica de productos más vendidos si el elemento existe
    if (topProductsElement) {
        const ctxTopProducts = topProductsElement.getContext('2d');
        topProductsChart = new Chart(ctxTopProducts, {
            type: 'bar', // Tipo de gráfica
            data: {
                labels: ['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E'], // Etiquetas del eje X
                datasets: [{
                    label: 'Productos Más Vendidos', // Etiqueta del conjunto de datos
                    data: [300, 250, 200, 150, 100], // Datos de productos vendidos
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1 // Grosor del borde
                }]
            },
            options: {
                responsive: true, // Hacer la gráfica responsive
                maintainAspectRatio: false, // No mantener relación de aspecto
                scales: {
                    y: {
                        beginAtZero: true // Comenzar el eje Y en cero
                    }
                }
            }
        });
    } else {
        console.error('Elemento canvas "topProductsChart" no encontrado');
    }

    // Función para actualizar los datos de las gráficas
    function updateCharts() {
        // Actualizar gráfica de ventas diarias si existe
        if (dailySalesChart) {
            // Nuevos datos de ventas diarias
            const newDailySalesData = [100, 140, 160, 120, 110, 190, 220];
            dailySalesChart.data.datasets[0].data = newDailySalesData;
            dailySalesChart.update(); // Actualiza la gráfica de ventas diarias
        }

        // Actualizar gráfica de productos más vendidos si existe
        if (topProductsChart) {
            // Nuevos datos de productos más vendidos
            const newTopProductsData = [310, 240, 210, 140, 90];
            topProductsChart.data.datasets[0].data = newTopProductsData;
            topProductsChart.update(); // Actualiza la gráfica de productos más vendidos
        }
    }

    // Ejemplo de actualización de datos cada 10 segundos
    // Puedes comentar esta línea si no quieres la actualización automática
    setInterval(updateCharts, 10000); // Actualiza las gráficas cada 10 segundos

    // Lógica para redirigir al usuario al hacer clic en "Cerrar sesión"
    const logoutButton = document.getElementById('logout');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            // No prevenimos el comportamiento por defecto del enlace
            // ya que parece que estás usando Flask para manejar el logout
            // Si quieres manejarlo con JavaScript, descomenta la siguiente línea:
            // event.preventDefault();
            
            // Aquí puedes agregar lógica adicional para la sesión si es necesario
            console.log('Cerrando sesión...');
        });
    }

    // Ajustar altura de las gráficas para que se vean bien
    function setChartHeights() {
        const chartContainers = document.querySelectorAll('.card-body');
        chartContainers.forEach(container => {
            if (container.querySelector('canvas')) {
                container.style.height = '300px';
            }
        });
    }
    
    // Ajustar alturas inicialmente
    setChartHeights();
    
    // Ajustar alturas al cambiar el tamaño de la ventana
    window.addEventListener('resize', setChartHeights);
});
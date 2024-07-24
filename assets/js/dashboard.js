// dashboard.js

// Espera a que el documento esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Configuración y creación de la gráfica de ventas diarias
    const ctxDailySales = document.getElementById('dailySalesChart').getContext('2d');
    const dailySalesChart = new Chart(ctxDailySales, {
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
            scales: {
                y: {
                    beginAtZero: true // Comenzar el eje Y en cero
                }
            }
        }
    });

    // Configuración y creación de la gráfica de productos más vendidos
    const ctxTopProducts = document.getElementById('topProductsChart').getContext('2d');
    const topProductsChart = new Chart(ctxTopProducts, {
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
            scales: {
                y: {
                    beginAtZero: true // Comenzar el eje Y en cero
                }
            }
        }
    });

    // Función para actualizar los datos de las gráficas (ejemplo)
    function updateCharts() {
        // Nuevos datos de ventas diarias
        const newDailySalesData = [100, 140, 160, 120, 110, 190, 220];
        dailySalesChart.data.datasets[0].data = newDailySalesData;
        dailySalesChart.update(); // Actualiza la gráfica de ventas diarias

        // Nuevos datos de productos más vendidos
        const newTopProductsData = [310, 240, 210, 140, 90];
        topProductsChart.data.datasets[0].data = newTopProductsData;
        topProductsChart.update(); // Actualiza la gráfica de productos más vendidos
    }

    // Ejemplo de actualización de datos cada 10 segundos
    setInterval(updateCharts, 10000); // Actualiza las gráficas cada 10 segundos

    // Lógica para redirigir al usuario al hacer clic en "Cerrar sesión"
    document.getElementById('logout').addEventListener('click', function(event) {
        event.preventDefault(); // Previene el comportamiento por defecto del enlace

        // Aquí puedes agregar lógica adicional para la sesión, como limpiar cookies o tokens
        // Redirige a la página de inicio
        window.location.href = 'login.html';
    });
});

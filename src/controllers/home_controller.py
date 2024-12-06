# src/controllers/home_controller.py
from flask import render_template, flash, redirect, url_for, session as flask_session
from src.controllers.base_controller import FlaskController, route

class HomeController(FlaskController):
    def __init__(self):
        super().__init__()
    
    @route('/', methods=['GET'])
    def index(self):
        """
        Maneja la ruta raíz de la aplicación.
        Si el usuario está autenticado, muestra el dashboard.
        Si no, redirige al login.
        """
        print("HomeController: Accediendo a la ruta '/'")
        
        # Verificar si el usuario está autenticado
        if 'logged_in' in flask_session and flask_session['logged_in']:
            return redirect(url_for('dashboard.index'))  # Corregido aquí
        
        # Si no está autenticado, redirigir al login
        return redirect(url_for('auth.login'))  
    
    @route('/home', methods=['GET'])
    def home(self):
        """
        Ruta para el home de usuarios autenticados
        """
        # Verificar si el usuario está autenticado
        if not flask_session.get('logged_in'):
            flash('Debe iniciar sesión para acceder', 'warning')
            return render_template('login.html')  
        
        return render_template('dashboard.html')
    
    def handle_error(self, error):
        """
        Maneja errores que puedan ocurrir en las rutas
        """
        print(f"Error en HomeController: {str(error)}")
        flash('Ha ocurrido un error inesperado', 'danger')
        return render_template('login.html')  


'''from flask import render_template
from src.controllers.base_controller import FlaskController, route

class HomeController(FlaskController):
    def __init__(self):
        super().__init__()

    @route('/', methods=['GET'])
    def index(self):
        print("HomeController: Accediendo a la ruta '/'")
        return render_template('login.html')'''

# src/controllers/base_controller.py
from flask import Blueprint
from src.models import session

class FlaskController:
    def __init__(self):
        # El nombre del blueprint será el nombre de la clase en minúsculas sin 'Controller'
        self.controller_name = self.__class__.__name__.lower().replace('controller', '')
        self.blueprint = Blueprint(self.controller_name, __name__)
        self._register_routes()

    def _register_routes(self):
        """
        Método que registra las rutas buscando métodos decorados con @route
        """
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, 'route_info'):
                route_info = method.route_info
                endpoint = f"{method_name}"  # Nombre del endpoint será el nombre del método
                self.blueprint.add_url_rule(
                    route_info['path'],
                    endpoint=endpoint,
                    view_func=method,
                    methods=route_info['methods']
                )

    def get_endpoint(self, action):
        """
        Helper para generar nombres de endpoints correctos
        """
        return f"{self.controller_name}.{action}"

def route(path, methods=None):
    """
    Decorador personalizado para registrar rutas en los controladores.
    """
    if methods is None:
        methods = ['GET']

    def decorator(f):
        f.route_info = {
            'path': path,
            'methods': methods
        }
        return f
    return decorator


'''from flask import Blueprint
from src.models import session 

class FlaskController:
    def __init__(self):
        # El nombre del blueprint será el nombre de la clase en minúsculas sin 'Controller'
        controller_name = self.__class__.__name__.lower().replace('controller', '')
        self.blueprint = Blueprint(controller_name, __name__)
        self._register_routes()
    
    def _register_routes(self):
        """
        Método que debe ser implementado por las clases hijas para registrar sus rutas.
        Busca métodos decorados con @route en la clase.
        """
        # Obtener todos los métodos de la clase
        for method_name in dir(self):
            method = getattr(self, method_name)
            # Verificar si el método tiene el atributo 'route_info'
            if hasattr(method, 'route_info'):
                route_info = method.route_info
                self.blueprint.route(
                    route_info['path'],
                    methods=route_info['methods']
                )(method)

def route(path, methods=None):
    """
    Decorador personalizado para registrar rutas en los controladores.
    """
    if methods is None:
        methods = ['GET']
    
    def decorator(f):
        f.route_info = {
            'path': path,
            'methods': methods
        }
        return f
    return decorator'''
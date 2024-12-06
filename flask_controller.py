# flask_controller.py
import importlib
import inspect
import os
from src.controllers.base_controller import FlaskController


class FlaskControllerRegister:
    def __init__(self, app):
        self.app = app

    def register_package(self, package_path):
        """
        Registra automáticamente todos los controladores en un paquete.
        """
        # Obtener la ruta base del proyecto
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Convertir el path del paquete a path del sistema de archivos
        package_dir = os.path.join(base_path, *package_path.split('.'))

        # Verificar si el directorio existe
        if not os.path.exists(package_dir):
            raise DirectoryNotFoundError(f"Directory not found: {package_dir}")

        # Recorrer todos los archivos en el directorio
        for filename in os.listdir(package_dir):
            if filename.endswith('_controller.py'):
                # Convertir el nombre del archivo a formato de módulo
                module_name = f"{package_path}.{filename[:-3]}"

                try:
                    # Importar el módulo
                    module = importlib.import_module(module_name)

                    # Buscar todas las clases en el módulo
                    for name, obj in inspect.getmembers(module):
                        # Verificar si es una clase que hereda de FlaskController
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, FlaskController)
                            and obj != FlaskController
                        ):
                            # Crear una instancia del controlador
                            controller = obj()

                            # Determinar el prefijo para el controlador
                            if name == "HomeController":
                                controller.blueprint.url_prefix = "/"  # Sin prefijo
                            else:
                                controller.blueprint.url_prefix = f"/{name.lower().replace('controller', '')}"
                                
                            # Registrar el blueprint
                            self.app.register_blueprint(controller.blueprint)
                            print(f"Registered controller: {name} at {controller.blueprint.url_prefix}")
                            
                except Exception as e:
                    print(f"Error al importar módulo {module_name}: {str(e)}")

    def get_url_prefix(self, controller_name):
        """
        Obtiene el prefijo de URL para un controlador específico.
        """
        if controller_name == "HomeController":
            return "/"  # Prefijo vacío para HomeController
        return f"/{controller_name.lower().replace('controller', '')}"

    def register_blueprint(self, module_name, controller, name, url_prefix):
        """
        Registra un blueprint para un controlador específico.
        """
        try:
            self.app.register_blueprint(controller.blueprint, url_prefix=url_prefix)
            print(f"Registered controller: {name} at {url_prefix}")
        except Exception as e:
            print(f"Error al registrar controlador {module_name}: {str(e)}")


class DirectoryNotFoundError(Exception):
    pass

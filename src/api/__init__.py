#src/api/__init__.py
from src.extensions import api
from src.api.resources.auth_resource import LoginResource
from src.api.resources.clientes_resource import ClienteListResource, ClienteResource
#from src.api.resources.productos_resource import ProductoListResource, ProductoResource
# Importa otros recursos...

def init_app(app):
    """
    Inicializa la API RESTful con todos los recursos
    """
    # Registrar recursos
    from src.api.resources.auth_resource import LoginResource
    from src.api.resources.clientes_resource import ClienteListResource, ClienteResource
    # Otras importaciones...
    
    # Registra los endpoints
    print("Registrando endpoint LoginResource en /api/login")
    api.add_resource(LoginResource, '/api/login')
    api.add_resource(ClienteListResource, '/api/clientes')
    api.add_resource(ClienteResource, '/api/clientes/<int:cliente_id>')
    # Otros endpoints...
    
    # Verifica las rutas registradas de manera más precisa
    print("API RESTful inicializada. Verificando rutas /api/*:")
    api_routes = []
    for rule in app.url_map.iter_rules():
        if '/api/' in rule.rule:
            api_routes.append(f"{rule.endpoint}: {rule.rule} ({', '.join(rule.methods)})")
    
    # Ordenar para facilitar la lectura
    api_routes.sort()
    for route in api_routes:
        print(route)
    
    # Mejor verificación: busca cualquier ruta que CONTENGA /api/login
    login_route_found = False
    for rule in app.url_map.iter_rules():
        if '/api/login' in rule.rule:
            login_route_found = True
            print(f"Ruta de login encontrada: {rule.rule} con métodos {rule.methods}")
    
    if not login_route_found:
        print("¡ADVERTENCIA! La ruta /api/login NO está registrada correctamente.")
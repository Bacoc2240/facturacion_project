from flask import Flask, request, session as flask_session
from flask_controller import FlaskControllerRegister
from flask_cors import CORS
from src.models.usuario import Usuario
from src.models import engine, Base
from flask_mail import Mail
from datetime import timedelta
import os
from dotenv import load_dotenv
# Importar todos los modelos para asegurar que se registren
from src.models.auditoria import Auditoria
from src.models.categorias import Categorias
from src.models.detalle_factura import DetalleFactura
from src.models.metodo_de_pago import MetodoDePago
from src.models.promocion import Promocion
from src.models.resolucion_dian import ResolucionDIAN
from src.models.nota_credito import NotaCredito, DetalleNotaCredito
from src.models.nota_debito import NotaDebito, DetalleNotaDebito
from src.extensions import init_app

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de CORS 
def configure_cors(app):
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:8100"],  # Ajusta según la URL de tu app Ionic
            "supports_credentials": True,  # Crucial para permitir cookies
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    return app


# Configuración de la sesión
app.secret_key = 'xv4j^3#iYq7!t5Kw8gZQZ3o!1m_&_J5r'
app.config['SESSION_TYPE'] = 'filesystem'  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = False  # En desarrollo
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_USE_SIGNER'] = True 

# Configuración del email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Configuración de la URL base para desarrollo
app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5000')

# Configuración para archivos adjuntos
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')

# Configuración para JWT
app.config['JWT_SECRET_KEY'] = app.secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Inicializar extensiones (incluirá Mail, API, CORS, etc.)
init_app(app)

# Crear todas las tablas al iniciar la aplicación
with app.app_context():
    Base.metadata.create_all(bind=engine)
    
# Registrar controladores automáticamente
register = FlaskControllerRegister(app)
register.register_package('src.controllers')

# Inicializar API si existe el módulo
from src.api import init_app as init_api
init_api(app)
print("API RESTful inicializada correctamente")

print("\nTodas las rutas registradas:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")

#procesador de contexto
@app.context_processor
def utility_processor():
    def has_permission(permission):
        if 'user_id' in flask_session:
            user_id = flask_session.get('user_id')
            with engine.connect() as connection:
                result = connection.execute(
                    f"SELECT * FROM usuario WHERE id = {user_id}"
                ).fetchone()
                if result:
                    user = Usuario(**dict(result))
                    return user.has_permission(permission)
        return False

    return dict(has_permission=has_permission)

@app.route('/api/login-test', methods=['POST', 'OPTIONS'])
def login_test():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
        
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Búsqueda en la BD - Esto es lo que necesitas activar
    from src.models.usuario import Usuario
    from src.models import session
    from src.password_utils import verify_password
    
    user = session.query(Usuario).filter_by(nombre_usuario=username).first()
    
    if user and user.check_password(password):
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=user.id_usuario)
        print(f"Login exitoso para usuario: {username}")
        return {'access_token': access_token}, 200
    
    print(f"Credenciales inválidas para: {username}")
    return {'message': 'Credenciales inválidas'}, 401

# 3. Añade este middleware
@app.after_request
def after_request(response):
    # Obtener el origen de la solicitud
    origin = request.headers.get('Origin')
    allowed_origins = ["http://localhost:8100", "http://localhost:4200", "capacitor://localhost"]
    
    # Si el origen está en la lista de permitidos, usarlo
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        
        # Siempre incluir estos encabezados
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
        
        # Asegurar código 200 para solicitudes OPTIONS
        if request.method == 'OPTIONS':
            response.status_code = 200
            
    return response

#Verificación de posibles conflictos en la ruta
print("\nVerificando posibles conflictos de rutas:")
for rule in app.url_map.iter_rules():
    if '/api/login' in rule.rule:
        print(f"Ruta: {rule.rule}, Métodos: {rule.methods}, Endpoint: {rule.endpoint}")
        
print("\nVerificando si la ruta /api/login está registrada:")
login_route_found = False
for rule in app.url_map.iter_rules():
    if '/api/login' in rule.rule:
        login_route_found = True
        print(f"¡Ruta encontrada!: {rule.rule}, Métodos: {rule.methods}")
if not login_route_found:
    print("¡ALERTA! La ruta /api/login NO está registrada")

# Punto de entrada principal
if __name__ == '__main__':
    try:
        print("Iniciando aplicación Flask...")
        app.run(debug=True)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
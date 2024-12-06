from flask import Flask, session as flask_session
from flask_controller import FlaskControllerRegister
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

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

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



# Inicializar Mail
mail = Mail()
mail.init_app(app)

# Crear todas las tablas al iniciar la aplicación
with app.app_context():
    Base.metadata.create_all(bind=engine)
    
# Registrar controladores automáticamente
register = FlaskControllerRegister(app)
register.register_package('src.controllers')

print("\nTodas las rutas registradas:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")

#print(app.url_map)

# Tu procesador de contexto existente...
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

# Punto de entrada principal
if __name__ == '__main__':
    try:
        print("Iniciando aplicación Flask...")
        app.run(debug=True)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")



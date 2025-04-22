from flask_mail import Mail
from flask_restful import Api
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

# Inicialización de las extensiones
mail = Mail()
api = Api()
cors = CORS()
ma = Marshmallow()
jwt = JWTManager()

def init_app(app):
    """Inicializa todas las extensiones con la aplicación Flask"""
    mail.init_app(app)
    api.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
# src/api/resources/auth_resource.py
from flask_restful import Resource
from flask import request, make_response, current_app
from flask_jwt_extended import create_access_token
from src.models.usuario import Usuario
from src.models import session
import json

class LoginResource(Resource):
    def options(self):
        # Manejar la solicitud OPTIONS de preflight explícitamente
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:8100")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Max-Age", "86400")
        return response
        
    def post(self):
        current_app.logger.info("LoginResource.post() llamado")
        print(f"LoginResource.post() llamado, datos: {request.get_json()}")
        
        try:
            data = request.get_json()
            if not data:
                return {"message": "No se recibieron datos JSON"}, 400
                
            username = data.get('username')
            password = data.get('password')
            
            print(f"Intento de login para: {username}")
            
            if not username or not password:
                return {"message": "Se requieren nombre de usuario y contraseña"}, 400
            
            # Para desarrollo/depuración
            if username == 'admin' and password == 'admin':
                access_token = create_access_token(identity='admin')
                print(f"Login exitoso para usuario admin (test)")
                return {'access_token': access_token}, 200
            
            # Búsqueda en la BD
            user = session.query(Usuario).filter_by(nombre_usuario=username).first()
            
            if user and user.check_password(password):
                access_token = create_access_token(identity=user.id)
                print(f"Login exitoso para usuario: {username}")
                return {'access_token': access_token}, 200
            
            print(f"Credenciales inválidas para: {username}")
            return {'message': 'Credenciales inválidas'}, 401
            
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return {'message': f'Error del servidor: {str(e)}'}, 500
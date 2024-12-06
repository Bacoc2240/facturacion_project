from functools import wraps
from flask import redirect, url_for, session as flask_session, jsonify
from src.models import session  # Usar la sesión global
from src.models.usuario import Usuario

# Definición de roles y permisos
ROLES = {
    'admin': ['read', 'write', 'delete', 'suspend'],
    'vendedor': ['read', 'write'],
    'inventario': ['read', 'write', 'suspend'],
    'visualizador': ['read']
}

def check_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in flask_session:
                return jsonify({'error': 'No autorizado'}), 401
            
            user_role = flask_session['user_role']
            if user_role not in ROLES or permission not in ROLES[user_role]:
                return jsonify({'error': 'Permiso denegado'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Verificando estado de sesión...")
        print("Contenido actual de la sesión:", dict(flask_session))
        
        if 'logged_in' not in flask_session or not flask_session['logged_in']:
            print("Usuario no autenticado, redirigiendo a login")
            return redirect(url_for('auth.login'))
            
        print("Usuario autenticado, permitiendo acceso")
        return f(*args, **kwargs)
    return decorated_function

'''def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_session.get('logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function'''

def render_if_has_permission(permission):
    """ 
    Helper function para verificar permisos en templates. 
    Usar en templates Jinja2. 
    """
    def wrapper(func):
        def wrapped(*args, **kwargs):
            if 'user_role' in flask_session:
                user = session.query(Usuario).get(flask_session['user_id'])
                if user and user.has_permission(permission):
                    return func(*args, **kwargs)
            return ''
        return wrapped
    return wrapper

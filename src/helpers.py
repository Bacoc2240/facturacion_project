from flask import session
from src.models.usuario import Usuario

# Helper Function
def render_if_has_permission(permission):
    """Helper function para verificar permisos en templates."""
    def wrapper(func):
        def wrapped(*args, **kwargs):
            if 'user_role' in session:
                user = Usuario.query.get(session['user_id'])
                if user and user.has_permission(permission):
                    return func(*args, **kwargs)
            return ''
        return wrapped
    return wrapper

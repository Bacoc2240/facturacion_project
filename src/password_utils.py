# password_utils.py
import bcrypt
import re

def hash_password(password: str) -> str:
    """
    Hashea una contraseña utilizando bcrypt.
    
    Args:
        password (str): Contraseña en texto plano
    
    Returns:
        str: Contraseña hasheada
    """
    # Convertir a bytes y generar salt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña proporcionada coincide con el hash.
    
    Args:
        plain_password (str): Contraseña en texto plano
        hashed_password (str): Contraseña hasheada
    
    Returns:
        bool: True si la contraseña es correcta, False en caso contrario
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def validar_contraseña(password: str) -> bool:
    """
    Valida que la contraseña cumpla con ciertos criterios de seguridad:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    
    Args:
        password (str): Contraseña a validar
    
    Returns:
        bool: True si cumple todos los criterios, False en caso contrario
    """
    # Criterios de seguridad
    if len(password) < 8:
        return False
    
    # Verificar presencia de:
    # - Al menos una mayúscula
    # - Al menos una minúscula  
    # - Al menos un número
    # - Al menos un carácter especial
    if not (
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    ):
        return False
    
    return True
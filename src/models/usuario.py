from sqlalchemy import Column, LargeBinary, Integer, String, ForeignKey, Boolean, DateTime, Enum
from src.models import Base, session  
from sqlalchemy.orm import relationship
from src.models.empleado import Empleado
from datetime import datetime, timezone
from src.password_utils import hash_password, validar_contraseña
import bcrypt
import enum
from datetime import datetime, timezone, timedelta
from flask import current_app
from flask_mail import Message
from src.extensions import mail 

# Definición de roles como Enum
class RolUsuario(enum.Enum):
    ADMIN = 'admin'
    VENDEDOR = 'vendedor'
    INVENTARIO = 'inventario'
    VISUALIZADOR = 'visualizador'

def get_utc_now():
    """Retorna el timestamp actual en UTC."""
    return datetime.now(timezone.utc)

class Usuario(Base):
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    contraseña = Column(LargeBinary, nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    intentos_fallidos = Column(Integer, default=0)
    habilitado = Column(Boolean, default=True)
    causa_suspension = Column(String(255))
    id_empleado = Column(Integer, ForeignKey('empleado.id_empleado'), nullable=False)
    ultima_sesion = Column(DateTime)
    fecha_creacion = Column(DateTime)
    primer_ingreso = Column(Boolean, default=True)

    empleado = relationship('Empleado', back_populates='usuario')

    def __init__(self, nombre_usuario, contraseña, rol, id_empleado):
        self.nombre_usuario = nombre_usuario
        self.set_password(contraseña)
        self.rol = rol
        self.id_empleado = id_empleado
        self.fecha_creacion = get_utc_now()

    def set_password(self, contraseña):
        """
        Establece la contraseña hasheada del usuario.
        
        Args:
            contraseña (str): La contraseña en texto plano
        """
        try:
            # Convertimos la contraseña a bytes si es necesario
            if isinstance(contraseña, str):
                contraseña = contraseña.encode('utf-8')
            
            # Generamos el hash y lo guardamos directamente como bytes
            self.contraseña = bcrypt.hashpw(contraseña, bcrypt.gensalt())
            
            # No necesitamos hacer session.add(self) aquí porque el objeto ya está siendo rastreado
            session.commit()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Error al establecer la contraseña: {e}")

    def check_password(self, contraseña):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.
        
        Args:
            contraseña (str): La contraseña en texto plano a verificar
            
        Returns:
            bool: True si la contraseña coincide, False en caso contrario
        """
        try:
            # Convertimos la contraseña a bytes si es necesario
            if isinstance(contraseña, str):
                contraseña = contraseña.encode('utf-8')
            
            # Asegurarnos de que el hash almacenado esté en el formato correcto
            stored_hash = self.contraseña
            
            # Si el hash está almacenado como string (por datos legacy), lo convertimos
            if isinstance(stored_hash, str):
                try:
                    stored_hash = stored_hash.encode('utf-8')
                except UnicodeEncodeError:
                    print("Error: Hash almacenado en formato incorrecto")
                    return False
            
            # Verificamos que tengamos un hash válido
            if not stored_hash or len(stored_hash) < 50:  # Los hashes bcrypt tienen una longitud mínima
                print("Error: Hash almacenado inválido o corrupto")
                return False
                
            return bcrypt.checkpw(contraseña, stored_hash)
            
        except Exception as e:
            print(f"Error en check_password: {e}")
            print(f"Tipo de contraseña: {type(contraseña)}")
            print(f"Tipo de hash almacenado: {type(stored_hash)}")
            return False

    def actualizar_ultima_sesion(self):
        """Actualiza el timestamp de última sesión."""
        self.ultima_sesion = get_utc_now()
        session.commit()

    def has_permission(self, permission):
        """Verifica si el usuario tiene un permiso específico."""
        ROLES_PERMISOS = {
            RolUsuario.ADMIN: ['read', 'write', 'delete', 'suspend'],
            RolUsuario.VENDEDOR: ['read', 'write'],
            RolUsuario.INVENTARIO: ['read', 'write', 'suspend'],
            RolUsuario.VISUALIZADOR: ['read']
        }
        return permission in ROLES_PERMISOS.get(self.rol, [])

    def get_permissions(self):
        """Obtiene todos los permisos del usuario según su rol."""
        ROLES_PERMISOS = {
            RolUsuario.ADMIN: ['read', 'write', 'delete', 'suspend'],
            RolUsuario.VENDEDOR: ['read', 'write'],
            RolUsuario.INVENTARIO: ['read', 'write', 'suspend'],
            RolUsuario.VISUALIZADOR: ['read']
        }
        return ROLES_PERMISOS.get(self.rol, [])

    def suspender_usuario(self, causa):
        """Método para suspender a un usuario."""
        self.habilitado = False
        self.causa_suspension = causa
        session.commit()

    def habilitar_usuario(self):
        """Método para reactivar la cuenta de un usuario suspendido."""
        self.habilitado = True
        self.causa_suspension = None
        self.intentos_fallidos = 0
        session.commit()

    @classmethod
    def crear_usuario(cls, nombre_usuario, contraseña, rol, id_empleado, creador=None):
        """
        Método estático para crear un nuevo usuario.
        
        Args:
            nombre_usuario (str): Nombre de usuario único
            contraseña (str): Contraseña en texto plano
            rol (RolUsuario): Rol del usuario
            id_empleado (int): ID del empleado asociado
            creador (Usuario, optional): Usuario que está creando este nuevo usuario
        """
        try:
            print(f"Creando usuario - nombre: {nombre_usuario}, rol: {rol}, id_empleado: {id_empleado}")
            
            # Validar la contraseña
            if not validar_contraseña(contraseña):
                raise ValueError("La contraseña no cumple con los requisitos de seguridad")
            
            # Crear instancia del usuario pero SIN hashear la contraseña todavía
            nuevo_usuario = cls(
                nombre_usuario=nombre_usuario,
                contraseña='temporal',  # Será reemplazado inmediatamente
                rol=rol,
                id_empleado=id_empleado
            )
            
            # Ahora establecemos la contraseña correctamente usando el método set_password
            nuevo_usuario.set_password(contraseña)
            
            # El resto del código permanece igual...
            
            return nuevo_usuario
            
        except Exception as e:
            session.rollback()
            raise ValueError(f"Error creando usuario: {e}")
        
    def to_dict(self):
        """Convierte el usuario a un diccionario para API/JSON."""
        return {
            'id': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'rol': self.rol.value,
            'habilitado': self.habilitado,
            'ultima_sesion': self.ultima_sesion.isoformat() if self.ultima_sesion else None,
            'fecha_creacion': self.fecha_creacion.isoformat(),
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia de Usuario desde un diccionario."""
        return cls(
            nombre_usuario=data['nombre_usuario'],
            contraseña=data['contraseña'],
            rol=RolUsuario(data['rol']),
            id_empleado=data['id_empleado']
        )
    
    def generar_token_actualizacion(self):
        """Genera un token para actualización de credenciales."""
        token = bcrypt.hashpw(str(datetime.now(timezone.utc)).encode(), bcrypt.gensalt()).decode()
        self.token_actualizacion = token
        self.token_expiracion = datetime.now(timezone.utc) + timedelta(hours=24)
        session.commit()
        return token

    def verificar_token_actualizacion(self, token):
        """Verifica si el token de actualización es válido."""
        return (
            self.token_actualizacion == token and 
            self.token_expiracion and 
            self.token_expiracion > datetime.now(timezone.utc)
        )

    def limpiar_token_actualizacion(self):
        """Limpia los campos de token después de la actualización."""
        self.token_actualizacion = None
        self.token_expiracion = None
        self.primer_ingreso = False
        session.commit()

    def enviar_email_actualizacion(self):
        """Envía email con token de actualización."""
        try:
            token = self.generar_token_actualizacion()
            mensaje = Message(
                'Actualización de Credenciales Requerida',
                recipients=[self.empleado.email]
            )
            mensaje.body = f'''
            Se requiere actualizar sus credenciales de acceso al sistema.
            
            Por favor, siga este enlace para actualizar sus datos:
            {current_app.config['BASE_URL']}/auth/actualizar_credenciales/{token}
            
            Este enlace expirará en 24 horas.
            Si no solicitó esta actualización, contacte al administrador del sistema.
            '''
            mail.send(mensaje)
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

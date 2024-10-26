from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from src.models import Base, session
from sqlalchemy.orm import relationship
from src.models.empleado import Empleado
from datetime import datetime, timezone, timedelta
import bcrypt
import enum

# Definición de roles como Enum
class RolUsuario(enum.Enum):
    ADMIN = 'admin'
    VENDEDOR = 'vendedor'
    INVENTARIO = 'inventario'
    VISUALIZADOR = 'visualizador'

# Función helper para obtener el timestamp actual en UTC
def get_utc_now():
    """Retorna el timestamp actual en UTC."""
    return datetime.now(timezone.utc)

class Usuario(Base):
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(255), nullable=False, unique=True)
    contraseña = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    intentos_fallidos = Column(Integer, default=0)
    habilitado = Column(Boolean, default=True)
    causa_suspension = Column(String(255))
    id_empleado = Column(Integer, ForeignKey('empleado.id_empleado'), nullable=False)
    ultima_sesion = Column(DateTime(timezone=True))
    fecha_creacion = Column(DateTime(timezone=True), default=get_utc_now)

    empleado = relationship('Empleado', back_populates='usuario')

    def __init__(self, nombre_usuario, contraseña, rol, id_empleado):
        self.nombre_usuario = nombre_usuario
        self.set_password(contraseña)
        self.rol = rol
        self.id_empleado = id_empleado
        self.fecha_creacion = get_utc_now()

    def set_password(self, contraseña):
        """Establece la contraseña hasheada del usuario."""
        salt = bcrypt.gensalt()
        self.contraseña = bcrypt.hashpw(contraseña.encode('utf-8'), salt)

    def check_password(self, contraseña):
        """Verifica si la contraseña proporcionada es correcta."""
        try:
            return bcrypt.checkpw(contraseña.encode('utf-8'), self.contraseña.encode('utf-8'))
        except Exception:
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

    @staticmethod
    def crear_usuario(nombre_usuario, contraseña, rol, id_empleado, creador):
        """Método estático para crear un nuevo usuario."""
        if creador.rol != RolUsuario.ADMIN:
            raise PermissionError("Solo un administrador puede crear usuarios.")
        
        usuario_existente = session.query(Usuario).filter_by(
            nombre_usuario=nombre_usuario
        ).first()
        
        if usuario_existente:
            raise ValueError("El usuario ya existe.")

        nuevo_usuario = Usuario(nombre_usuario, contraseña, rol, id_empleado)
        session.add(nuevo_usuario)
        session.commit()
        return nuevo_usuario

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
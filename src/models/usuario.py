from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from src.models import Base, session
from sqlalchemy.orm import relationship
from src.models.empleado import Empleado
from datetime import datetime, timedelta
import bcrypt  # Para hashear la contraseña
import smtplib  # Para enviar correos electrónicos
from email.mime.text import MIMEText

class Usuario(Base):
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(255), nullable=False, unique=True)  # Documento de identidad o correo electrónico
    contraseña = Column(String(255), nullable=False)  # Hasheada con bcrypt
    rol = Column(String(30), nullable=False)  # E.g., 'Administrador', 'Empleado', etc.
    intentos_fallidos = Column(Integer, default=0)  # Número de intentos fallidos
    habilitado = Column(Boolean, default=True)  # Si el usuario está habilitado o suspendido
    causa_suspension = Column(String(255))  # Razón de la suspensión, si aplica
    id_empleado = Column(Integer, ForeignKey('empleado.id_empleado'), nullable=False)

    empleado = relationship('Empleado', back_populates='usuario')

    def __init__(self, nombre_usuario, contraseña, rol, id_empleado):
        self.nombre_usuario = nombre_usuario
        self.contraseña = self.generar_hash_contraseña(contraseña)
        self.rol = rol
        self.id_empleado = id_empleadobcrypt

    @staticmethod
    def generar_hash_contraseña(contraseña):
        """Genera un hash para la contraseña utilizando bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(contraseña.encode('utf-8'), salt)

    def verificar_contraseña(self, contraseña):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        return bcrypt.checkpw(contraseña.encode('utf-8'), self.Contraseña)

    def autenticar(self, contraseña):
        """Método para autenticar usuarios."""
        if not self.habilitado:
            raise ValueError("El usuario está suspendido. Razón: {}".format(self.causa_suspension))
        
        if self.intentos_fallidos >= 3:
            raise ValueError("Cuenta bloqueada debido a múltiples intentos fallidos.")
        
        if self.verificar_contraseña(contraseña):
            self.intentos_fallidos = 0  # Reiniciar intentos fallidos en caso de éxito
            return True
        else:
            self.intentos_fallidos += 1
            if self.intentos_fallidos >= 3:
                raise ValueError("Cuenta bloqueada después de 3 intentos fallidos.")
            return False

    def suspender_usuario(self, causa):
        """Método para suspender a un usuario, solo puede ser ejecutado por un administrador."""
        self.habilitado = False
        self.causa_suspension = causa

    def habilitar_usuario(self):
        """Método para reactivar la cuenta de un usuario suspendido."""
        self.habilitado = True
        self.causa_suspension = None
        self.intentos_fallidos = 0

    @staticmethod
    def crear_usuario(nombre_usuario, contraseña, rol, id_empleado, creador):
        """Método estático para crear un nuevo usuario. Solo el administrador puede hacerlo."""
        if creador.Rol != 'Administrador':
            raise PermissionError("Solo un administrador puede crear usuarios.")
        
        # Verificar si el usuario ya existe
        usuario_existente = session.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first()
        if usuario_existente:
            raise ValueError("El usuario ya existe.")

        nuevo_usuario = Usuario(nombre_usuario, contraseña, rol, id_empleado)
        session.add(nuevo_usuario)
        session.commit()
        return nuevo_usuario

    def enviar_recuperacion_contrasena(self, correo_destino):
        """Método para enviar un enlace de recuperación de contraseña al correo electrónico registrado."""
        if not self.Habilitado:
            raise ValueError("No se puede recuperar la contraseña de un usuario suspendido.")
        
        # Generar un enlace de recuperación (en un caso real, debe ser un enlace único y seguro)
        link_recuperacion = "http://mi_sistema.com/recuperar_contrasena/{}".format(self.ID_Usuario)
        
        # Configuración del correo electrónico
        mensaje = MIMEText(f"Haz clic en el siguiente enlace para recuperar tu contraseña: {link_recuperacion}")
        mensaje['Subject'] = "Recuperación de contraseña"
        mensaje['From'] = "admin@mi_sistema.com"
        mensaje['To'] = correo_destino

        # Enviar correo
        try:
            servidor_smtp = smtplib.SMTP('smtp.mi_sistema.com', 587)
            servidor_smtp.starttls()
            servidor_smtp.login('admin@mi_sistema.com', 'mi_contraseña')
            servidor_smtp.send_message(mensaje)
            servidor_smtp.quit()
            print("Correo de recuperación enviado.")
        except Exception as e:
            print(f"Error al enviar el correo: {str(e)}")

    def verificar_habilitacion(self):
        """Verifica si el usuario está habilitado en el sistema."""
        return self.Habilitado

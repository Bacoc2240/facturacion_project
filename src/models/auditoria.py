from sqlalchemy import Column, Integer, String, Text, DateTime, func
from src.models import Base, session  # Usar la sesión global

class Auditoria(Base):
    __tablename__ = 'auditoria'
    
    id = Column(Integer, primary_key=True)
    tabla = Column(String(50), nullable=False)
    accion = Column(String(50), nullable=False)
    registro_id = Column(Integer, nullable=False)
    usuario_id = Column(Integer, nullable=False)
    detalles = Column(Text)
    fecha_hora = Column(DateTime, default=func.current_timestamp())

    def __init__(self, tabla, accion, registro_id, usuario_id, detalles=None):
        self.tabla = tabla
        self.accion = accion
        self.registro_id = registro_id
        self.usuario_id = usuario_id
        self.detalles = detalles

    @classmethod
    def crear_auditoria(cls, tabla, accion, registro_id, usuario_id, detalles=None):
        nueva_auditoria = cls(tabla, accion, registro_id, usuario_id, detalles)
        session.add(nueva_auditoria)
        session.commit()
        return nueva_auditoria

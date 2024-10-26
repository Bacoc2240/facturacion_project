from sqlalchemy import Column, Integer, String, Text, DateTime, func
from src.models import session, Base

class Auditoria(Base):
    __tablename__ = 'auditoria'
    
    id = Column(Integer, primary_key=True)
    tabla = Column(String(50), nullable=False)
    accion = Column(String(50), nullable=False)
    registro_id = Column(Integer, nullable=False)
    usuario_id = Column(Integer, nullable=False)
    detalles = Column(Text)
    fecha_hora = Column(DateTime, default=func.current_timestamp())

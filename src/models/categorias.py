from sqlalchemy import Column, Integer, String, Float, ForeignKey
from src.models import Base, session  # Usar la sesión global

class Categorias(Base):
    __tablename__ = "categorias"    
    id = Column(Integer, primary_key=True)
    categoria = Column(String(300), unique=True, nullable=False)

    def __init__(self, categoria):
        self.categoria = categoria
        
    @staticmethod
    def obtener_categorias():
        return session.query(Categorias).all()  # Usando la sesión global

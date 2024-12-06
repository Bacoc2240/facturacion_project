from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from src.models import Base, session

class MetodoDePago(Base):
    __tablename__ = 'metodo_de_pago'

    id_metodo_pago = Column(Integer, primary_key=True)
    nombre_metodo = Column(String(55), nullable=False)
    descripcion = Column(Text)

    # Relación con la tabla intermedia 'factura_metodo_de_pago'
    factura = relationship('Factura', secondary='factura_metodo_de_pago', back_populates='metodos_pago')

    # Constructor
    def __init__(self, nombre_metodo, descripcion=None):
        self.nombre_metodo = nombre_metodo
        self.descripcion = descripcion

    # Método para obtener todos los métodos de pago disponibles
    @staticmethod
    def obtener_metodos_disponibles():
        return session.query(MetodoDePago).all()

# Clase intermedia para la relación Many-to-Many entre Factura y MetodoDePago
from sqlalchemy import Table, ForeignKey

factura_metodo_de_pago = Table(
    'factura_metodo_de_pago', Base.metadata,
    Column('id', Integer, ForeignKey('factura.id')),
    Column('id_metodo_pago', Integer, ForeignKey('metodo_de_pago.id_metodo_pago'))
)

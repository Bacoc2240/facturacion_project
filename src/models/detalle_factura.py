from sqlalchemy import Column, Integer, String, Float, ForeignKey
from src.models import session, Base
from src.models.productos import Productos
from src.models.factura import Factura

class DetalleFactura(Base):
    __tablename__ = 'detalle_factura'

    id = Column(Integer, primary_key=True)
    precio_unitario = Column(Float(10, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    subtotal = Column(Float(10, 2), nullable=False)
    id_factura = Column(Integer, ForeignKey('factura.id'), nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id'), nullable=False)

     
    # Constructor del modelo
    def __init__(self, precio_unitario, cantidad, id_factura, id_producto):
        self.precio_unitario = precio_unitario
        self.cantidad = cantidad
        self.subtotal = precio_unitario * cantidad
        self.id_factura = id_factura
        self.id_producto = id_producto
        
    # Método para actualizar el subtotal
    def calcular_subtotal(self):
        self.subtotal = self.precio_unitario * self.cantidad
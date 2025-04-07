from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from src.models import Base, session
from src.models.productos import Productos

class DetalleFactura(Base):
    __tablename__ = 'detalle_factura'
    
    id = Column(Integer, primary_key=True)
    precio_unitario = Column(Float(10, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    subtotal = Column(Float(10, 2), nullable=False)
    porcentaje_iva = Column(Numeric(5, 2), default=19.00)  # Nueva columna
    id_factura = Column(Integer, ForeignKey('factura.id'), nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id'), nullable=False)
    
    # Relaciones
    producto = relationship('Productos', backref='detalles_factura')
    factura = relationship('Factura', back_populates='detalles')
    
    # Constructor actualizado para incluir el porcentaje de IVA
    def __init__(self, precio_unitario, cantidad, id_factura, id_producto, porcentaje_iva=19.00):
        self.precio_unitario = precio_unitario
        self.cantidad = cantidad
        self.subtotal = precio_unitario * cantidad
        self.id_factura = id_factura
        self.id_producto = id_producto
        self.porcentaje_iva = porcentaje_iva
    
    # Método para actualizar el subtotal
    def calcular_subtotal(self):
        self.subtotal = self.precio_unitario * self.cantidad
    
    # Método para calcular el IVA
    def calcular_iva(self):
        """Calcula el monto de IVA para este ítem basado en su porcentaje específico"""
        return self.subtotal * (self.porcentaje_iva / 100)
    
    # Guardar en la base de datos usando la sesión global
    def guardar(self):
        """
        Agrega este detalle a la sesión actual sin hacer commit
        para mantener la integridad de la transacción
        """
        session.add(self)
        session.flush()  # Flush asigna ID y ejecuta SQL sin confirmar la transacción
        return self  # Devolver self permite encadenar operaciones
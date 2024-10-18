from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from src.models import Base, session
from sqlalchemy.orm import relationship
from src.models.factura import Factura

class Transaccion(Base):
    __tablename__ = 'transaccion'

    ID_Transaccion = Column(Integer, primary_key=True, autoincrement=True)
    Fecha = Column(Date, nullable=False)
    Tipo = Column(String(45), nullable=False)  # E.g., "Pago", "Devolución", etc.
    Monto = Column(Numeric(10, 2), nullable=False)
    ID_Factura = Column(Integer, ForeignKey('factura.id'), nullable=False)

    # Relación con Factura
    factura = relationship('Factura', back_populates='transacciones')

    def __init__(self, fecha, tipo, monto, id):
        self.Fecha = fecha
        self.Tipo = tipo
        self.Monto = monto

        # Verificar si la factura asociada existe
        factura = session.query(Factura).filter_by(id_factura=id).first()
        if factura:
            self.ID_Factura = id
        else:
            raise ValueError("La factura asociada no existe.")

    # Método para asociar la transacción a una factura
    def asociar_a_factura(self, factura):
        if isinstance(factura, Factura):
            self.ID_Factura = factura.id
        else:
            raise ValueError("El objeto proporcionado no es una instancia de Factura.")

    # Método para obtener información detallada de la transacción
    def obtener_informacion(self):
        return {
            'ID_Transaccion': self.ID_Transaccion,
            'Fecha': self.Fecha,
            'Tipo': self.Tipo,
            'Monto': str(self.Monto),
            'ID_Factura': self.ID_Factura
        }

    # Método para actualizar el monto de la transacción
    def actualizar_monto(self, nuevo_monto):
        if nuevo_monto > 0:
            self.Monto = nuevo_monto
        else:
            raise ValueError("El monto debe ser mayor a cero.")

    # Método para verificar si una transacción está asociada a una factura
    def verificar_asociacion_factura(self):
        if self.ID_Factura:
            return True
        return False

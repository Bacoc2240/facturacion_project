from sqlalchemy import Column, Integer, String, Text, Date, Numeric
from src.models import Base, session
from sqlalchemy.orm import relationship
from datetime import datetime

class Promocion(Base):
    __tablename__ = 'promocion'

    id_promocion = Column(Integer, primary_key=True)
    nombre_promocion = Column(String(55), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    porcentaje_descuento = Column(Numeric(5, 2), nullable=False)
    estado = Column(String(45), nullable=False)

    factura = relationship('Factura', back_populates='promocion')

    def __init__(self, nombre_promocion, fecha_inicio, fecha_fin, porcentaje_descuento, estado, descripcion=None):
        self.nombre_promocion = nombre_promocion
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.porcentaje_descuento = porcentaje_descuento
        self.estado = estado

    def esta_activa(self):
        hoy = datetime.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin and self.estado.lower() == 'activa'

    def aplicar_descuento(self, monto):
        if self.esta_activa():
            return monto - (monto * (self.porcentaje_descuento / 100))
        else:
            raise ValueError("La promoción no está activa o ha expirado.")

    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        session.commit()

    def extender_promocion(self, nueva_fecha_fin):
        if nueva_fecha_fin > self.fecha_fin:
            self.fecha_fin = nueva_fecha_fin
            session.commit()
        else:
            raise ValueError("La nueva fecha de fin debe ser posterior a la fecha de fin actual.")

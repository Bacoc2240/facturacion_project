from sqlalchemy import Column, Integer, String, Date, Boolean
from src.models import Base, session
from datetime import datetime

class ResolucionDIAN(Base):
    __tablename__ = 'resolucion_dian'

    id_resolucion = Column(Integer, primary_key=True)
    numero_resolucion = Column(String(50), nullable=False)
    rango_inicial = Column(Integer, nullable=False)
    rango_final = Column(Integer, nullable=False)
    fecha_inicial = Column(Date, nullable=False)
    fecha_final = Column(Date, nullable=False)
    numero_actual = Column(Integer, nullable=False)
    activa = Column(Boolean, default=True)

    def __init__(self, numero_resolucion, rango_inicial, rango_final, fecha_inicial, fecha_final):
        self.numero_resolucion = numero_resolucion
        self.rango_inicial = rango_inicial
        self.rango_final = rango_final
        self.fecha_inicial = fecha_inicial
        self.fecha_final = fecha_final
        self.numero_actual = rango_inicial

    # Numeración facturas
    def asignar_numero_factura(self):
        if self.numero_actual > self.rango_final:
            raise ValueError("El rango de facturación ha sido agotado.")
        if self.numero_actual >= self.rango_final - 200:
            print("Advertencia: El rango de facturación está próximo a agotarse.")
        if self.numero_actual >= self.rango_final - 5:
            print("Advertencia: Quedan menos de 5 números disponibles.")
        numero_factura = self.numero_actual
        self.numero_actual += 1
        return numero_factura

    # Verifica si la resolución está vigente
    def es_resolucion_valida(self):
        hoy = datetime.now().date()
        return self.fecha_inicial <= hoy <= self.fecha_final

    # Guardar cambios en la base de datos
    def guardar(self):
        session.add(self)
        session.commit()

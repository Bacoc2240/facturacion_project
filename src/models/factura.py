from sqlalchemy import Column, Integer, Float, ForeignKey, Date, Table, String
from sqlalchemy.orm import relationship
from src.models import session, Base
from src.models.cliente import Cliente
from src.models.empleado import Empleado
from src.models.promocion import Promocion
from src.models.metodo_de_pago import MetodoDePago
from src.models.resolucion_dian import ResolucionDIAN


# Tabla intermedia para la relación Many-to-Many entre Factura y MetodoDePago
factura_metodo_de_pago = Table(
    'factura_metodo_de_pago', Base.metadata,
    Column('id', Integer, ForeignKey('factura.id')),
    Column('id_metodo_pago', Integer, ForeignKey('metodo_de_pago.id_metodo_pago')),
    extend_existing=True  # Este parámetro evitará el error de redefinición
)


class Factura(Base):
    __tablename__ = 'factura'

    id = Column(Integer, primary_key=True)
    numero_factura = Column(Integer, nullable=False, unique=True)
    fecha = Column(Date, nullable=False)
    subtotal = Column(Float(10, 2), nullable=False)
    total = Column(Float(10, 2), nullable=False)
    IVA = Column(Float(10, 2), nullable=False)
    descuento_aplicado = Column(Float(10, 2))
    id_cliente = Column(String, ForeignKey('cliente.id_cliente'), nullable=False)
    id_empleado = Column(Integer, ForeignKey('empleado.id_empleado'), nullable=False)
    id_promocion = Column(Integer, ForeignKey('promocion.id_promocion'))
    id_resolucion = Column(Integer, ForeignKey('resolucion_dian.id_resolucion'), nullable=False)

    # Relaciones bidireccionales
    cliente = relationship('Cliente', back_populates='factura')
    empleado = relationship('Empleado', back_populates='factura')
    promocion = relationship('Promocion', back_populates='factura')
    transacciones = relationship('Transaccion', back_populates='factura')

    # Relación Many-to-Many con MetodoDePago
    metodos_pago = relationship('MetodoDePago', secondary=factura_metodo_de_pago, back_populates='facturas')

    def __init__(self, fecha, subtotal, IVA, id_cliente, id_empleado, id_resolucion, descuento_aplicado=None, id_promocion=None, metodos_pago_ids=[]):
        self.fecha = fecha
        self.subtotal = subtotal
        self.IVA = IVA
        self.id_cliente = id_cliente
        self.id_empleado = id_empleado
        self.descuento_aplicado = descuento_aplicado
        self.id_promocion = id_promocion

        # Cálculo automático del número de factura basado en la resolución DIAN
        resolucion = session.query(ResolucionDIAN).filter_by(id_resolucion=id_resolucion).first()
        if resolucion and resolucion.es_resolucion_valida():
            self.numero_factura = resolucion.asignar_numero_factura()
        else:
            raise ValueError("No hay una resolución DIAN válida disponible para la facturación.")

        # Cálculo automático del total
        self.total = self.calcular_total()

        # Agregar los métodos de pago seleccionados
        self.agregar_metodos_pago(metodos_pago_ids)

    # Método para calcular el total con IVA y descuento (si aplica)
    def calcular_total(self):
        total_con_iva = self.subtotal + (self.subtotal * (self.IVA / 100))
        if self.descuento_aplicado:
            total_con_iva -= self.descuento_aplicado
        return total_con_iva

    # Método para aplicar el descuento de una promoción a la factura
    def aplicar_descuento(self, promocion):
        if promocion and promocion.esta_activa():
            self.descuento_aplicado = promocion.aplicar_descuento(self.subtotal)
        else:
            raise ValueError("La promoción no es válida o ha expirado.")
        self.total = self.calcular_total()

    # Método para agregar múltiples métodos de pago a la factura
    def agregar_metodos_pago(self, metodos_pago_ids):
        for metodo_id in metodos_pago_ids:
            metodo = session.query(MetodoDePago).get(metodo_id)
            if metodo:
                self.metodos_pago.append(metodo)
        session.commit()

    # Método para obtener todos los métodos de pago seleccionados
    def obtener_metodos_pago(self):
        return [metodo.nombre_metodo for metodo in self.metodos_pago]

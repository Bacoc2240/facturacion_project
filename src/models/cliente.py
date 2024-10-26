from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from src.models import session, Base
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError

class Cliente(Base):
    __tablename__ = 'cliente'

    id_cliente = Column(String(20), primary_key=True)  # Número de documento del cliente
    tipo_documento = Column(String(3), nullable=False)  # Tipo de documento (CC, TI, CE, PP, PEP)
    nombre_cliente = Column(String(255), nullable=False)
    direccion = Column(String(255))
    telefono = Column(String(20))
    correo_electronico = Column(String(255))
    historial_compras = Column(Text)

    # Constructor del modelo
    def __init__(self, id_cliente, tipo_documento, nombre_cliente, direccion=None, 
                 telefono=None, correo_electronico=None, historial_compras=None):
        self.id_cliente = id_cliente
        self.tipo_documento = tipo_documento
        self.nombre_cliente = nombre_cliente
        self.direccion = direccion
        self.telefono = telefono
        self.correo_electronico = correo_electronico
        self.historial_compras = historial_compras
        
    # Relación con la tabla Factura
    factura = relationship('Factura', back_populates='cliente')

    # Validación para el tipo de documento
    @validates('tipo_documento')
    def validate_tipo_documento(self, key, tipo_documento):
        documentos_validos = ['CC', 'TI', 'CE', 'PP', 'PEP']
        if tipo_documento not in documentos_validos:
            raise ValueError(f"Tipo de documento no válido: {tipo_documento}. Los tipos válidos son: {', '.join(documentos_validos)}.")
        return tipo_documento
    
    # Verificación de existencia del cliente
    @classmethod
    def verificar_existencia_cliente(cls, id_cliente, tipo_documento):
        # Busca en la base de datos si el cliente ya existe
        cliente_existente = session.query(cls).filter_by(id_cliente=id_cliente, tipo_documento=tipo_documento).first()
        if cliente_existente:
            raise ValueError(f"El cliente con documento {tipo_documento} {id_cliente} ya existe.")
        return False

    # Método agregar nuevo cliente
    @classmethod
    def agregar_cliente(cls, id_cliente, tipo_documento, nombre_cliente, direccion=None, telefono=None, correo_electronico=None, historial_compras=None):
        try:
            # Verificar si el cliente ya existe
            cls.verificar_existencia_cliente(id_cliente, tipo_documento)
            # Crea el nuevo cliente
            nuevo_cliente = cls(id_cliente, tipo_documento, nombre_cliente, direccion, telefono, correo_electronico, historial_compras)
            session.add(nuevo_cliente)
            session.commit()
            print(f"Cliente {nombre_cliente} con documento {tipo_documento} {id_cliente} ha sido agregado con éxito.")
        except ValueError as e:
            print(e)
        except IntegrityError:
            session.rollback()
            print("Error al intentar agregar el cliente. Posible problema de integridad en la base de datos.")


    # Método para agregar una compra al historial
    def agregar_compra(self, detalle_compra):
        if self.historial_compras:
            self.historial_compras += f'\n{detalle_compra}'
        else:
            self.historial_compras = detalle_compra

    # Método para actualizar los datos del cliente
    def actualizar_datos(self, nombre=None, direccion=None, telefono=None, correo_electronico=None):
        if nombre:
            self.nombre_cliente = nombre
        if direccion:
            self.direccion = direccion
        if telefono:
            self.telefono = telefono
        if correo_electronico:
            self.correo_electronico = correo_electronico


    
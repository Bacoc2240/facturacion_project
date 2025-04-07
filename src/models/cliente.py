from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from src.models import Base, session  # Usar la sesión global
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
    preferencias = Column(String(255))  # Añadido para almacenar el producto preferido
    activo = Column(Boolean, default=True)

    # Constructor del modelo
    def __init__(self, id_cliente, tipo_documento, nombre_cliente, direccion=None, 
                 telefono=None, correo_electronico=None, historial_compras=None, preferencias=None):
        self.id_cliente = id_cliente
        self.tipo_documento = tipo_documento
        self.nombre_cliente = nombre_cliente
        self.direccion = direccion
        self.telefono = telefono
        self.correo_electronico = correo_electronico
        self.historial_compras = historial_compras
        self.preferencias = preferencias
        
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
    
    def obtener_historial_compras(self):
        """Retorna el historial formateado o 'No Aplica' si está vacío"""
        return self.historial_compras if self.historial_compras else "No aplica"

    def obtener_producto_preferido(self):
        """Determina el producto más comprado del historial y lo guarda en preferencias"""
        if not self.historial_compras:
            self.preferencias = "No aplica"
            return self.preferencias

        try:
            # Separar el historial en productos individuales
            productos = [
                producto.strip()
                for linea in self.historial_compras.split('\n')
                for producto in linea.split(',')
                if producto.strip()
            ]

            if not productos:
                self.preferencias = "No aplica"
                return self.preferencias

            # Contar frecuencia de productos
            from collections import Counter
            conteo = Counter(productos)
            
            # Obtener el más frecuente
            producto_frecuente = conteo.most_common(1)
            self.preferencias = producto_frecuente[0][0] if producto_frecuente else "No aplica"
            
            # Guardar el cambio en la base de datos
            session.commit()
            
            return self.preferencias

        except Exception as e:
            print(f"Error al calcular producto preferido: {e}")
            self.preferencias = "No aplica"
            return self.preferencias

    # Método agregar nuevo cliente
    @classmethod
    def agregar_cliente(cls, id_cliente, tipo_documento, nombre_cliente, direccion=None, 
                    telefono=None, correo_electronico=None, historial_compras=None):
        try:
            # Verificar si el cliente ya existe
            cls.verificar_existencia_cliente(id_cliente, tipo_documento)
            
            # Crear el nuevo cliente
            nuevo_cliente = cls(
                id_cliente=id_cliente,
                tipo_documento=tipo_documento,
                nombre_cliente=nombre_cliente,
                direccion=direccion,
                telefono=telefono,
                correo_electronico=correo_electronico,
                historial_compras=historial_compras
            )
            
            # Calcular preferencias iniciales si hay historial
            if historial_compras:
                nuevo_cliente.preferencias = nuevo_cliente.obtener_producto_preferido()
            else:
                nuevo_cliente.preferencias = "No aplica"
                
            session.add(nuevo_cliente)
            session.commit()
            
            print(f"Cliente {nombre_cliente} con documento {tipo_documento} {id_cliente} ha sido agregado con éxito.")
            return nuevo_cliente
            
        except ValueError as e:
            session.rollback()
            print(f"Error de validación: {str(e)}")
            raise
        except IntegrityError as e:
            session.rollback()
            print(f"Error de integridad en la base de datos: {str(e)}")
            raise ValueError("Error al intentar agregar el cliente. Posible problema de integridad en la base de datos.")
        except Exception as e:
            session.rollback()
            print(f"Error inesperado: {str(e)}")
            raise
            
    # Método para agregar una compra al historial
    def agregar_compra(self, detalle_compra):
        try:
            if self.historial_compras:
                self.historial_compras += f'\n{detalle_compra}'
            else:
                self.historial_compras = detalle_compra
                
            # Actualizar preferencias después de agregar compra
            self.obtener_producto_preferido()
            
            session.commit()
            print(f"Compra agregada y preferencias actualizadas para cliente {self.id_cliente}")
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al agregar compra: {e}")
            return False

    # Método para actualizar los datos del cliente
    def actualizar_datos(self, nombre=None, direccion=None, telefono=None, correo_electronico=None):
        try:
            if nombre:
                self.nombre_cliente = nombre
            if direccion:
                self.direccion = direccion
            if telefono:
                self.telefono = telefono
            if correo_electronico:
                self.correo_electronico = correo_electronico
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar datos del cliente: {e}")
            return False
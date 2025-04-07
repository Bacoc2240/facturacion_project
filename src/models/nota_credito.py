from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models import Base, session

class NotaCredito(Base):
    """
    Modelo para las notas crédito.
    
    Una nota crédito es un documento legal que permite corregir o anular total o parcialmente
    una factura ya emitida. Sirve para reflejar ajustes por devoluciones, descuentos posteriores
    o errores en la facturación.
    """
    __tablename__ = 'nota_credito'
    
    id = Column(Integer, primary_key=True)
    numero = Column(Integer, nullable=False, unique=True, index=True)
    factura_id = Column(Integer, ForeignKey('factura.id'), nullable=False)
    fecha_emision = Column(DateTime, nullable=False, default=datetime.now)
    motivo_dian = Column(Integer, nullable=False)
    observaciones = Column(Text, nullable=True)
    archivo_soporte = Column(String(255), nullable=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    iva = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    enviada = Column(Boolean, default=False)
    fecha_envio = Column(DateTime, nullable=True)
    creado_por = Column(Integer, ForeignKey('empleado.id_empleado'), nullable=True)
    
    # Relaciones - Modificado para evitar el conflicto
    # Eliminamos el back_populates o backref para evitar duplicación
    factura = relationship('Factura')
    detalles = relationship('DetalleNotaCredito', back_populates='nota_credito', cascade='all, delete-orphan')
    empleado = relationship('Empleado', backref='notas_credito_creadas')
    
    def __init__(self, numero, factura_id, fecha_emision=None, motivo_dian=None, 
             observaciones=None, subtotal=0.0, iva=0.0, total=0.0, creado_por=None, 
             archivo_soporte=None, estado="Procesada"):
        """
        Inicializa una nueva nota crédito.
        
        Args:
            numero (int): Número secuencial de la nota crédito.
            factura_id (int): ID de la factura asociada.
            fecha_emision (datetime, optional): Fecha de emisión de la nota crédito. Por defecto es la fecha actual.
            motivo_dian (int): Código del motivo DIAN (1: Devolución parcial, 2: Anulación, etc.)
            observaciones (str, optional): Comentarios adicionales.
            subtotal (float): Monto subtotal de la nota crédito.
            iva (float): Monto de IVA de la nota crédito.
            total (float): Monto total de la nota crédito.
            creado_por (int, optional): ID del empleado que crea la nota crédito.
            archivo_soporte (str, optional): Ruta al archivo de soporte.
            estado (str, optional): Estado de la nota crédito. Por defecto es "Procesada".
        """
        self.numero = numero
        self.factura_id = factura_id  # Cambio de id_factura a factura_id
        self.fecha_emision = fecha_emision or datetime.now()
        self.motivo_dian = motivo_dian
        self.observaciones = observaciones
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.creado_por = creado_por
        self.archivo_soporte = archivo_soporte
        self.estado = estado
        
    def __repr__(self):
        return f"<NotaCredito #{self.numero}>"
    
    @property
    def motivo_descripcion(self):
        """Obtiene la descripción textual del motivo DIAN."""
        motivos = {
            1: 'Devolución parcial de los bienes y/o no aceptación parcial del servicio',
            2: 'Anulación de factura electrónica',
            3: 'Rebaja o descuento parcial o total',
            4: 'Ajuste de precio',
            5: 'Descuento comercial por pronto pago',
            6: 'Descuento comercial por volumen de ventas'
        }
        return motivos.get(self.motivo_dian, 'Motivo no especificado')
    
    @property
    def es_anulacion_total(self):
        """Determina si la nota crédito anula completamente la factura."""
        return self.motivo_dian == 2
    
    def recalcular_totales(self):
        """Recalcula los totales de la nota crédito basados en sus detalles."""
        subtotal = 0.0
        iva_total = 0.0
        
        for detalle in self.detalles:
            subtotal += detalle.subtotal
            iva_total += detalle.valor_iva
            
        self.subtotal = subtotal
        self.iva = iva_total
        self.total = subtotal + iva_total
        
    def marcar_como_enviada(self):
        """Marca la nota crédito como enviada al cliente."""
        self.enviada = True
        self.fecha_envio = datetime.now()
        session.commit()
        
    @classmethod
    def obtener_siguiente_numero(cls):
        """
        Obtiene el siguiente número disponible para una nueva nota crédito.
        
        Returns:
            int: El siguiente número en secuencia.
        """
        ultima_nc = session.query(cls).order_by(cls.numero.desc()).first()
        if ultima_nc:
            return ultima_nc.numero + 1
        return 1
    
    @classmethod
    def buscar_por_factura(cls, factura_id):
        """
        Busca todas las notas crédito asociadas a una factura.
        
        Args:
            factura_id (int): ID de la factura a buscar.
            
        Returns:
            list: Lista de notas crédito asociadas a la factura.
        """
        return session.query(cls).filter_by(factura_id=factura_id).all()

    
    @classmethod
    def factura_tiene_anulacion_total(cls, factura_id):
        """
        Verifica si una factura ya tiene una nota crédito de anulación total.
        
        Args:
            factura_id (int): ID de la factura a verificar.
            
        Returns:
            bool: True si la factura ya tiene una nota crédito de anulación total.
        """
        existe = session.query(cls).filter_by(
            factura_id=factura_id,  # Cambio de id_factura a factura_id
            motivo_dian=2  # Anulación de factura electrónica
        ).first()
        
        return existe is not None
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para serialización JSON
        
        Returns:
            dict: Diccionario con los datos de la nota crédito
        """
        return {
            'id': self.id,
            'numero': self.numero,
            'factura_id': self.factura_id,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'motivo_dian': self.motivo_dian,
            'motivo_descripcion': self.motivo_descripcion,
            'subtotal': float(self.subtotal),
            'iva': float(self.iva),
            'total': float(self.total),
            'observaciones': self.observaciones,
            'archivo_soporte': self.archivo_soporte,
            'estado': getattr(self, 'estado', 'Procesada'),
            'enviada': self.enviada,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None
        }


class DetalleNotaCredito(Base):
    __tablename__ = 'detalle_nota_credito'
    
    id = Column(Integer, primary_key=True)
    nota_credito_id = Column(Integer, ForeignKey('nota_credito.id'), nullable=False)
    detalle_factura_id = Column(Integer, ForeignKey('detalle_factura.id'), nullable=True)
    cantidad = Column(Float, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    porcentaje_iva = Column(Float, nullable=False, default=19.0)
    
    # Relaciones
    nota_credito = relationship('NotaCredito', back_populates='detalles')
    detalle_factura = relationship('DetalleFactura')
    
    def __init__(self, nota_credito_id=None, detalle_factura_id=None, cantidad=0, 
                valor_unitario=0, porcentaje_iva=19.0):
        """
        Inicializa un nuevo detalle de nota crédito.
        
        Args:
            nota_credito_id (int): ID de la nota crédito.
            detalle_factura_id (int): ID del detalle de factura asociado.
            cantidad (float): Cantidad del producto.
            valor_unitario (float): Precio unitario del producto.
            porcentaje_iva (float, optional): Porcentaje de IVA aplicable. Por defecto es 19%.
        """
        self.nota_credito_id = nota_credito_id
        self.detalle_factura_id = detalle_factura_id
        self.cantidad = float(cantidad)
        self.valor_unitario = float(valor_unitario)
        self.porcentaje_iva = float(porcentaje_iva)
        
    def __repr__(self):
        return f"<DetalleNotaCredito #{self.id} - NC #{self.nota_credito_id}>"
    
    @property
    def subtotal(self):
        """Calcula el subtotal del detalle."""
        return self.cantidad * self.valor_unitario
    
    @property
    def valor_iva(self):
        """Calcula el valor del IVA para este detalle."""
        return self.subtotal * (self.porcentaje_iva / 100.0)
    
    @property
    def total(self):
        """Calcula el total del detalle (subtotal + IVA)."""
        return self.subtotal + self.valor_iva
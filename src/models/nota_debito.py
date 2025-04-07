from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models import Base, session

class NotaDebito(Base):
    """
    Modelo para las notas débito.
    
    Una nota débito es un documento legal que se emite para aumentar el valor de una factura ya emitida,
    debido a cargos adicionales, ajustes de precio, o servicios complementarios.
    """
    __tablename__ = 'nota_debito'
    
    id = Column(Integer, primary_key=True)
    numero = Column(Integer, nullable=False, unique=True, index=True)
    factura_id = Column(Integer, ForeignKey('factura.id'), nullable=False)
    fecha_emision = Column(DateTime, nullable=False, default=datetime.now)
    concepto = Column(String(255), nullable=False)
    observaciones = Column(Text, nullable=True)
    archivo_soporte = Column(String(255), nullable=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    valor_iva = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    enviada = Column(Boolean, default=False)
    fecha_envio = Column(DateTime, nullable=True)
    creado_por = Column(Integer, ForeignKey('empleado.id_empleado'), nullable=True)
    estado = Column(String(20), nullable=False, default='Procesada')
    activa = Column(Boolean, nullable=False, default=True)
    
    # Relaciones - Evitamos conflictos con relaciones existentes
    factura = relationship('Factura')
    detalles = relationship('DetalleNotaDebito', back_populates='nota_debito', cascade='all, delete-orphan')
    empleado = relationship('Empleado', backref='notas_debito_creadas')
    
    def __init__(self, numero, factura_id, fecha_emision=None, concepto=None, 
                 observaciones=None, subtotal=0.0, valor_iva=0.0, total=0.0, 
                 estado='Procesada', creado_por=None, archivo_soporte=None):
        """
        Inicializa una nueva nota débito.
        
        Args:
            numero (int): Número secuencial de la nota débito.
            factura_id (int): ID de la factura asociada.
            fecha_emision (datetime, optional): Fecha de emisión de la nota débito. Por defecto es la fecha actual.
            concepto (str): Concepto o motivo de la nota débito.
            observaciones (str, optional): Comentarios adicionales.
            subtotal (float): Monto subtotal de la nota débito.
            valor_iva (float): Monto de IVA de la nota débito.
            total (float): Monto total de la nota débito.
            estado (str): Estado de la nota débito (Procesada, Anulada, etc.)
            creado_por (int, optional): ID del empleado que crea la nota débito.
            archivo_soporte (str, optional): Ruta al archivo de soporte.
        """
        self.numero = numero
        self.factura_id = factura_id
        self.fecha_emision = fecha_emision or datetime.now()
        self.concepto = concepto
        self.observaciones = observaciones
        self.subtotal = subtotal
        self.valor_iva = valor_iva
        self.total = total
        self.estado = estado
        self.creado_por = creado_por
        self.archivo_soporte = archivo_soporte
        self.activa = True
        
    def __repr__(self):
        return f"<NotaDebito #{self.numero}>"
    
    def recalcular_totales(self):
        """Recalcula los totales de la nota débito basados en sus detalles."""
        subtotal = 0.0
        iva_total = 0.0
        
        for detalle in self.detalles:
            subtotal += detalle.subtotal
            iva_total += detalle.valor_iva
            
        self.subtotal = subtotal
        self.valor_iva = iva_total
        self.total = subtotal + iva_total
        
    def marcar_como_enviada(self):
        """Marca la nota débito como enviada al cliente."""
        self.enviada = True
        self.fecha_envio = datetime.now()
        session.commit()
        
    def anular(self):
        """Anula la nota débito."""
        self.activa = False
        self.estado = 'Anulada'
        self.fecha_modificacion = datetime.now()
        
    @classmethod
    def obtener_siguiente_numero(cls):
        """
        Obtiene el siguiente número disponible para una nueva nota débito.
        
        Returns:
            int: El siguiente número en secuencia.
        """
        ultima_nd = session.query(cls).order_by(cls.numero.desc()).first()
        if ultima_nd:
            return ultima_nd.numero + 1
        return 1
    
    @classmethod
    def buscar_por_factura(cls, factura_id):
        """
        Busca todas las notas débito asociadas a una factura.
        
        Args:
            factura_id (int): ID de la factura a buscar.
            
        Returns:
            list: Lista de notas débito asociadas a la factura.
        """
        return session.query(cls).filter_by(factura_id=factura_id, activa=True).all()
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para serialización JSON
        
        Returns:
            dict: Diccionario con los datos de la nota débito
        """
        return {
            'id': self.id,
            'numero': self.numero,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'factura_id': self.factura_id,
            'concepto': self.concepto,
            'subtotal': float(self.subtotal),
            'valor_iva': float(self.valor_iva),
            'total': float(self.total),
            'observaciones': self.observaciones,
            'archivo_soporte': self.archivo_soporte,
            'estado': self.estado,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None
        }


class DetalleNotaDebito(Base):
    """
    Modelo para los detalles de una nota débito.
    
    Cada detalle representa un cargo adicional o concepto incluido en la nota débito.
    """
    __tablename__ = 'detalle_nota_debito'
    
    id = Column(Integer, primary_key=True)
    id_nota_debito = Column(Integer, ForeignKey('nota_debito.id'), nullable=False)
    descripcion = Column(String(255), nullable=False)
    cantidad = Column(Float, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False)
    porcentaje_iva = Column(Float, nullable=False, default=19.0)
    subtotal = Column(Float, nullable=False, default=0.0)
    
    # Relaciones
    nota_debito = relationship('NotaDebito', back_populates='detalles')
    
    def __init__(self, id_nota_debito, descripcion, cantidad, precio_unitario, 
                porcentaje_iva=19.0, subtotal=None):
        """
        Inicializa un nuevo detalle de nota débito.
        
        Args:
            id_nota_debito (int): ID de la nota débito.
            descripcion (str): Descripción del cargo o concepto.
            cantidad (float): Cantidad.
            precio_unitario (float): Precio unitario.
            porcentaje_iva (float, optional): Porcentaje de IVA aplicable. Por defecto es 19%.
            subtotal (float, optional): Subtotal calculado. Si es None, se calcula automáticamente.
        """
        self.id_nota_debito = id_nota_debito
        self.descripcion = descripcion
        self.cantidad = float(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.porcentaje_iva = float(porcentaje_iva)
        
        # Calcular subtotal si no se proporciona
        if subtotal is None:
            self.subtotal = self.cantidad * self.precio_unitario
        else:
            self.subtotal = float(subtotal)
        
    def __repr__(self):
        return f"<DetalleNotaDebito #{self.id} - ND #{self.id_nota_debito}>"
    
    @property
    def valor_iva(self):
        """Calcula el valor del IVA para este detalle."""
        return self.subtotal * (self.porcentaje_iva / 100.0)
    
    @property
    def total(self):
        """Calcula el total del detalle (subtotal + IVA)."""
        return self.subtotal + self.valor_iva
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para serialización JSON
        
        Returns:
            dict: Diccionario con los datos del detalle
        """
        return {
            'id': self.id,
            'id_nota_debito': self.id_nota_debito,
            'descripcion': self.descripcion,
            'cantidad': float(self.cantidad),
            'precio_unitario': float(self.precio_unitario),
            'porcentaje_iva': float(self.porcentaje_iva),
            'subtotal': float(self.subtotal),
            'iva': self.valor_iva,
            'total': self.total
        }
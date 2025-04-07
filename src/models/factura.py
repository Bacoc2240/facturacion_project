from sqlalchemy import Column, Integer, Float, ForeignKey, Date, Table, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from src.models import Base, session
from src.models.metodo_de_pago import MetodoDePago
from src.models.resolucion_dian import ResolucionDIAN
from src.models.detalle_factura import DetalleFactura
from src.models.productos import Productos

from datetime import date

# Tabla intermedia para la relación Many-to-Many entre Factura y MetodoDePago
factura_metodo_de_pago = Table(
    'factura_metodo_de_pago', 
    Base.metadata,
    Column('id', Integer, ForeignKey('factura.id')),
    Column('id_metodo_pago', Integer, ForeignKey('metodo_de_pago.id_metodo_pago')),
    extend_existing=True
)

class Factura(Base):
    __tablename__ = 'factura'
    
    # Campos básicos de identificación
    id = Column(Integer, primary_key=True)
    numero_factura = Column(Integer, nullable=False, unique=True)
    fecha = Column(Date, nullable=False)
    
    # Campos para valores monetarios - usando Numeric para mayor precisión
    subtotal = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    IVA = Column(Numeric(10, 2), nullable=False)
    descuento_aplicado = Column(Numeric(10, 2))
    
    # Claves foráneas
    id_cliente = Column(String(20), ForeignKey('cliente.id_cliente'), nullable=False)
    id_empleado = Column(Integer, ForeignKey('empleado.id_empleado'), nullable=False)
    id_promocion = Column(Integer, ForeignKey('promocion.id_promocion'))
    id_resolucion = Column(Integer, ForeignKey('resolucion_dian.id_resolucion'), nullable=False)
    
    # Campo de estado y control
    estado = Column(String(20), default='APROBADA')  # PENDIENTE, APROBADA, ANULADA
    activa = Column(Boolean, default=True)
    fecha_modificacion = Column(Date)
    
    # Relaciones
    cliente = relationship('Cliente', back_populates='factura')
    empleado = relationship('Empleado', back_populates='factura')
    promocion = relationship('Promocion', back_populates='factura')
    transacciones = relationship('Transaccion', back_populates='factura')
    metodos_pago = relationship('MetodoDePago', 
                              secondary=factura_metodo_de_pago, 
                              back_populates='factura')
    detalles = relationship('DetalleFactura', back_populates='factura', cascade="all, delete-orphan")
    notas_credito = relationship("NotaCredito", 
                            foreign_keys="NotaCredito.factura_id",  
                            primaryjoin="Factura.id==NotaCredito.factura_id",
                            lazy="joined",  
                            viewonly=True)  

    notas_debito = relationship("NotaDebito", 
                            foreign_keys="NotaDebito.factura_id",  
                            primaryjoin="Factura.id==NotaDebito.factura_id",
                            lazy="joined",  
                            viewonly=True)

    def __init__(self, fecha, subtotal, IVA, id_cliente, id_empleado, id_resolucion, 
                 descuento_aplicado=None, id_promocion=None, metodos_pago_ids=None):
        """
        Inicializa una nueva factura con todos los campos necesarios.
        Realiza validaciones y cálculos automáticos.
        """
        self.fecha = fecha
        self.subtotal = subtotal
        self.IVA = IVA
        self.id_cliente = id_cliente
        self.id_empleado = id_empleado
        self.descuento_aplicado = descuento_aplicado
        self.id_promocion = id_promocion
        self.estado = 'APROBADA'
        self.activa = True
        self.fecha_modificacion = date.today()
        
        # Asignar número de factura según resolución DIAN
        self._asignar_numero_factura(id_resolucion)
        
        # Calcular el total incluyendo IVA y descuentos
        self.total = self.calcular_total()
        
        # Agregar métodos de pago si se proporcionaron
        if metodos_pago_ids:
            self.agregar_metodos_pago(metodos_pago_ids)

    def _asignar_numero_factura(self, id_resolucion):
        """
        Asigna un número de factura válido según la resolución DIAN.
        Maneja la lógica de validación y asignación.
        """
        resolucion = session.query(ResolucionDIAN).filter_by(id_resolucion=id_resolucion).first()
        if not resolucion:
            raise ValueError("Resolución DIAN no encontrada")
            
        if not resolucion.es_resolucion_valida():
            raise ValueError("La resolución DIAN no es válida o ha expirado")
            
        self.numero_factura = resolucion.asignar_numero_factura()
        self.id_resolucion = id_resolucion

    def calcular_total(self):
        """
        Calcula el total de la factura incluyendo IVA y descuentos.
        Retorna el valor como Decimal para mayor precisión.
        """
        total = self.subtotal * (1 + (self.IVA / 100))
        if self.descuento_aplicado:
            total -= self.descuento_aplicado
        return round(total, 2)

    def anular(self):
        """
        Anula la factura, registrando la fecha de modificación.
        """
        if self.estado == 'ANULADA':
            raise ValueError("La factura ya está anulada")
            
        self.activa = False
        self.estado = 'ANULADA'
        self.fecha_modificacion = date.today()

    def cambiar_estado(self, nuevo_estado):
        """
        Actualiza el estado de la factura con validaciones.
        """
        estados_validos = ['PENDIENTE', 'APROBADA', 'ANULADA']
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado no válido. Debe ser uno de: {estados_validos}")
            
        self.estado = nuevo_estado
        self.fecha_modificacion = date.today()

    @classmethod
    def obtener_facturas_activas(cls):
        """
        Obtiene todas las facturas activas ordenadas por fecha.
        """
        return session.query(cls)\
            .filter_by(activa=True)\
            .order_by(cls.fecha.desc())\
            .all()

    @classmethod
    def obtener_facturas_por_periodo(cls, fecha_inicio, fecha_fin):
        """
        Obtiene facturas dentro de un rango de fechas específico.
        """
        return session.query(cls)\
            .filter(cls.fecha.between(fecha_inicio, fecha_fin))\
            .filter_by(activa=True)\
            .order_by(cls.fecha.desc())\
            .all()
            
    def agregar_producto(self, id_producto, cantidad, precio_unitario, porcentaje_iva=19.0):
        """
        Agrega un producto a la factura y crea el detalle correspondiente
        
        Args:
            id_producto: ID del producto a agregar
            cantidad: Cantidad del producto
            precio_unitario: Precio unitario del producto
            porcentaje_iva: Porcentaje de IVA específico para este producto (predeterminado: 19%)
        """
        try:
            # Verificar que la factura tenga un ID asignado
            if self.id is None:
                raise ValueError("La factura debe guardarse primero antes de agregar productos")
                
            # Verificar que el producto existe y tiene stock suficiente
            producto = session.query(Productos).get(id_producto)
            if not producto:
                raise ValueError(f"El producto con ID {id_producto} no existe")
            
            if producto.stock < cantidad:
                raise ValueError(f"Stock insuficiente para el producto {producto.nombre}")
            
            # Crear el detalle de la factura asegurando que se asigna el id_factura y el porcentaje_iva
            detalle = DetalleFactura(
                precio_unitario=precio_unitario,
                cantidad=cantidad,
                id_factura=self.id,
                id_producto=id_producto,
                porcentaje_iva=porcentaje_iva  # Usar el porcentaje de IVA específico
            )
            
            # Calcular el subtotal 
            detalle.calcular_subtotal()
            
            # Actualizar el stock del producto
            producto.stock -= cantidad
            
            # Agregar el detalle a la sesión sin hacer commit
            session.add(detalle)
            session.flush()  # Esto asigna un ID al detalle sin hacer commit completo
            
            # Actualizar los totales de la factura
            # Nota: Aquí podríamos necesitar recalcular el IVA total considerando
            # los porcentajes específicos de cada producto
            self.subtotal += detalle.subtotal
            
            # Calcular el IVA para este detalle específico
            iva_detalle = detalle.subtotal * (porcentaje_iva / 100)
            
            # Actualizar el IVA total de la factura
            # (podría requerir un enfoque más sofisticado para múltiples porcentajes)
            self.IVA = float(self.IVA) + float(iva_detalle)
            
            # Recalcular el total
            self.total = self.calcular_total()
            
            return detalle
            
        except Exception as e:
            raise ValueError(f"Error al agregar producto: {str(e)}")

    def eliminar_producto(self, id_detalle):
        """
        Elimina un producto de la factura
        
        Args:
            id_detalle: ID del detalle de factura a eliminar
        """
        try:
            detalle = session.query(DetalleFactura).get(id_detalle)
            if not detalle or detalle.id_factura != self.id:
                raise ValueError("Detalle de factura no encontrado")
            
            # Restaurar el stock del producto (modificado: usar 'stock' en lugar de 'stock_actual')
            producto = session.query(Productos).get(detalle.id_producto)
            if producto:
                producto.stock += detalle.cantidad
            
            # Actualizar los totales de la factura
            self.subtotal -= detalle.subtotal
            self.total = self.calcular_total()
            
            # Eliminar el detalle
            session.delete(detalle)
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise ValueError(f"Error al eliminar producto: {str(e)}")

    def actualizar_cantidad_producto(self, id_detalle, nueva_cantidad):
        """
        Actualiza la cantidad de un producto en la factura
        
        Args:
            id_detalle: ID del detalle de factura a actualizar
            nueva_cantidad: Nueva cantidad del producto
        """
        try:
            detalle = session.query(DetalleFactura).get(id_detalle)
            if not detalle or detalle.id_factura != self.id:
                raise ValueError("Detalle de factura no encontrado")
            
            producto = session.query(Productos).get(detalle.id_producto)
            if not producto:
                raise ValueError("Producto no encontrado")
            
            # Calcular la diferencia de stock
            diferencia = nueva_cantidad - detalle.cantidad
            
            # Modificado: usar 'stock' en lugar de 'stock_actual'
            if producto.stock < diferencia:
                raise ValueError(f"Stock insuficiente para el producto {producto.nombre}")
            
            # Actualizar el stock (modificado: usar 'stock' en lugar de 'stock_actual')
            producto.stock -= diferencia
            
            # Actualizar el detalle
            detalle.cantidad = nueva_cantidad
            detalle.calcular_subtotal()
            
            # Actualizar los totales de la factura
            self.recalcular_totales()
            
            session.commit()
            return detalle
            
        except Exception as e:
            session.rollback()
            raise ValueError(f"Error al actualizar cantidad: {str(e)}")

    def recalcular_totales(self):
        """
        Recalcula los totales de la factura basándose en sus detalles
        """
        detalles = session.query(DetalleFactura).filter_by(id_factura=self.id).all()
        self.subtotal = sum(detalle.subtotal for detalle in detalles)
        self.total = self.calcular_total()
        
    def agregar_metodos_pago(self, metodos_pago_ids):
        """
        Agrega métodos de pago a la factura
        
        Args:
            metodos_pago_ids: ID o lista de IDs de métodos de pago
        """
        try:
            # Si no es una lista, convertirlo a lista
            if not isinstance(metodos_pago_ids, list):
                metodos_pago_ids = [metodos_pago_ids]
            
            # Obtener los métodos de pago y agregarlos a la factura
            for metodo_id in metodos_pago_ids:
                metodo = session.query(MetodoDePago).get(metodo_id)
                if metodo:
                    # Comprobar si ya existe la relación para evitar duplicados
                    if metodo not in self.metodos_pago:
                        self.metodos_pago.append(metodo)
                        print(f"Método de pago {metodo.nombre_metodo} (ID: {metodo.id_metodo_pago}) añadido a la factura")
                else:
                    print(f"Método de pago con ID {metodo_id} no encontrado")
            
            # Guardar cambios sin hacer commit (solo flush)
            session.flush()
            
        except Exception as e:
            print(f"Error al agregar métodos de pago: {str(e)}")
            raise ValueError(f"Error al agregar métodos de pago: {str(e)}")
        
    def obtener_notas_asociadas(self):
        """
        Obtiene todas las notas crédito y débito asociadas a esta factura
        
        Returns:
            dict: Diccionario con las notas crédito y débito
        """
        # Convertimos notas a diccionarios para JSON
        notas_credito_list = []
        for nc in self.notas_credito:
            # Verificamos si la nota está activa (si tiene ese atributo)
            if not hasattr(nc, 'activa') or nc.activa:
                # Verificamos si tiene método to_dict
                if hasattr(nc, 'to_dict'):
                    notas_credito_list.append(nc.to_dict())
                else:
                    # Crear diccionario manualmente con atributos básicos
                    notas_credito_list.append({
                        'id': nc.id,
                        'numero': nc.numero,
                        'fecha': nc.fecha_emision.isoformat() if hasattr(nc, 'fecha_emision') else None,
                        'motivo': nc.motivo_dian if hasattr(nc, 'motivo_dian') else None,
                        'total': float(nc.total) if hasattr(nc, 'total') else 0.0
                    })
                    
        # Lo mismo para notas débito
        notas_debito_list = []
        for nd in self.notas_debito:
            if not hasattr(nd, 'activa') or nd.activa:
                if hasattr(nd, 'to_dict'):
                    notas_debito_list.append(nd.to_dict())
                else:
                    notas_debito_list.append({
                        'id': nd.id,
                        'numero': nd.numero,
                        'fecha': nd.fecha_emision.isoformat() if hasattr(nd, 'fecha_emision') else None,
                        'concepto': nd.concepto if hasattr(nd, 'concepto') else None,
                        'total': float(nd.total) if hasattr(nd, 'total') else 0.0
                    })
        
        return {
            'notas_credito': notas_credito_list,
            'notas_debito': notas_debito_list
        }
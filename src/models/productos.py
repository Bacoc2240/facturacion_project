from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
import random
from sqlalchemy.sql import func
from src.models import Base, session
from src.models.categorias import Categorias
from src.models.auditoria import Auditoria
from sqlalchemy.exc import IntegrityError

class Productos(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    codigo_barras = Column(String(50), unique=True)
    nombre = Column(String(55))
    genero = Column(String(55))
    descripcion = Column(String(300), nullable=False)
    stock = Column(Integer, nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    categoria = relationship('Categorias', backref='productos')
    
    def __init__(self, codigo_barras, nombre, genero, descripcion, stock, precio, categoria_id):
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.genero = genero
        self.descripcion = descripcion
        self.stock = stock
        self.precio = precio
        self.categoria_id = categoria_id
        
    @classmethod
    def obtener_productos(cls, session):
        """
        Obtiene todos los productos activos de la base de datos.
        
        Args:
            session: Sesión de SQLAlchemy
            
        Returns:
            List[Productos]: Lista de objetos Producto
        """
        try:
            return session.query(cls).filter_by(activo=True).all()
        except Exception as e:
            print(f"Error al obtener productos: {str(e)}")
            raise
    
    @staticmethod
    def obtener_producto_por_codigo(session, codigo_barras):
        return session.query(Productos).filter_by(codigo_barras=codigo_barras).first()
    
    @staticmethod
    def generar_codigo_barras(session):
        MAX_INTENTOS = 100
        for _ in range(MAX_INTENTOS):
            codigo = str(random.randint(1000000000, 9999999999))
            if not session.query(Productos).filter_by(codigo_barras=codigo).first():
                return codigo
        raise ValueError("No se pudo generar un código de barras único después de múltiples intentos")

    @staticmethod
    def crear_producto(datos, usuario_id, session):
        try:
            categorias_existentes = session.query(Categorias).count()
            if categorias_existentes == 0:
                raise ValueError("No hay categorías disponibles")
            
            codigo_barras = datos.get('codigo_barras') or Productos.generar_codigo_barras(session)
            
            if Productos.obtener_producto_por_codigo(session, codigo_barras):
                raise ValueError("El producto ya existe")
            
            # Formatear el precio antes de guardar
            precio = round(float(datos['precio']), 2)
            
            nuevo_producto = Productos(
                codigo_barras=codigo_barras,
                nombre=datos['nombre'],
                genero=datos['genero'],
                descripcion=datos['descripcion'],
                stock=int(datos['stock']) if datos.get('stock') else 0,
                precio= precio,
                categoria_id=int(datos['categoria_id'])
            )
            
            # Primero agregamos y hacemos commit del producto
            session.add(nuevo_producto)
            session.commit()
            
            # Usamos el método de clase crear_auditoria
            Auditoria.crear_auditoria(
                tabla='productos',
                accion='crear',
                registro_id=nuevo_producto.id,
                usuario_id=usuario_id,
                detalles=f"Creación del producto: {datos['nombre']}"
            )
            
            return nuevo_producto
            
        except IntegrityError:
            session.rollback()
            raise ValueError("Error de integridad en la base de datos")
        except Exception as e:
            session.rollback()
            raise ValueError(f"Error al crear el producto: {str(e)}")
    
    def actualizar(self, datos, usuario_id):
        try:
            for key, value in datos.items():
                if hasattr(self, key) and key not in ['id', 'codigo_barras']:  # No permitimos actualizar id ni código de barras
                    setattr(self, key, value)
                    
            
            auditoria = Auditoria(
                tabla='productos',
                accion='actualizar',
                registro_id=self.id,
                usuario_id=usuario_id,
                detalles=f"Actualización del producto: {self.nombre}"
            )
            session.add(auditoria)
            session.commit()
            return self
            
        except Exception as e:
            session.rollback()
            raise e
    
    def suspender(self, usuario_id):
        try:
            self.activo = False
            auditoria = Auditoria(
                tabla='productos',
                accion='suspender',
                registro_id=self.id,
                usuario_id=usuario_id,
                detalles=f"Suspensión del producto: {self.nombre}"
            )
            session.add(auditoria)
            session.commit()
            return self
            
        except Exception as e:
            session.rollback()
            raise e
    
    def reactivar(self, usuario_id):
        try:
            self.activo = True
            auditoria = Auditoria(
                tabla='productos',
                accion='reactivar',
                registro_id=self.id,
                usuario_id=usuario_id,
                detalles=f"Reactivación del producto: {self.nombre}"
            )
            session.add(auditoria)
            session.commit()
            return self
            
        except Exception as e:
            session.rollback()
            raise e

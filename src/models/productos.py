from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models import session, Base
from src.models.categorias import Categorias 
from src.models.auditoria import Auditoria



#Instancio el objeto productos mediante una clase
class Productos(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    codigo_barras = Column(String(50), unique=True)
    nombre = Column(String(55))
    genero = Column(String(55))
    descripcion = Column(String(300), unique=True, nullable=False)
    stock = Column(Float(10, 8), nullable=False)
    precio = Column(Float(10,8), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    categoria = relationship('Categorias', backref='productos')
    
    # Método Constructor, permite construir un elmento de esa clase
    def __init__(self, codigo_barras, nombre, genero, descripcion, stock, precio, categoria_id):
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.genero = genero
        self.descripcion = descripcion
        self.stock = stock
        self.precio = precio
        self.categoria_id = categoria_id
        
    # Método CRUD que para que gestionar la base de datos. 
    @staticmethod
    def obtener_productos():
        return session.query(Productos).join(Categorias).filter(Productos.activo == True).all()
    
    @staticmethod
    def obtener_producto_por_codigo(codigo_barras):
        return session.query(Productos).filter_by(codigo_barras=codigo_barras).first()
    
    @staticmethod
    def crear_producto(datos, usuario_id):
        try:
            # Verificar si el producto ya existe
            if Productos.obtener_producto_por_codigo(datos['codigo_barras']):
                raise ValueError("El producto ya existe en la base de datos")
            
            nuevo_producto = Productos(
                codigo_barras=datos['codigo_barras'],
                nombre=datos['nombre'],
                genero=datos['genero'],
                descripcion=datos['descripcion'],
                stock=datos['stock'],
                precio=datos['precio'],
                categoria_id=datos['categoria_id']
            )
            
            session.add(nuevo_producto)
            
            # Registrar auditoría
            auditoria = Auditoria(
                tabla='productos',
                accion='crear',
                registro_id=nuevo_producto.id,
                usuario_id=usuario_id,
                detalles=f"Creación del producto: {nuevo_producto.nombre}"
            )
            session.add(auditoria)
            
            session.commit()
            return nuevo_producto
            
        except Exception as e:
            session.rollback()
            raise e
    
    def actualizar(self, datos, usuario_id):
        try:
            for key, value in datos.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            # Registrar auditoría
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
            
            # Registrar auditoría
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
            
            # Registrar auditoría
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
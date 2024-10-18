from sqlalchemy import Column, Integer, String, Float, ForeignKey
from src.models import session, Base
from src.models.categorias import Categorias 

#Instancio el objeto productos mediante una clase
class Productos(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(55))
    genero = Column(String(55))
    descripcion = Column(String(300), unique=True, nullable=False)
    stock = Column(Float(10, 8), nullable=False)
    precio = Column(Float(10,8), nullable=False)
    categoria = Column(Integer, ForeignKey('categorias.id'), nullable=False)
    
    # Constructor que recibe los datos cuando se llama la clase
    def __init__(self, nombre, genero, descripcion, stock, precio, categoria):
        self.nombre = nombre
        self.genero = genero
        self.descripcion = descripcion
        self.stock = stock
        self.precio = precio
        self.categoria = categoria

    def obtener_productos():
        productos = session.query(Productos).join(Categorias).all()
        return productos
    
    def agregar_producto(producto):
        producto = session.add(producto)
        session.commit()
        return producto
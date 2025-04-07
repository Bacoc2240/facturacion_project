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
    
    @classmethod
    def crear_resolucion_inicial(cls):
        """
        Crea una resolución DIAN inicial si no existe ninguna en la base de datos.
        Este método es llamado al inicializar el controlador.
        """
        try:
            # Verificar si ya existe alguna resolución
            resoluciones_existentes = session.query(cls).count()
            
            # Si ya existen resoluciones, no hacemos nada
            if resoluciones_existentes > 0:
                print("Ya existen resoluciones DIAN, no se creará una inicial.")
                return
            
            # Crear una resolución por defecto con fechas actuales
            hoy = datetime.now().date()
            un_anio_despues = hoy.replace(year=hoy.year + 1)
            
            # Crear la resolución inicial
            resolucion_inicial = cls(
                numero_resolucion="INICIAL-AUTO",
                rango_inicial=1,
                rango_final=1000,
                fecha_inicial=hoy,
                fecha_final=un_anio_despues
            )
            
            # Guardar en la base de datos
            session.add(resolucion_inicial)
            session.commit()
            print("Resolución DIAN inicial creada automáticamente")
        except Exception as e:
            session.rollback()
            print(f"Error al crear resolución DIAN inicial: {str(e)}")
            raise
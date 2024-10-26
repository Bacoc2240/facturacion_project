from sqlalchemy import Column, Integer, String, Date, Boolean
from src.models import session, Base
from sqlalchemy.orm import relationship

class Empleado(Base):
    __tablename__ = 'empleado'

    id_empleado = Column(Integer, primary_key=True)
    nombre_apellidos = Column(String(255), nullable=False)
    numero_identificacion = Column(String(20), unique=True, nullable=False) 
    correo_electronico = Column(String(60), nullable=False)
    telefono = Column(String(45), nullable=False)
    fecha_contratacion = Column((Date), nullable=False)
    cargo = Column(String(45), nullable=False)
    activo = Column(Boolean, default=True)  
    fecha_activacion = Column((Date), nullable=False) 

    factura = relationship('Factura', back_populates='empleado')
    usuario = relationship('Usuario', back_populates='empleado', uselist=False)

    def __init__(self, nombre_apellidos, numero_identificacion, correo_electronico, telefono, fecha_contratacion, cargo):
        self.nombre_apellidos = nombre_apellidos
        self.numero_identificacion = numero_identificacion
        self.correo_electronico = correo_electronico
        self.telefono = telefono
        self.fecha_contratacion = fecha_contratacion
        self.cargo = cargo
        self.fecha_activacion = None

    @staticmethod
    def verificar_empleado(numero_identificacion):
        empleado = session.query(Empleado).filter_by(numero_identificacion=numero_identificacion).first()
        return empleado

    @staticmethod
    def agregar_o_activar_empleado(nombre_apellidos, email, telefono, fecha_contratacion, cargo, numero_identificacion):
        empleado_existente = Empleado.verificar_empleado(numero_identificacion)

        if empleado_existente:
            if not empleado_existente.activo:
                empleado_existente.activo = True
                empleado_existente.fecha_activacion = date.today()
                session.commit()
                print(f"Empleado activado nuevamente. Fecha de activación: {empleado_existente.fecha_activacion}")
            else:
                raise ValueError("El empleado ya existe y está activo.")
        else:
            nuevo_empleado = Empleado(nombre_apellidos, email, telefono, fecha_contratacion, cargo, numero_identificacion)
            session.add(nuevo_empleado)
            session.commit()
            print(f"Empleado {nombre_apellidos} agregado correctamente.")

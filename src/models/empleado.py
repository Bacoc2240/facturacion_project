from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from src.models import Base, session
from datetime import date
from src.models.factura import Factura

class Empleado(Base):
    __tablename__ = 'empleado'
    id_empleado = Column(Integer, primary_key=True)
    nombre_apellidos = Column(String(255), nullable=False)
    numero_identificacion = Column(String(20), unique=True, nullable=False)
    correo_electronico = Column(String(60), nullable=False)
    telefono = Column(String(45), nullable=False)
    fecha_contratacion = Column(Date, nullable=False)
    cargo = Column(String(45), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_activacion = Column(Date, nullable=False)
    is_test_data = Column(Boolean, default=True)

    # Relaciones
    factura = relationship('Factura', back_populates='empleado')
    usuario = relationship('Usuario', back_populates='empleado', uselist=False)

    def __init__(self, nombre_apellidos, numero_identificacion, correo_electronico, telefono, fecha_contratacion, cargo, activo=True, is_test_data=True):
        self.nombre_apellidos = nombre_apellidos
        self.numero_identificacion = numero_identificacion
        self.correo_electronico = correo_electronico
        self.telefono = telefono
        self.fecha_contratacion = fecha_contratacion
        self.cargo = cargo
        self.activo = activo
        self.fecha_activacion = date.today() if activo else None
        self.is_test_data = is_test_data
        
    @staticmethod
    def verificar_empleado(numero_identificacion):
        empleado = session.query(Empleado).filter_by(numero_identificacion=numero_identificacion).first()
        return empleado

    @staticmethod
    def agregar_o_activar_empleado(nombre_apellidos, correo_electronico, telefono, fecha_contratacion, cargo, numero_identificacion):
        # Input validation
        if not all([nombre_apellidos, correo_electronico, telefono, fecha_contratacion, cargo, numero_identificacion]):
            raise ValueError("Todos los campos son obligatorios")
        
        try:
            empleado_existente = Empleado.verificar_empleado(numero_identificacion)
            
            if empleado_existente:
                if not empleado_existente.activo:
                    empleado_existente.activo = True
                    empleado_existente.fecha_activacion = date.today()
                    session.commit()
                    print(f"Empleado activado nuevamente. Fecha de activación: {empleado_existente.fecha_activacion}")
                    return empleado_existente
                else:
                    raise ValueError("El empleado ya existe y está activo.")
            else:
                nuevo_empleado = Empleado(
                    nombre_apellidos=nombre_apellidos,
                    numero_identificacion=numero_identificacion,
                    correo_electronico=correo_electronico,
                    telefono=telefono,
                    fecha_contratacion=fecha_contratacion,
                    cargo=cargo
                )
                session.add(nuevo_empleado)
                session.commit()
                print(f"Empleado {nombre_apellidos} agregado correctamente.")
                return nuevo_empleado
        except Exception as e:
            session.rollback()
            print(f"Error al agregar o activar empleado: {str(e)}")
            raise
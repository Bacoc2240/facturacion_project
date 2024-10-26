from flask_sqlalchemy import SQLAlchemy
import psycopg2 #Adaptador para bd PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship 

#Crear motor de la base de datos
engine = create_engine("postgresql+psycopg2://postgres:adsof2024@localhost:5432/facturacion_project",
                       connect_args={"options": "-c timezone=UTC"}
                       )

#Conectar a la base de datos
connection = engine.connect()

#Clase base para los modelos
Base = declarative_base()
Base.metadata.bind = engine

# Crear una sesión
Session = sessionmaker(bind=engine)

session = Session()
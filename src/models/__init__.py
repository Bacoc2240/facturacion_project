# src/__init__.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Crear motor de la base de datos
engine = create_engine(
    "postgresql+psycopg2://postgres:adsof2024@localhost:5432/facturacion_project",
    connect_args={"options": "-c timezone=UTC"}
)

Base = declarative_base()
Base.metadata.bind = engine

# Crear una sesión global
Session = sessionmaker(bind=engine)
session = Session()  








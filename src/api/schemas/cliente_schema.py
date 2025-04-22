# src/api/schemas/cliente_schema.py
from src.extensions import ma
from src.models.cliente import Cliente

class ClienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cliente
        include_fk = True
        load_instance = True

cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)
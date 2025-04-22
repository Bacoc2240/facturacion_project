from flask import request
from flask_restful import Resource
from src.models.cliente import Cliente
from src.models import session as db
from src.api.schemas.cliente_schema import cliente_schema, clientes_schema

class ClienteListResource(Resource):
    def get(self):
        clientes = Cliente.query.all()
        return clientes_schema.dump(clientes)
    
    def post(self):
        cliente_data = request.get_json()
        cliente = cliente_schema.load(cliente_data)
        db.session.add(cliente)
        db.session.commit()
        return cliente_schema.dump(cliente), 201

class ClienteResource(Resource):
    def get(self, cliente_id):
        cliente = Cliente.query.get_or_404(cliente_id)
        return cliente_schema.dump(cliente)
        
    def put(self, cliente_id):
        cliente = Cliente.query.get_or_404(cliente_id)
        cliente_data = request.get_json()
        
        # Actualiza los campos
        for key, value in cliente_data.items():
            setattr(cliente, key, value)
            
        db.session.commit()
        return cliente_schema.dump(cliente)
        
    def delete(self, cliente_id):
        cliente = Cliente.query.get_or_404(cliente_id)
        db.session.delete(cliente)
        db.session.commit()
        return '', 204
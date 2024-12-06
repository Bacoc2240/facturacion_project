from flask import render_template, request, redirect, url_for, flash
from src.models import session  # Usar la sesión global
from src.models.cliente import Cliente
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required, check_permission

class ClientesController(FlaskController):
    def __init__(self):
        super().__init__()

    @route('/', methods=['GET'])
    @login_required
    @check_permission('read')
    def index(self):
        clientes = session.query(Cliente).all()  # Usar session en lugar de db.session
        return render_template('clientes.html', clientes=clientes)




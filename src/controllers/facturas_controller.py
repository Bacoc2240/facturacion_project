from flask import render_template
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required
from src.models.factura import Factura

class FacturasController(FlaskController):
    def __init__(self):
        super().__init__()

    @route('/', methods=['GET'])
    @login_required
    def index(self):
        return render_template('facturas.html')


    
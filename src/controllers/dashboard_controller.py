from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required
from flask import render_template
from flask import session as flask_session

class DashboardController(FlaskController):
    
    @route('/', methods=['GET'])
    @login_required
    def index(self):
        print("Accediendo al dashboard")  # Log de acceso
        print("Sesión actual:", dict(flask_session))  # Log de sesión en dashboard
        return render_template('dashboard.html')

'''from flask import render_template
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required

class DashboardController(FlaskController):
    def __init__(self):
        super().__init__()

    @route('/', methods=['GET'])
    @login_required
    def index(self):
        return render_template('dashboard.html')'''


from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from functools import wraps
from src.models import Base, engine
from src.models.productos import Productos
from src.models.categorias import Categorias
from src.models.cliente import Cliente
from src.models.detalle_factura import DetalleFactura
from src.models.empleado import Empleado
from src.models.factura import Factura
from src.models.metodo_de_pago import MetodoDePago
from src.models.promocion import Promocion
from src.models.resolucion_dian import ResolucionDIAN
from src.models.transaccion import Transaccion
from src.models.usuario import Usuario

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')


Base.metadata.create_all(engine)

# Configur una clave para la sesión (Debo cambiarla en producción)
app.secret_key = 'miadsof'
app.debug = True

# verificar si el usuario está logueado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Lógica de autenticación (Debo mejorarla en producción)
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciales inválidas')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/dashboard')
@login_required
def dashboard(): 
    return render_template('dashboard.html')

@app.route('/productos')
@login_required
def productos(): 
    return render_template('productos.html')

@app.route('/clientes')
@login_required
def clientes(): 
    return render_template('clientes.html')

@app.route('/empleados')
@login_required
def empleados(): 
    return render_template('empleados.html')

@app.route('/facturas')
@login_required
def facturas(): 
    return render_template('facturas.html')

@app.route('/transacciones')
@login_required
def transacciones(): 
    return render_template('transacciones.html')

if __name__ == '__main__':
    app.run(debug=True)
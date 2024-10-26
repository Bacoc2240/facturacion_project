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

app = Flask(__name__, static_folder='static', template_folder='templates')
Base.metadata.create_all(engine)
app.secret_key = 'miadsof'
app.debug = True

# Definición de roles y permisos
ROLES = {
    'admin': ['read', 'write', 'delete', 'suspend'],
    'vendedor': ['read', 'write'],
    'inventario': ['read', 'write', 'suspend'],
    'visualizador': ['read']
}

def check_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session:
                return jsonify({'error': 'No autorizado'}), 401
            
            user_role = session['user_role']
            if user_role not in ROLES or permission not in ROLES[user_role]:
                return jsonify({'error': 'Permiso denegado'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
        
        # Consultar el usuario en la base de datos
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):  
            session['logged_in'] = True
            session['user_id'] = user.id
            session['user_role'] = user.rol  # Asumiendo que tienes un campo rol en tu modelo Usuario
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciales inválidas')
            
    return render_template('login.html')

@app.route('/productos', methods=['GET'])
@login_required
@check_permission('read')
def productos():
    productos = Productos.obtener_productos()
    return render_template('productos.html', productos=productos)

@app.route('/api/productos', methods=['GET'])
@login_required
@check_permission('read')
def get_productos():
    productos = Productos.obtener_productos()
    return jsonify([{
        'id': p.id,
        'codigo_barras': p.codigo_barras,
        'nombre': p.nombre,
        'genero': p.genero,
        'descripcion': p.descripcion,
        'stock': p.stock,
        'precio': p.precio,
        'categoria': p.categoria.nombre
    } for p in productos])

@app.route('/api/productos', methods=['POST'])
@login_required
@check_permission('write')
def crear_producto():
    try:
        datos = request.get_json()
        producto = Productos.crear_producto(datos, session['user_id'])
        return jsonify({
            'message': 'Producto creado exitosamente',
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre
            }
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Error al crear el producto'}), 500

@app.route('/api/productos/<int:id>', methods=['PUT'])
@login_required
@check_permission('write')
def actualizar_producto(id):
    try:
        producto = Productos.query.get_or_404(id)
        datos = request.get_json()
        producto.actualizar(datos, session['user_id'])
        return jsonify({'message': 'Producto actualizado exitosamente'})
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el producto'}), 500

@app.route('/api/productos/<int:id>/suspender', methods=['POST'])
@login_required
@check_permission('suspend')
def suspender_producto(id):
    try:
        producto = Productos.query.get_or_404(id)
        producto.suspender(session['user_id'])
        return jsonify({'message': 'Producto suspendido exitosamente'})
    except Exception as e:
        return jsonify({'error': 'Error al suspender el producto'}), 500

@app.route('/api/productos/<int:id>/reactivar', methods=['POST'])
@login_required
@check_permission('suspend')
def reactivar_producto(id):
    try:
        producto = Productos.query.get_or_404(id)
        producto.reactivar(session['user_id'])
        return jsonify({'message': 'Producto reactivado exitosamente'})
    except Exception as e:
        return jsonify({'error': 'Error al reactivar el producto'}), 500

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


"""@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/dashboard')
@login_required
def dashboard(): 
    return render_template('dashboard.html')

@app.route('/productos')
@login_required
def productos():
    # Llama a la función para obtener los productos
    productos = Productos.obtener_productos()
    
    # Envía los productos al template 'productos.html'
    return render_template('productos.html', productos=productos) 
    

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
    return render_template('transacciones.html')"""


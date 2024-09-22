from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from functools import wraps

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')

# Configur una clave para la sesión (Debo cambiarla en producción)
app.secret_key = 'tu_clave_secreta_aqui'

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
from flask import Flask, render_template, request, redirect, url_for, jsonify #Importa la clase Flask de flask (librería)

app = Flask(__name__) #Creamos una app instanciando la clase Flask 

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/') #Decoramos con método de app que es una instancia de la clase Flask y argumentamos "slash"
def login(): #Definimos una función llamada Inicio
    return render_template('login.html') #Retorno de la función

@app.route('/dashboard') 
def dashboard(): 
    return render_template('dashboard.html') 

@app.route('/productos') 
def productos(): 
    return render_template('productos.html') 

@app.route('/clientes') 
def clientes(): 
    return render_template('clientes.html') 

@app.route('/empleados') 
def empleados(): 
    return render_template('empleados.html') 

@app.route('/facturas') 
def facturas(): 
    return render_template('facturas.html') 

@app.route('/transacciones') 
def transacciones(): 
    return render_template('transacciones.html') 


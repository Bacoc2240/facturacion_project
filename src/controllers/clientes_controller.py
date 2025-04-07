from datetime import date
from flask import render_template, jsonify, request, url_for, redirect, flash
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required, check_permission
from src.models.cliente import Cliente
from src.models import session

class ClientesController(FlaskController):
    def __init__(self):
        super().__init__()
        # prefijo para todas las rutas de este controlador
        self.url_prefix = '/clientes'

     # Ruta principal que renderiza la plantilla
    @route('/')
    @login_required
    def index(self):
        try:
            clientes = session.query(Cliente).filter_by(activo=True).all()
            return render_template('clientes.html', 
                                clientes=clientes,
                                titulo='Listado de Clientes')
        except Exception as e:
            print(f"Error al cargar clientes: {str(e)}")
            return render_template('clientes.html', 
                                clientes=[],
                                titulo='Listado de Clientes',
                                error=str(e))

    # API endpoints
    @route('/api/lista')
    @login_required
    def obtener_lista_clientes(self):
        try:
            print("Accediendo a /api/lista")  # Debug log
            clientes = session.query(Cliente).filter_by(activo=True).all()
            
            # Para cada cliente, actualizar las preferencias si no están definidas
            for cliente in clientes:
                if not hasattr(cliente, 'preferencias') or not cliente.preferencias:
                    if cliente.historial_compras:
                        cliente.obtener_producto_preferido()
            
            clientes_json = [{
                'id_cliente': c.id_cliente,
                'tipo_documento': c.tipo_documento,
                'nombre_cliente': c.nombre_cliente,
                'direccion': c.direccion,
                'telefono': c.telefono,
                'correo_electronico': c.correo_electronico,
                'historial_compras': c.historial_compras if c.historial_compras else "No aplica",
                'preferencias': c.preferencias if hasattr(c, 'preferencias') and c.preferencias else "No aplica",
                'activo': c.activo
            } for c in clientes]
            
            return jsonify(clientes_json)
        except Exception as e:
            print(f"Error en obtener_lista_clientes: {str(e)}")  # Debug log
            return jsonify({'error': str(e)}), 500

    @route('/api/clientes/crear', methods=['POST'])
    @login_required
    @check_permission('write')
    def crear_cliente(self):
        try:
            # Obtener y validar los datos JSON
            datos = request.get_json()
            if not datos:
                return jsonify({
                    'success': False,
                    'error': "No se recibieron datos"
                }), 400

            # Validar campos requeridos
            campos_requeridos = ['id_cliente', 'tipo_documento', 'nombre_cliente']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in datos]
            
            if campos_faltantes:
                return jsonify({
                    'success': False,
                    'error': f"Faltan los siguientes campos requeridos: {', '.join(campos_faltantes)}"
                }), 400

            try:
                # Intentar crear el cliente
                nuevo_cliente = Cliente.agregar_cliente(
                    id_cliente=datos['id_cliente'],
                    tipo_documento=datos['tipo_documento'],
                    nombre_cliente=datos['nombre_cliente'],
                    direccion=datos.get('direccion'),
                    telefono=datos.get('telefono'),
                    correo_electronico=datos.get('correo_electronico'),
                    historial_compras=datos.get('historial_compras')
                )

                # Si el cliente se creó exitosamente
                if nuevo_cliente:
                    return jsonify({
                        'success': True,
                        'message': 'Cliente creado exitosamente',
                        'cliente': {
                            'id_cliente': nuevo_cliente.id_cliente,
                            'nombre_cliente': nuevo_cliente.nombre_cliente,
                            'tipo_documento': nuevo_cliente.tipo_documento,
                            'preferencias': nuevo_cliente.preferencias if hasattr(nuevo_cliente, 'preferencias') else "No aplica"
                        }
                    }), 201
                else:
                    return jsonify({
                        'success': False,
                        'error': "No se pudo crear el cliente"
                    }), 500

            except ValueError as ve:
                # Manejar errores de validación
                return jsonify({
                    'success': False,
                    'error': str(ve)
                }), 400

        except Exception as e:
            # Manejar errores inesperados
            print(f"Error no esperado al crear cliente: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error al procesar la solicitud: {str(e)}"
            }), 500
    
    @route('/api/clientes/<string:id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_cliente(self, id):
        try:
            cliente = session.query(Cliente).get(id)
            if not cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 404

            # Asegurar que las preferencias estén actualizadas
            if hasattr(cliente, 'obtener_producto_preferido') and cliente.historial_compras:
                if not hasattr(cliente, 'preferencias') or not cliente.preferencias or cliente.preferencias == "No aplica":
                    cliente.obtener_producto_preferido()

            return jsonify({
                'id_cliente': cliente.id_cliente,
                'tipo_documento': cliente.tipo_documento,
                'nombre_cliente': cliente.nombre_cliente,
                'telefono': cliente.telefono,
                'correo_electronico': cliente.correo_electronico,
                'historial_compras': cliente.historial_compras if cliente.historial_compras else "No aplica",
                'preferencias': cliente.preferencias if hasattr(cliente, 'preferencias') and cliente.preferencias else "No aplica"
            })
        except Exception as e:
            print(f"Error al obtener cliente: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @route('/api/clientes/<string:id>', methods=['PUT'])
    @login_required
    @check_permission('write')
    def actualizar_cliente(self, id):
        try:
            cliente = session.query(Cliente).get(id)
            if not cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 404

            datos = request.get_json()
            print(f"Datos recibidos para actualización: {datos}")  # Debug log

            # Actualizar datos del cliente
            if 'nombre_cliente' in datos:
                cliente.nombre_cliente = datos['nombre_cliente']
            if 'telefono' in datos:
                cliente.telefono = datos['telefono']
            if 'correo_electronico' in datos:
                cliente.correo_electronico = datos['correo_electronico']
            if 'historial_compras' in datos:
                cliente.historial_compras = datos['historial_compras']
                # Actualizar preferencias si se modifica el historial
                if hasattr(cliente, 'obtener_producto_preferido'):
                    cliente.obtener_producto_preferido()

            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Cliente actualizado exitosamente',
                'cliente': {
                    'id_cliente': cliente.id_cliente,
                    'tipo_documento': cliente.tipo_documento,
                    'nombre_cliente': cliente.nombre_cliente,
                    'telefono': cliente.telefono,
                    'correo_electronico': cliente.correo_electronico,
                    'historial_compras': cliente.historial_compras if cliente.historial_compras else "No aplica",
                    'preferencias': cliente.preferencias if hasattr(cliente, 'preferencias') else "No aplica"
                }
            })
            
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar cliente: {str(e)}")  # Debug log
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @route('/api/clientes/<string:id>/desactivar', methods=['POST'])
    @login_required
    @check_permission('write')
    def desactivar_cliente(self, id):
        try:
            cliente = session.query(Cliente).get(id)
            if not cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 404

            cliente.activo = False
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Cliente desactivado exitosamente'
            })
            
        except Exception as e:
            session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @route('/logout', methods=['GET'])
    def logout(self):
        # Limpiar la sesión
        session.clear()
        # Redirigir al login
        return redirect(url_for('auth.login'))
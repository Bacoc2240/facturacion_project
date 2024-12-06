from flask import jsonify, request, render_template, flash, redirect, url_for, session as flask_session, make_response
from src.models import session  # Usar la sesión global
import json
from src.models.productos import Productos
from src.models.usuario import Usuario
from src.models.categorias import Categorias
from src.models.decorators import login_required, check_permission
from src.controllers.base_controller import FlaskController, route


class ProductosController(FlaskController):
    def __init__(self):
        super().__init__()

    @route('/api/lista', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_lista_productos(self):
        """
        Endpoint específico que solo devuelve datos JSON de productos.
        Este endpoint está separado de la vista principal.
        """
        try:
            productos = Productos.obtener_productos(session)
            productos_json = [{
                'id': p.id,
                'codigo_barras': p.codigo_barras,
                'nombre': p.nombre,
                'genero': p.genero,
                'descripcion': p.descripcion,
                'stock': p.stock,
                'precio': float(p.precio),
                'categoria': p.categoria.categoria if p.categoria else None,
                'activo': p.activo
            } for p in productos]
            
            return jsonify(productos_json)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # El método index 
    @route('/', methods=['GET'])
    @login_required
    @check_permission('read')
    def index(self):
        try:
            productos = Productos.obtener_productos(session)
            for producto in productos:
                producto.precio = float(producto.precio)
            return render_template(
                'productos.html',
                productos=productos,
                controller=self.controller_name
            )
        except Exception as e:
            flash(f'Error al cargar productos: {str(e)}', 'danger')
            return redirect(url_for(self.get_endpoint('index')))
        
    @route('/crear', methods=['POST'])
    @login_required
    @check_permission('write')
    def crear_producto(self):
        try:
            datos = request.form.to_dict()
            print(f"Datos recibidos del formulario: {datos}")
            
            # Obtener la categoría
            categoria_nombre = datos.get('categoria')
            print(f"Buscando categoría: '{categoria_nombre}'")
            
            if not categoria_nombre:
                return jsonify({
                    'success': False,
                    'error': "Debe seleccionar una categoría"
                }), 400
            
            # Consulta a la tabla categorias
            categoria = session.query(Categorias).filter(
                Categorias.categoria == categoria_nombre
            ).first()
            
            if not categoria:
                return jsonify({
                    'success': False,
                    'error': f"Categoría '{categoria_nombre}' no encontrada"
                }), 400
            
            # Añadir el ID de la categoría a los datos
            datos['categoria_id'] = categoria.id
            
            # Validar datos obligatorios
            campos_requeridos = ['nombre', 'precio', 'descripcion', 'categoria_id']
            for campo in campos_requeridos:
                if not datos.get(campo):
                    return jsonify({
                        'success': False,
                        'error': f"El campo {campo} es obligatorio"
                    }), 400
            
            # Convertir tipos de datos
            try:
                datos['precio'] = float(datos['precio'])
                datos['stock'] = int(datos['stock']) if datos.get('stock') else 0
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': "Error en el formato de precio o stock"
                }), 400
            
            # Generar el código de barras
            codigo_barras = Productos.generar_codigo_barras(session)
            datos['codigo_barras'] = codigo_barras
            
            # Crear el producto
            producto = Productos.crear_producto(datos, flask_session['user_id'], session)
            
            # Devolver respuesta JSON exitosa
            return jsonify({
                'success': True,
                'message': 'Producto creado exitosamente',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'categoria': categoria_nombre,
                    'stock': producto.stock,
                    'genero': producto.genero,
                    'precio': float(producto.precio),
                    'descripcion': producto.descripcion,
                    'codigo_barras': producto.codigo_barras,
                    'activo': producto.activo
                }
            }), 200
            
        except Exception as e:
            print(f"Error no esperado: {str(e)}")  # Para debugging
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @route('/', methods=['GET'])
    @login_required
    @check_permission('read')
    def index(self):
        productos = Productos.obtener_productos(session)
        return render_template('productos.html', productos=productos)

    @route('/<int:id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_producto(self, id):
        try:
            producto = session.query(Productos).get(id)
            if not producto:
                return jsonify({'error': 'Producto no encontrado'}), 404
                
            return jsonify({
                'id': producto.id,
                'nombre': producto.nombre,
                'categoria': producto.categoria.categoria if producto.categoria else None,
                'genero': producto.genero,
                'descripcion': producto.descripcion,
                'stock': producto.stock,
                'precio': float(producto.precio),
                'activo': producto.activo
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @route('/<int:id>/editar', methods=['POST'])
    @login_required
    @check_permission('write')
    def editar_producto(self, id):
        try:
            print(f"Recibiendo solicitud de edición para producto {id}")
            print("Datos recibidos:", request.form.to_dict())
            producto = session.query(Productos).get(id)
            if not producto:
                print(f"Producto {id} no encontrado")
                return jsonify({'error': 'Producto no encontrado'}), 404

            datos = request.form.to_dict()
            print("Datos a actualizar:", datos)
            # Manejo de la categoría
            if 'categoria' in datos:
                categoria = session.query(Categorias).filter_by(categoria=datos['categoria']).first()
                if categoria:
                    datos['categoria_id'] = categoria.id
                    del datos['categoria']

            # Convertir tipos de datos
            if 'precio' in datos:
                datos['precio'] = round(float(datos['precio']), 2)
            if 'stock' in datos:
                datos['stock'] = int(datos['stock'])

            # Actualizar el producto
            producto.actualizar(datos, flask_session['user_id'])
            session.commit()

            # Devolver datos actualizados completos
            print("Producto actualizado exitosamente")
            return jsonify({
                'message': 'Producto actualizado exitosamente',
                'producto': {
                    'id': producto.id,
                    'codigo_barras': producto.codigo_barras,
                    'nombre': producto.nombre,
                    'categoria': producto.categoria.categoria if producto.categoria else None,
                    'genero': producto.genero,
                    'descripcion': producto.descripcion,
                    'stock': producto.stock,
                    'precio': float(producto.precio),
                    'activo': producto.activo
                }
            })
        
        except ValueError as e:
            print(f"Error en la actualización: {str(e)}")
            session.rollback()
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 500

    @route('/<int:id>/suspender', methods=['POST'])
    @login_required
    @check_permission('suspend')
    def suspender_producto(self, id):
        try:
            producto = session.query(Productos).get(id)
            if not producto:
                raise ValueError("Producto no encontrado")
            
            producto.suspender(flask_session['user_id'])
            session.commit()
            flash('Producto suspendido exitosamente', 'success')
        except Exception as e:
            session.rollback()
            flash(f'Error al suspender el producto: {str(e)}', 'danger')
        finally:
            session.close()

        return redirect(url_for('productos.index'))
    
    @route('/suspendidos', methods=['GET'])
    @login_required
    @check_permission('read')
    def listar_suspendidos(self):
        try:
            user_id = flask_session.get('user_id')
            current_user = session.query(Usuario).get(user_id)
            
            print(f"Usuario ID: {user_id}")
            print(f"Rol del usuario: {current_user.rol}")
            print(f"Permisos del usuario: {current_user.get_permissions()}")
            
            has_read = current_user.has_permission('read')
            print(f"¿Tiene permiso de lectura?: {has_read}")

            if not current_user or not has_read:
                return jsonify({
                    'error': 'No tienes los permisos necesarios para ver esta información',
                    'required_permission': 'read',
                    'user_permissions': current_user.get_permissions() if current_user else []
                }), 403

            query = session.query(Productos).filter(Productos.activo == False)

            if request.args.get('nombre'):
                query = query.filter(Productos.nombre.ilike(f"%{request.args.get('nombre')}%"))
            
            if request.args.get('genero'):
                query = query.filter(Productos.genero == request.args.get('genero'))
                
            if request.args.get('categoria'):
                query = query.filter(Productos.categoria == request.args.get('categoria'))

            productos = query.all()
            
            # Serialización manual de los productos
            productos_json = []
            for p in productos:
                producto_dict = {
                    'id': p.id,
                    'codigo_barras': p.codigo_barras,
                    'nombre': p.nombre,
                    'genero': p.genero,
                    'descripcion': p.descripcion,
                    'stock': p.stock,
                    'precio': str(p.precio) if p.precio is not None else '0.00',  # Convertimos Decimal a string
                    'categoria': p.categoria.nombre if hasattr(p.categoria, 'nombre') else str(p.categoria),  # Manejamos el objeto categoria
                    'activo': p.activo
                }
                productos_json.append(producto_dict)

            print(f"Productos serializados exitosamente: {len(productos_json)}")
            return jsonify(productos_json)

        except Exception as e:
            print(f"Error en listar_suspendidos: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            session.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()


    @route('/<int:id>/reactivar', methods=['POST'])
    @login_required
    @check_permission('suspend')
    def reactivar_producto(self, id):
        try:
            producto = session.query(Productos).get(id)
            if not producto:
                raise ValueError("Producto no encontrado")
            
            producto.reactivar(flask_session['user_id'])
            session.commit()
            flash('Producto reactivado exitosamente', 'success')
        except Exception as e:
            session.rollback()
            flash(f'Error al reactivar el producto: {str(e)}', 'danger')
        finally:
            session.close()

        return redirect(url_for('productos.index'))

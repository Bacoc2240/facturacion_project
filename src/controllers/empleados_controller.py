from datetime import date
from flask import render_template, jsonify, request, url_for, redirect, session as flask_session, flash
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required, check_permission
from src.models.usuario import Usuario
from src.models.empleado import Empleado
from src.models import session


class EmpleadosController(FlaskController):
    def __init__(self):
        super().__init__()

    # Esta es la ruta principal
    @route('/empleados', methods=['GET'])
    @login_required
    def index(self):
        try:
            empleados = session.query(Empleado).filter_by(activo=True).all()
            return render_template('empleados.html', 
                                empleados=empleados,
                                titulo='Listado de Empleados')
        except Exception as e:
            print(f"Error al cargar empleados: {str(e)}")
            return render_template('empleados.html', 
                                empleados=[],
                                titulo='Listado de Empleados',
                                error=str(e))

    # Rutas de la API para las operaciones CRUD
    @route('/api/lista', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_lista_empleados(self):
        try:
            empleados = session.query(Empleado).filter_by(activo=True).all()
            empleados_json = [{
                'id_empleado': e.id_empleado,
                'nombre_apellidos': e.nombre_apellidos,
                'numero_identificacion': e.numero_identificacion,
                'correo_electronico': e.correo_electronico,
                'telefono': e.telefono,
                'cargo': e.cargo,
                'fecha_contratacion': e.fecha_contratacion.isoformat() if e.fecha_contratacion else None,
                'activo': e.activo
            } for e in empleados]
            
            return jsonify(empleados_json)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @route('/crear', methods=['POST'])
    @login_required
    @check_permission('write')
    def crear_empleado(self):
        try:
            datos = request.form.to_dict()
            print(f"Datos recibidos del formulario: {datos}")
            
            # Validar campos obligatorios
            campos_requeridos = [
                'nombre_apellidos', 
                'numero_identificacion',
                'correo_electronico', 
                'telefono', 
                'fecha_contratacion',
                'cargo'
            ]
            
            for campo in campos_requeridos:
                if not datos.get(campo):
                    return jsonify({
                        'success': False,
                        'error': f"El campo {campo} es obligatorio"
                    }), 400
            
            try:
                # Convertir la fecha de string a objeto date
                fecha_contratacion = date.fromisoformat(datos['fecha_contratacion'])
                
                # Usar el método estático existente para crear/activar empleado
                nuevo_empleado = Empleado.agregar_o_activar_empleado(
                    nombre_apellidos=datos['nombre_apellidos'],
                    correo_electronico=datos['correo_electronico'],
                    telefono=datos['telefono'],
                    fecha_contratacion=fecha_contratacion,
                    cargo=datos['cargo'],
                    numero_identificacion=datos['numero_identificacion']
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Empleado creado exitosamente',
                    'empleado': {
                        'id_empleado': nuevo_empleado.id_empleado,
                        'nombre_apellidos': nuevo_empleado.nombre_apellidos,
                        'numero_identificacion': nuevo_empleado.numero_identificacion,
                        'correo_electronico': nuevo_empleado.correo_electronico,
                        'telefono': nuevo_empleado.telefono,
                        'cargo': nuevo_empleado.cargo,
                        'fecha_contratacion': nuevo_empleado.fecha_contratacion.isoformat(),
                        'activo': nuevo_empleado.activo
                    }
                }), 200
                
            except ValueError as ve:
                return jsonify({
                    'success': False,
                    'error': str(ve)
                }), 400
                
        except Exception as e:
            print(f"Error no esperado: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error al procesar la solicitud: {str(e)}"
            }), 500
            
    @route('/<int:id>', methods=['GET'])  # Esta se convertirá en /empleados/<id>
    @login_required
    @check_permission('read')
    def obtener_empleado(self, id):
        try:
            empleado = session.query(Empleado).get(id)
            if not empleado:
                return jsonify({'error': 'Empleado no encontrado'}), 404
                
            return jsonify({
                'id_empleado': empleado.id_empleado,
                'nombre_apellidos': empleado.nombre_apellidos,
                'numero_identificacion': empleado.numero_identificacion,
                'correo_electronico': empleado.correo_electronico,
                'telefono': empleado.telefono,
                'cargo': empleado.cargo,
                'fecha_contratacion': empleado.fecha_contratacion.isoformat() if empleado.fecha_contratacion else None,
                'activo': empleado.activo
            })
        except Exception as e:
            print(f"Error al obtener empleado: {str(e)}")  # Añadir log
            return jsonify({'error': str(e)}), 500
        
    @route('/<int:id>/editar', methods=['POST'])  # Esta se convertirá en /empleados/<id>/editar
    @login_required
    @check_permission('write')
    def editar_empleado(self, id):
        try:
            empleado = session.query(Empleado).get(id)
            if not empleado:
                return jsonify({'error': 'Empleado no encontrado'}), 404

            datos = request.form.to_dict()
            
            # Convertir la fecha de contratación
            if 'fecha_contratacion' in datos:
                datos['fecha_contratacion'] = date.fromisoformat(datos['fecha_contratacion'])

            # Actualizar empleado
            for key, value in datos.items():
                if hasattr(empleado, key):
                    setattr(empleado, key, value)

            session.commit()

            return jsonify({
                'success': True,
                'message': 'Empleado actualizado exitosamente',
                'empleado': {
                    'id_empleado': empleado.id_empleado,
                    'nombre_apellidos': empleado.nombre_apellidos,
                    'numero_identificacion': empleado.numero_identificacion,
                    'correo_electronico': empleado.correo_electronico,
                    'telefono': empleado.telefono,
                    'cargo': empleado.cargo,
                    'fecha_contratacion': empleado.fecha_contratacion.isoformat() if empleado.fecha_contratacion else None,
                    'activo': empleado.activo
                }
            })
        
        except ValueError as e:
            session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @route('/<int:id>/suspender', methods=['POST'])
    @login_required
    @check_permission('suspend')
    def suspender_empleado(self, id):  # Cambiar nombre de la función
        try:
            empleado = session.query(Empleado).get(id)
            if not empleado:
                return jsonify({
                    'success': False,
                    'error': "Empleado no encontrado"
                }), 404
            
            empleado.activo = False  # Marcar como inactivo
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Empleado suspendido exitosamente'
            })
            
        except Exception as e:
            session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        finally:
            session.close()
    
    @route('/suspendidos', methods=['GET'])
    @login_required
    @check_permission('read')
    def listar_suspendidos(self):
        try:
            # Verificación de permisos del usuario
            user_id = flask_session.get('user_id')
            current_user = session.query(Usuario).get(user_id)
            
            # Logging para debug
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

            # Consulta base para empleados inactivos
            query = session.query(Empleado).filter(Empleado.activo == False)

            # Aplicar filtros si existen en la solicitud
            if request.args.get('nombre'):
                query = query.filter(Empleado.nombre_apellidos.ilike(
                    f"%{request.args.get('nombre')}%"))
            
            if request.args.get('cargo'):
                query = query.filter(Empleado.cargo == request.args.get('cargo'))
            
            if request.args.get('identificacion'):
                query = query.filter(Empleado.numero_identificacion.ilike(
                    f"%{request.args.get('identificacion')}%"))

            empleados = query.all()
            
            # Serialización manual de los empleados
            empleados_json = []
            for e in empleados:
                empleado_dict = {
                    'id_empleado': e.id_empleado,
                    'nombre_apellidos': e.nombre_apellidos,
                    'numero_identificacion': e.numero_identificacion,
                    'correo_electronico': e.correo_electronico,
                    'telefono': e.telefono,
                    'cargo': e.cargo,
                    'fecha_contratacion': e.fecha_contratacion.strftime('%Y-%m-%d') if e.fecha_contratacion else None,
                    'activo': e.activo
                }
                empleados_json.append(empleado_dict)

            print(f"Empleados serializados exitosamente: {len(empleados_json)}")
            return jsonify(empleados_json)

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
    def reactivar_empleado(self, id):
        try:
            empleado = session.query(Empleado).get(id)
            if not empleado:
                raise ValueError("Empleado no encontrado")
            
            empleado.fecha_activacion = date.today()
            empleado.activo = True
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Empleado reactivado exitosamente'
            })
        except Exception as e:
            session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        finally:
            session.close()    
    
    @route('/logout', methods=['GET'])
    def logout(self):
        # Limpiar la sesión
        session.clear()
        # Redirigir al login
        return redirect(url_for('auth.login'))
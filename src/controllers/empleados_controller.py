from flask import render_template, jsonify, request, url_for, redirect
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required, check_permission
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
        """
        Endpoint específico que solo devuelve datos JSON de empleados.
        Este endpoint está separado de la vista principal para una mejor organización.
        """
        try:
            # Obtener empleados activos de la base de datos
            empleados = session.query(Empleado).filter_by(activo=True).all()
            
            # Convertir los objetos empleado a formato JSON
            empleados_json = [{
                'id_empleado': e.id_empleado,
                'nombre_apellidos': e.nombre_apellidos,
                'numero_identificacion': e.numero_identificacion,
                'correo_electronico': e.correo_electronico,
                'telefono': e.telefono,
                'cargo': e.cargo,
                'fecha_contratacion': e.fecha_contratacion.strftime('%Y-%m-%d') if e.fecha_contratacion else None,
                'activo': e.activo
            } for e in empleados]
            
            return jsonify(empleados_json)
            
        except Exception as e:
            # En caso de error, devolver una respuesta JSON con el error
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
            
            # Verificar si el empleado ya existe
            empleado_existente = Empleado.verificar_empleado(datos['numero_identificacion'])
            if empleado_existente and empleado_existente.activo:
                return jsonify({
                    'success': False,
                    'error': "El empleado ya existe y está activo"
                }), 400
                
            try:
                # Usar el método estático existente para crear/activar empleado
                nuevo_empleado = Empleado.agregar_o_activar_empleado(
                    nombre_apellidos=datos['nombre_apellidos'],
                    correo_electronico=datos['correo_electronico'],
                    telefono=datos['telefono'],
                    fecha_contratacion=date.fromisoformat(datos['fecha_contratacion']),
                    cargo=datos['cargo'],
                    numero_identificacion=datos['numero_identificacion']
                )
                
                # Devolver respuesta JSON exitosa
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
            print(f"Error no esperado: {str(e)}")  # Para debugging
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
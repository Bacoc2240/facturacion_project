from flask import (
    render_template, jsonify, request, 
    redirect, url_for, flash
)
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required, check_permission
from src.models.resolucion_dian import ResolucionDIAN
from src.models import session
from datetime import datetime, date, timedelta
import traceback

class ResolucionDIANController(FlaskController):
    """
    Controlador para la gestión de resoluciones DIAN.
    Maneja todas las operaciones relacionadas con resoluciones DIAN incluyendo:
    - Visualización y listado de resoluciones
    - Creación y activación de resoluciones
    - Validación de resoluciones
    """

    def __init__(self):
        super().__init__()
        
        print("Controlador de Resoluciones DIAN inicializado. Las resoluciones deben crearse manualmente.")
        
    # ===============================
    # Rutas de Visualización
    # ===============================

    @route('/', methods=['GET'])
    @login_required
    def index(self):
        """Vista principal de resoluciones DIAN."""
        try:
            # Obtener resoluciones con sus relaciones
            resoluciones = session.query(ResolucionDIAN).all()
            
            # Determinar si hay una resolución activa
            resolucion_activa = session.query(ResolucionDIAN).filter_by(activa=True).first()

            return render_template(
                'resoluciones.html',
                resoluciones=resoluciones,
                hay_resolucion_activa=resolucion_activa is not None,
                titulo='Gestión de Resoluciones DIAN'
            )

        except Exception as e:
            self._limpiar_sesion()
            print(f"Error al cargar resoluciones: {str(e)}")
            return render_template(
                'resoluciones.html',
                resoluciones=[],
                hay_resolucion_activa=False,
                titulo='Gestión de Resoluciones DIAN',
                error=str(e)
            )

    # ===============================
    # API Endpoints
    # ===============================

    @route('/api/resoluciones/crear', methods=['POST'])
    @login_required
    @check_permission('write')
    def crear_resolucion_api(self):
        """Endpoint para crear una nueva resolución DIAN."""
        try:
            datos = request.get_json()

            # Validar datos requeridos
            if not self._validar_datos_resolucion(datos):
                return jsonify({
                    'success': False,
                    'error': 'Faltan datos requeridos o son inválidos'
                }), 400

            # Convertir fechas de string a date
            fecha_inicial = datetime.strptime(datos['fecha_inicial'], '%Y-%m-%d').date()
            fecha_final = datetime.strptime(datos['fecha_final'], '%Y-%m-%d').date()

            # Validar fechas
            if fecha_inicial > fecha_final:
                return jsonify({
                    'success': False,
                    'error': 'La fecha inicial debe ser anterior a la fecha final'
                }), 400

            # Validar rango de numeración
            if datos['rango_inicial'] >= datos['rango_final']:
                return jsonify({
                    'success': False,
                    'error': 'El rango inicial debe ser menor al rango final'
                }), 400

            # Si se solicita que esta resolución sea activa, desactivar las existentes
            if datos.get('activar', False):
                self._desactivar_resoluciones_existentes()

            # Crear la resolución
            nueva_resolucion = ResolucionDIAN(
                numero_resolucion=datos['numero_resolucion'],
                rango_inicial=datos['rango_inicial'],
                rango_final=datos['rango_final'],
                fecha_inicial=fecha_inicial,
                fecha_final=fecha_final
            )
            nueva_resolucion.activa = datos.get('activar', False)

            # Guardar los cambios
            session.add(nueva_resolucion)
            session.commit()

            return jsonify({
                'success': True,
                'message': 'Resolución DIAN creada exitosamente',
                'resolucion': self._formatear_resolucion(nueva_resolucion)
            }), 201

        except Exception as e:
            session.rollback()
            print(f"Error al crear resolución DIAN: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @route('/api/resoluciones/activar/<int:id_resolucion>', methods=['POST'])
    @login_required
    @check_permission('write')
    def activar_resolucion_api(self, id_resolucion):
        """Endpoint para activar una resolución DIAN específica."""
        try:
            # Buscar la resolución
            resolucion = session.query(ResolucionDIAN).get(id_resolucion)
            if not resolucion:
                return jsonify({
                    'success': False,
                    'error': 'Resolución no encontrada'
                }), 404

            # Verificar validez de la resolución
            if not resolucion.es_resolucion_valida():
                return jsonify({
                    'success': False,
                    'error': 'La resolución no está vigente'
                }), 400

            # Desactivar todas las resoluciones existentes
            self._desactivar_resoluciones_existentes()

            # Activar la resolución seleccionada
            resolucion.activa = True
            session.commit()

            return jsonify({
                'success': True,
                'message': 'Resolución DIAN activada exitosamente'
            })

        except Exception as e:
            session.rollback()
            print(f"Error al activar resolución DIAN: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @route('/api/resoluciones/lista', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_lista_resoluciones(self):
        """Endpoint para obtener la lista de resoluciones DIAN."""
        try:
            resoluciones = session.query(ResolucionDIAN).all()
            
            resoluciones_json = [self._formatear_resolucion(r) for r in resoluciones]
            
            return jsonify({
                'success': True,
                'resoluciones': resoluciones_json
            })

        except Exception as e:
            print(f"Error al obtener resoluciones: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @route('/api/resoluciones/activa', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_resolucion_activa(self):
        """Endpoint para obtener la resolución DIAN activa."""
        try:
            resolucion = session.query(ResolucionDIAN).filter_by(activa=True).first()
            
            if not resolucion:
                return jsonify({
                    'success': False,
                    'error': 'No hay resolución DIAN activa'
                }), 404
            
            return jsonify({
                'success': True,
                'resolucion': self._formatear_resolucion(resolucion)
            })

        except Exception as e:
            print(f"Error al obtener resolución activa: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # ===============================
    # Métodos Auxiliares
    # ===============================

    def _limpiar_sesion(self):
        """Método interno para limpiar el estado de la sesión."""
        try:
            if hasattr(session, 'is_active') and session.is_active:
                session.rollback()
        except Exception as e:
            print(f"Error al limpiar sesión: {str(e)}")
            try:
                session.remove()
            except:
                pass

    def _validar_datos_resolucion(self, datos):
        """Valida que estén todos los datos requeridos para crear una resolución DIAN."""
        campos_requeridos = [
            'numero_resolucion', 'rango_inicial', 'rango_final', 
            'fecha_inicial', 'fecha_final'
        ]
        
        # Verificar que todos los campos requeridos estén presentes
        if not all(key in datos for key in campos_requeridos):
            return False
        
        # Verificar que los tipos de datos sean correctos
        try:
            int(datos['rango_inicial'])
            int(datos['rango_final'])
            datetime.strptime(datos['fecha_inicial'], '%Y-%m-%d')
            datetime.strptime(datos['fecha_final'], '%Y-%m-%d')
        except (ValueError, TypeError):
            return False
        
        return True

    def _desactivar_resoluciones_existentes(self):
        """Desactiva todas las resoluciones DIAN existentes."""
        session.query(ResolucionDIAN).update({'activa': False})

    def _formatear_resolucion(self, resolucion):
        """Formatea los datos de una resolución DIAN para la respuesta JSON."""
        return {
            'id': resolucion.id_resolucion,
            'numero_resolucion': resolucion.numero_resolucion,
            'rango_inicial': resolucion.rango_inicial,
            'rango_final': resolucion.rango_final,
            'fecha_inicial': resolucion.fecha_inicial.isoformat() if resolucion.fecha_inicial else None,
            'fecha_final': resolucion.fecha_final.isoformat() if resolucion.fecha_final else None,
            'numero_actual': resolucion.numero_actual,
            'activa': resolucion.activa,
            'vigente': resolucion.es_resolucion_valida()
        }
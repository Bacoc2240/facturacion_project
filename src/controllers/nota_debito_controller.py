import os
import json
from datetime import date, datetime
from flask import (
    render_template, jsonify, request, url_for, 
    redirect, session as flask_session, flash, send_file
)
from sqlalchemy.orm import joinedload
from src.controllers.base_controller import FlaskController, route
from src.models.decorators import login_required, check_permission
from src.models.factura import Factura
from src.models.empleado import Empleado 
from src.models.cliente import Cliente
from src.models.productos import Productos
from src.models.detalle_factura import DetalleFactura
from src.models.nota_debito import NotaDebito, DetalleNotaDebito  # Suponemos que existen estos modelos
from src.models import session
from sqlalchemy import or_, and_, func
import logging
import config

class NotaDebitoController(FlaskController):
    """
    Controlador para la gestión de notas débito.
    Maneja todas las operaciones relacionadas con notas débito incluyendo:
    - Creación y visualización de notas débito
    - Obtención de notas débito asociadas a facturas
    - Generación de informes
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
    # ===============================
    # Rutas de Visualización
    # ===============================

    @route('/', methods=['GET'])
    @login_required
    @check_permission('read')
    def index(self):
        """Vista principal de notas débito"""
        try:
            # Obtener listado de notas débito
            notas_debito = session.query(NotaDebito)\
                .join(NotaDebito.factura)\
                .order_by(NotaDebito.fecha_emision.desc())\
                .all()
                
            return render_template(
                'notas_debito/index.html',
                notas_debito=notas_debito,
                titulo='Gestión de Notas Débito'
            )
        except Exception as e:
            self.logger.error(f"Error al cargar notas débito: {str(e)}")
            flash(f"Error al cargar notas débito: {str(e)}", "error")
            return render_template(
                'notas_debito/index.html',
                notas_debito=[],
                titulo='Gestión de Notas Débito',
                error=str(e)
            )
            
    @route('/ver/<int:nota_id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def ver_nota_debito(self, nota_id):
        """Muestra los detalles de una nota débito específica"""
        try:
            # Obtener la nota débito con sus relaciones
            nota = session.query(NotaDebito)\
                .filter(NotaDebito.id == nota_id)\
                .first()
                
            if not nota:
                flash('Nota débito no encontrada', 'danger')
                return redirect(url_for('notas_debito.index'))
                
            # Obtener detalles de la nota débito
            detalles = session.query(DetalleNotaDebito)\
                .filter(DetalleNotaDebito.id_nota_debito == nota_id)\
                .all()
                
            # Obtener la factura asociada
            factura = session.query(Factura).get(nota.factura_id)
            
            # Obtener cliente
            cliente = None
            if factura:
                cliente = session.query(Cliente).get(factura.id_cliente)
                
            # Determinar si se debe mostrar para impresión
            imprimir = request.args.get('print', 'false').lower() == 'true'
                
            return render_template(
                'notas_debito/ver.html',
                nota=nota,
                detalles=detalles,
                factura=factura,
                cliente=cliente,
                imprimir=imprimir,
                titulo=f'Nota Débito #{nota.numero}'
            )
        except Exception as e:
            self.logger.error(f"Error al mostrar nota débito: {str(e)}")
            flash(f"Error al mostrar nota débito: {str(e)}", "error")
            return redirect(url_for('notas_debito.index'))
    
    # ===============================
    # API Endpoints
    # ===============================

    @route('/api/notas-debito/siguiente-numero', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_siguiente_numero(self):
        """Endpoint para obtener el siguiente número de nota débito disponible"""
        try:
            # Obtener la última nota débito
            ultima_nota = session.query(NotaDebito)\
                .order_by(NotaDebito.numero.desc())\
                .first()
                
            # Si no hay notas, empezar desde 1
            if not ultima_nota:
                siguiente_numero = 1
            else:
                siguiente_numero = ultima_nota.numero + 1
                
            return jsonify({
                'success': True,
                'numero': siguiente_numero
            })
        except Exception as e:
            self.logger.error(f"Error al obtener siguiente número de nota débito: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/api/notas-debito', methods=['POST'])
    @login_required
    @check_permission('write')
    def crear_nota_debito(self):
        """Endpoint para crear una nueva nota débito"""
        try:
            # Obtener datos del formulario
            datos = request.form
            
            # Procesar archivo adjunto si existe
            archivo_soporte = None
            if 'archivo_soporte' in request.files:
                archivo = request.files['archivo_soporte']
                if archivo.filename:
                    # Guardar el archivo en una ubicación temporal o permanente
                    # y almacenar la ruta en archivo_soporte
                    archivo_soporte = self._guardar_archivo_soporte(archivo)
            
            # Validar datos requeridos
            if not datos.get('factura_id') or not datos.get('concepto'):
                return jsonify({
                    'success': False,
                    'error': 'Faltan datos requeridos (factura_id, concepto)'
                }), 400
                
            # Validar que la factura exista
            factura = session.query(Factura).get(datos.get('factura_id'))
            if not factura:
                return jsonify({
                    'success': False,
                    'error': 'Factura no encontrada'
                }), 404
                
            # Obtener detalles de la nota débito (productos o cargos adicionales)
            detalles_json = datos.get('detalles', '[]')
            try:
                detalles = json.loads(detalles_json)
            except:
                detalles = []
                
            if not detalles:
                return jsonify({
                    'success': False,
                    'error': 'No se especificaron conceptos para la nota débito'
                }), 400
                
            # Crear la nota débito
            fecha_emision = datetime.strptime(datos.get('fecha_emision'), '%Y-%m-%d').date() if datos.get('fecha_emision') else date.today()
            
            nueva_nota = NotaDebito(
                numero=int(datos.get('numero', 1)),
                factura_id=factura.id,
                fecha_emision=fecha_emision,
                concepto=datos.get('concepto'),
                subtotal=float(datos.get('subtotal', 0)),
                valor_iva=float(datos.get('iva', 0)),
                total=float(datos.get('total', 0)),
                observaciones=datos.get('observaciones', ''),
                archivo_soporte=archivo_soporte,
                estado='Procesada'
            )
            
            session.add(nueva_nota)
            session.flush()  # Para obtener el ID
            
            # Crear los detalles de la nota débito
            for detalle in detalles:
                nuevo_detalle = DetalleNotaDebito(
                    id_nota_debito=nueva_nota.id,
                    descripcion=detalle.get('descripcion', ''),
                    cantidad=float(detalle.get('cantidad', 0)),
                    precio_unitario=float(detalle.get('precio_unitario', 0)),
                    porcentaje_iva=float(detalle.get('porcentaje_iva', 0)),
                    subtotal=float(detalle.get('cantidad', 0)) * float(detalle.get('precio_unitario', 0))
                )
                session.add(nuevo_detalle)
                
            # Guardar los cambios
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Nota débito creada exitosamente',
                'nota_debito_id': nueva_nota.id
            }), 201
                
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error al crear nota débito: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/api/factura/<int:factura_id>/asociadas', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_notas_asociadas(self, factura_id):
        """Endpoint para obtener todas las notas débito asociadas a una factura"""
        try:
            # Verificar que la factura exista
            factura = session.query(Factura).get(factura_id)
            if not factura:
                return jsonify({
                    'success': False,
                    'error': 'Factura no encontrada'
                }), 404
                
            # Obtener notas débito asociadas - Usar factura_id en vez de id_factura
            notas = session.query(NotaDebito)\
                .filter(NotaDebito.factura_id == factura_id)\
                .all()
                
            # Formatear las notas para la respuesta
            notas_json = []
            for nota in notas:
                nota_json = {
                    'id': nota.id,
                    'numero': nota.numero,
                    'fecha': nota.fecha_emision.isoformat() if nota.fecha_emision else None,
                    'concepto': nota.concepto,
                    'subtotal': float(nota.subtotal),
                    'valor_iva': float(nota.valor_iva),
                    'total': float(nota.total),
                    'estado': nota.estado,
                    'observaciones': nota.observaciones,
                    'factura_numero': factura.numero_factura
                }
                notas_json.append(nota_json)
                
            return jsonify({
                'success': True,
                'notas': notas_json
            })
                
        except Exception as e:
            self.logger.error(f"Error al obtener notas débito asociadas: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/api/notas-debito/<int:nota_id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_nota_debito(self, nota_id):
        """Endpoint para obtener los detalles de una nota débito específica"""
        try:
            # Obtener la nota débito
            nota = session.query(NotaDebito).get(nota_id)
            if not nota:
                return jsonify({
                    'success': False,
                    'error': 'Nota débito no encontrada'
                }), 404
                
            # Obtener la factura asociada - Usar factura_id en vez de id_factura
            factura = session.query(Factura).get(nota.factura_id)
            
            # Obtener detalles de la nota débito
            detalles = session.query(DetalleNotaDebito)\
                .filter(DetalleNotaDebito.id_nota_debito == nota_id)\
                .all()
                
            # Formatear detalles
            detalles_json = []
            for d in detalles:
                detalle_json = {
                    'id': d.id,
                    'descripcion': d.descripcion,
                    'cantidad': float(d.cantidad),
                    'precio_unitario': float(d.precio_unitario),
                    'porcentaje_iva': float(d.porcentaje_iva),
                    'subtotal': float(d.subtotal)
                }
                detalles_json.append(detalle_json)
                
            # Formatear nota débito
            nota_json = {
                'id': nota.id,
                'numero': nota.numero,
                'fecha_emision': nota.fecha_emision.isoformat() if nota.fecha_emision else None,
                'concepto': nota.concepto,
                'subtotal': float(nota.subtotal),
                'valor_iva': float(nota.valor_iva),
                'total': float(nota.total),
                'estado': nota.estado,
                'observaciones': nota.observaciones,
                'factura': {
                    'id': factura.id if factura else None,
                    'numero_factura': factura.numero_factura if factura else 'N/A'
                },
                'items': detalles_json
            }
                
            return jsonify({
                'success': True,
                'nota_debito': nota_json
            })
                
        except Exception as e:
            self.logger.error(f"Error al obtener nota débito: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/api/notas-debito/<int:nota_id>/enviar-correo', methods=['POST'])
    @login_required
    @check_permission('write')
    def enviar_correo_nota_debito(self, nota_id):
        """Endpoint para enviar la nota débito por correo electrónico"""
        try:
            # Obtener datos del request
            datos = request.json
            
            if not datos or 'email' not in datos:
                return jsonify({
                    'success': False,
                    'error': 'Falta el correo electrónico de destino'
                }), 400
                
            # Verificar que la nota débito exista
            nota = session.query(NotaDebito).get(nota_id)
            if not nota:
                return jsonify({
                    'success': False,
                    'error': 'Nota débito no encontrada'
                }), 404
                
            # En un entorno real, aquí generaríamos el PDF y enviaríamos el correo
            # Para este ejemplo, simplemente simulamos el éxito
            email_destino = datos['email']
            
            # Simulamos el envío exitoso
            return jsonify({
                'success': True,
                'message': f'Nota débito enviada exitosamente a {email_destino}'
            })
                
        except Exception as e:
            self.logger.error(f"Error al enviar correo de nota débito: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    # ===============================
    # Métodos Auxiliares
    # ===============================
    
    def _guardar_archivo_soporte(self, archivo):
        """
        Guarda el archivo de soporte y devuelve la ruta relativa
        """
        try:
            # Crear directorio si no existe
            directorio = os.path.join(config.UPLOAD_FOLDER, 'notas_debito')
            os.makedirs(directorio, exist_ok=True)
            
            # Generar nombre de archivo único
            nombre_archivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}"
            ruta_completa = os.path.join(directorio, nombre_archivo)
            
            # Guardar archivo
            archivo.save(ruta_completa)
            
            # Devolver ruta relativa
            return os.path.join('notas_debito', nombre_archivo)
            
        except Exception as e:
            self.logger.error(f"Error al guardar archivo soporte: {str(e)}")
            return None
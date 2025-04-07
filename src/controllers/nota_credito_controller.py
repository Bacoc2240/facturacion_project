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
from src.models.nota_credito import NotaCredito, DetalleNotaCredito
from src.models import session
from sqlalchemy import or_, and_, func
import logging
import config

class NotaCreditoController(FlaskController):
    """
    Controlador para la gestión de notas crédito.
    Maneja todas las operaciones relacionadas con notas crédito incluyendo:
    - Creación y visualización de notas crédito
    - Obtención de notas crédito asociadas a facturas
    - Generación de informes
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        #self.base_route = '/api/notas-credito'  # Ruta base unificada

        
    # ===============================
    # Rutas de Visualización
    # ===============================

    @route('/', methods=['GET'])
    @login_required
    @check_permission('read')
    def index(self):
        """Vista principal de notas crédito"""
        try:
            # Obtener listado de notas crédito
            notas_credito = session.query(NotaCredito)\
                .join(NotaCredito.factura)\
                .order_by(NotaCredito.fecha_emision.desc())\
                .all()
                
            return render_template(
                'notacredito/index.html',  
                notas_credito=notas_credito,
                titulo='Gestión de Notas Crédito'
            )
        except Exception as e:
            self.logger.error(f"Error al cargar notas crédito: {str(e)}")
            flash(f"Error al cargar notas crédito: {str(e)}", "error")
            return render_template(
                'notacredito/index.html',  
                notas_credito=[],
                titulo='Gestión de Notas Crédito',
                error=str(e)
            )

            
    @route('/ver/<int:nota_id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def ver_nota_credito(self, nota_id):
        """Muestra los detalles de una nota crédito específica"""
        try:
            # Obtener la nota crédito con sus relaciones
            nota = session.query(NotaCredito)\
                .filter(NotaCredito.id == nota_id)\
                .first()
                
            if not nota:
                flash('Nota crédito no encontrada', 'danger')
                return redirect(url_for('notacredito.index'))
                
            # Obtener detalles de la nota crédito
            detalles_db = session.query(DetalleNotaCredito)\
                .filter(DetalleNotaCredito.nota_credito_id == nota_id)\
                .all()
                
            # Obtener la factura asociada
            factura = session.query(Factura).get(nota.factura_id)
            
            # Obtener cliente
            cliente = None
            if factura:
                cliente = session.query(Cliente).get(factura.id_cliente)
            
            # Obtener empleado que creó la nota (o un valor por defecto)
            empleado = None
            if nota.creado_por:
                empleado = session.query(Empleado).get(nota.creado_por)
                
            # Determinar si se debe mostrar para impresión o en un modal
            imprimir = request.args.get('print', 'false').lower() == 'true'
            es_modal = request.args.get('modal', 'false').lower() == 'true'
            
            # Preparar los detalles con la estructura que espera la plantilla
            detalles = []
            for detalle in detalles_db:
                # Obtener producto asociado al detalle si existe
                producto = None
                if hasattr(detalle, 'detalle_factura_id') and detalle.detalle_factura_id:
                    # Si hay un detalle de factura asociado, obtener el producto desde ahí
                    detalle_factura = session.query(DetalleFactura).get(detalle.detalle_factura_id)
                    if detalle_factura and detalle_factura.id_producto:
                        producto = session.query(Productos).get(detalle_factura.id_producto)
                elif hasattr(detalle, 'id_producto') and detalle.id_producto:
                    # Si el detalle tiene directamente id_producto
                    producto = session.query(Productos).get(detalle.id_producto)
                    
                # Crear estructura de datos para la plantilla
                detalle_info = {
                    'producto': {
                        'codigo_barras': producto.codigo_barras if producto else 'N/A',
                        'nombre': producto.nombre if producto else 'Producto no encontrado',
                        'categoria': producto.categoria if producto else ''
                    },
                    'detalle': {
                        'cantidad': detalle.cantidad,
                        'precio_unitario': detalle.valor_unitario if hasattr(detalle, 'valor_unitario') else 0,
                        'subtotal': detalle.subtotal
                    },
                    'porcentaje_iva': detalle.porcentaje_iva
                }
                detalles.append(detalle_info)
            
            # Variables adicionales necesarias para la plantilla
            factura_original = factura  # Para compatibilidad con la plantilla
            
            # Calcular valores para mostrar en el formato
            nota_credito_valores = {
                'subtotal': nota.subtotal,
                'IVA': nota.iva,
                'total': nota.total
            }
            
            # Convertir el valor total a letras (simulado)
            valor_en_letras = "Cuatrocientos dieciséis punto cinco pesos"
            
            # Método de pago (valor por defecto)
            metodo_pago = "CRÉDITO"
                
            return render_template(
                'notacredito/ver.html',
                nota=nota,
                nota_credito=nota,  # Para compatibilidad con la plantilla
                detalles=detalles,
                factura=factura,
                factura_original=factura,  # Para compatibilidad con la plantilla
                cliente=cliente,
                empleado=empleado or {'nombre': 'Vendedor no especificado'},  # Valor por defecto para empleado
                imprimir=imprimir,
                es_modal=es_modal,
                nota_credito_valores=nota_credito_valores,
                valor_en_letras=valor_en_letras,
                metodo_pago=metodo_pago,
                titulo=f'Nota Crédito #{nota.numero}'
            )
            
        except Exception as e:
            self.logger.error(f"Error al mostrar nota crédito: {str(e)}")
            flash(f"Error al mostrar nota crédito: {str(e)}", "error")
            
            # Si es una solicitud modal, devolver un JSON con el error
            if request.args.get('modal', 'false').lower() == 'true':
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
            return redirect(url_for('notacredito.index'))
        
    # ===============================
    # API Endpoints
    # ===============================

    @route('/api/notas-credito/siguiente-numero', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_siguiente_numero(self):
        """Endpoint para obtener el siguiente número de nota crédito disponible"""
        try:
            # Obtener la última nota crédito
            ultima_nota = session.query(NotaCredito)\
                .order_by(NotaCredito.numero.desc())\
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
            self.logger.error(f"Error al obtener siguiente número de nota crédito: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/api/notas-credito', methods=['POST'])
    @login_required
    @check_permission('write')
    def crear_nota_credito(self):
        """Endpoint para crear una nueva nota crédito"""
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
            if not datos.get('factura_id') or not datos.get('motivo_dian'):
                return jsonify({
                    'success': False,
                    'error': 'Faltan datos requeridos (factura_id, motivo_dian)'
                }), 400
                
            # Validar que la factura exista
            factura = session.query(Factura).get(datos.get('factura_id'))
            if not factura:
                return jsonify({
                    'success': False,
                    'error': 'Factura no encontrada'
                }), 404
                
            # Obtener detalles de la nota crédito (productos)
            detalles_json = datos.get('detalles', '[]')
            try:
                detalles = json.loads(detalles_json)
            except:
                detalles = []
                
            if not detalles:
                return jsonify({
                    'success': False,
                    'error': 'No se especificaron productos para la nota crédito'
                }), 400
                
            # Crear la nota crédito
            fecha_emision = datetime.strptime(datos.get('fecha_emision_nc'), '%Y-%m-%d').date() if datos.get('fecha_emision_nc') else date.today()
            
            # Usar factura_id en lugar de id_factura para coincidir con el modelo
            nueva_nota = NotaCredito(
                numero=int(datos.get('numero', 1)),
                fecha_emision=fecha_emision,
                factura_id=factura.id,  
                motivo_dian=int(datos.get('motivo_dian')),
                subtotal=float(datos.get('subtotal', 0)),
                iva=float(datos.get('iva', 0)),
                total=float(datos.get('total', 0)),
                observaciones=datos.get('observaciones', ''),
                archivo_soporte=archivo_soporte,
                estado='Procesada',
                creado_por=flask_session.get('empleado_id')  # Agregar empleado desde la sesión
            )
            
            session.add(nueva_nota)
            session.flush()  # Para obtener el ID
            
            # Crear los detalles de la nota crédito
            for detalle in detalles:
                # Corregimos la lógica para manejar el detalle_factura_id que no puede ser nulo
                detalle_factura_id = detalle.get('detalle_factura_id') or detalle.get('detalle_id')
                
                # Si no hay detalle_factura_id, intentamos encontrarlo
                if not detalle_factura_id:
                    # Buscar en la factura el detalle que coincida con el producto_id
                    producto_id = detalle.get('producto_id')
                    if producto_id:
                        detalle_factura = session.query(DetalleFactura)\
                            .filter(DetalleFactura.factura_id == factura.id,
                                    DetalleFactura.id_producto == producto_id)\
                            .first()
                        if detalle_factura:
                            detalle_factura_id = detalle_factura.id
                
                # Si aún no hay detalle_factura_id, no podemos continuar con este detalle
                if not detalle_factura_id:
                    continue
                    
                nuevo_detalle = DetalleNotaCredito(
                    nota_credito_id=nueva_nota.id,
                    detalle_factura_id=detalle_factura_id,
                    cantidad=float(detalle.get('cantidad', 0)),
                    valor_unitario=float(detalle.get('precio_unitario', 0)),
                    porcentaje_iva=float(detalle.get('porcentaje_iva', 0))
                )
                session.add(nuevo_detalle)
                
            # Guardar los cambios
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Nota crédito creada exitosamente',
                'nota_credito_id': nueva_nota.id
            }), 201
                
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error al crear nota crédito: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/api/factura/<int:factura_id>/asociadas', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_notas_asociadas(self, factura_id):
        """Endpoint para obtener todas las notas crédito asociadas a una factura"""
        try:
            # Verificar que la factura exista
            factura = session.query(Factura).get(factura_id)
            if not factura:
                return jsonify({
                    'success': False,
                    'error': 'Factura no encontrada'
                }), 404
                
            # Obtener notas crédito asociadas
            notas = session.query(NotaCredito)\
                .filter(NotaCredito.factura_id == factura_id)\
                .all()
                
            # Formatear las notas para la respuesta
            notas_json = []
            for nota in notas:
                nota_json = {
                    'id': nota.id,
                    'numero': nota.numero,
                    'fecha': nota.fecha_emision.isoformat() if nota.fecha_emision else None,
                    'motivo': nota.motivo_dian,
                    'subtotal': float(nota.subtotal),
                    'iva': float(nota.iva),
                    'total': float(nota.total),
                    'estado': nota.estado if hasattr(nota, 'estado') else 'Procesada',
                    'observaciones': nota.observaciones,
                    'factura_numero': factura.numero_factura
                }
                notas_json.append(nota_json)
                
            return jsonify({
                'success': True,
                'notas': notas_json
            })
                
        except Exception as e:
            self.logger.error(f"Error al obtener notas crédito asociadas: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/<int:id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_nota_credito(self, id):
        """Endpoint para obtener una nota crédito por ID"""
        try:
            nota = session.query(NotaCredito).get(id)
            if not nota:
                return jsonify({'success': False, 'error': 'Nota no encontrada'}), 404
                
            # Obtener la factura asociada
            factura = session.query(Factura).get(nota.factura_id)
            
            # Obtener detalles de la nota crédito (productos)
            detalles = session.query(DetalleNotaCredito)\
                .filter(DetalleNotaCredito.nota_credito_id == id)\
                .all()
                
            # Formatear nota crédito
            nota_json = {
                'id': nota.id,
                'numero': nota.numero,
                'fecha_emision': nota.fecha_emision.isoformat() if nota.fecha_emision else None,
                'motivo_dian': nota.motivo_dian,
                'motivo_descripcion': nota.motivo_descripcion,
                'subtotal': float(nota.subtotal),
                'iva': float(nota.iva),
                'total': float(nota.total),
                'estado': getattr(nota, 'estado', 'Procesada'),
                'observaciones': nota.observaciones,
                'factura': {
                    'id': factura.id if factura else None,
                    'numero_factura': factura.numero_factura if factura else 'N/A'
                },
                'items': [
                    {
                        'id': d.id,
                        'cantidad': float(d.cantidad),
                        'precio_unitario': float(d.valor_unitario),
                        'porcentaje_iva': float(d.porcentaje_iva),
                        'subtotal': float(d.subtotal)
                    } for d in detalles
                ]
            }
                
            return jsonify({
                'success': True,
                'nota_credito': nota_json
            })
                
        except Exception as e:
            self.logger.error(f"Error al obtener nota crédito: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @route('/api/notas-credito/<int:nota_id>/enviar-correo', methods=['POST'])
    @login_required
    @check_permission('write')
    def enviar_correo_nota_credito(self, nota_id):
        """Endpoint para enviar la nota crédito por correo electrónico"""
        try:
            # Obtener datos del request
            datos = request.json
            
            if not datos or 'email' not in datos:
                return jsonify({
                    'success': False,
                    'error': 'Falta el correo electrónico de destino'
                }), 400
                
            # Verificar que la nota crédito exista
            nota = session.query(NotaCredito).get(nota_id)
            if not nota:
                return jsonify({
                    'success': False,
                    'error': 'Nota crédito no encontrada'
                }), 404
                
            # En un entorno real, aquí generaríamos el PDF y enviaríamos el correo
            # Para este ejemplo, simplemente simulamos el éxito
            email_destino = datos['email']
            
            # Simulamos el envío exitoso
            return jsonify({
                'success': True,
                'message': f'Nota crédito enviada exitosamente a {email_destino}'
            })
                
        except Exception as e:
            self.logger.error(f"Error al enviar correo de nota crédito: {str(e)}")
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
            directorio = os.path.join(config.UPLOAD_FOLDER, 'notas_credito')
            os.makedirs(directorio, exist_ok=True)
            
            # Generar nombre de archivo único
            nombre_archivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}"
            ruta_completa = os.path.join(directorio, nombre_archivo)
            
            # Guardar archivo
            archivo.save(ruta_completa)
            
            # Devolver ruta relativa
            return os.path.join('notas_credito', nombre_archivo)
            
        except Exception as e:
            self.logger.error(f"Error al guardar archivo soporte: {str(e)}")
            return None
        
    # Agregar en el controlador
    @route('/api/docs', methods=['GET'])
    def documentacion_api(self):
        """Documentación técnica de los endpoints"""
        docs = {
            "obtener_nota": {
                "ruta": "/api/notas-credito/<int:id>",
                "metodo": "GET",
                "descripcion": "Obtiene los detalles de una nota crédito"
            }
        }
        return jsonify(docs)
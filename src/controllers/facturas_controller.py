import os
import json
from datetime import date
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
from src.models.resolucion_dian import ResolucionDIAN
from src.models.metodo_de_pago import MetodoDePago
from src.models import session
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import joinedload 
import tempfile
# Eliminamos la importación problemática de WeasyPrint
# from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from num2words import num2words
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import logging
import config

class FacturasController(FlaskController):
    """
    Controlador para la gestión de facturas.
    Maneja todas las operaciones relacionadas con facturas incluyendo:
    - Visualización y listado de facturas
    - Creación y anulación de facturas 
    - Gestión de productos en facturas
    - Validación de stock y resolución DIAN
    - Impresión y envío de facturas
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
    # ===============================
    # Métodos de Utilidad de Sesión
    # ===============================
    
    def _limpiar_sesion(self):
        """
        Método interno para limpiar el estado de la sesión y manejar transacciones.
        Asegura la consistencia de la base de datos en caso de errores.
        """
        try:
            if hasattr(session, 'is_active') and session.is_active:
                session.rollback()
        except Exception as e:
            print(f"Error al limpiar sesión: {str(e)}")
            try:
                session.remove()
            except:
                pass
        
    def _limpiar_mensajes_flash(self):
        """
        Método interno para limpiar los mensajes flash acumulados en la sesión.
        Ayuda a evitar que se acumulen mensajes de error obsoletos.
        """
        try:
            if flask_session and '_flashes' in flask_session:
                flask_session.pop('_flashes', None)
                print("Mensajes flash limpiados exitosamente")
        except Exception as e:
            print(f"Error al limpiar mensajes flash: {str(e)}")
            
            
    # ===============================
    # Rutas de Visualización
    # ===============================

    @route('/', methods=['GET'])
    @login_required
    def index(self):
        """Vista principal de facturas que muestra la lista de facturas y formulario de creación."""
        
        # Limpiar mensajes flash acumulados
        self._limpiar_mensajes_flash()
        
        try:
            # Primero aseguramos que no haya transacciones activas
            session.rollback()
            
            # Obtener facturas con sus relaciones
            facturas = session.query(Factura)\
                .join(Factura.empleado)\
                .join(Factura.cliente)\
                .filter(Factura.activa == True)\
                .all()

            # Obtener lista de clientes activos
            clientes = self._obtener_clientes_activos()

            # Obtener lista de empleados activos
            empleados = self._obtener_empleados_activos()

            return render_template(
                'facturas.html',
                facturas=facturas,
                empleados=empleados,
                clientes=clientes,
                titulo='Gestión de Facturas'
            )

        except Exception as e:
            self._limpiar_sesion()
            print(f"Error al cargar facturas: {str(e)}")
            return render_template(
                'facturas.html',
                facturas=[],
                empleados=[],
                clientes=[],
                titulo='Gestión de Facturas',
                error=str(e)
            )

    @route('/ver/<int:factura_id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def ver_factura(self, factura_id):
        """Muestra los detalles de una factura específica."""
        try:
            # Para depuración: imprimir el ID de factura recibido
            print(f"Accediendo a la factura con ID: {factura_id}")
            
            # Obtener la factura
            factura = session.query(Factura).get(factura_id)
            
            if not factura:
                flash('Factura no encontrada', 'danger')
                return redirect(url_for('facturas.index'))
            
            print(f"Factura encontrada: #{factura.numero_factura}")
            
            # Obtener los detalles de la factura con JOIN a productos para obtener más datos
            detalles = session.query(DetalleFactura).filter_by(id_factura=factura_id).all()
            print(f"Detalles encontrados: {len(detalles)}")
            
            # Obtener los IDs de productos para cargarlos en una sola consulta
            producto_ids = [d.id_producto for d in detalles]
            
            # Diccionario para almacenar la información de productos
            productos = {}
            
            if producto_ids:
                # Cargar los productos en una sola consulta para evitar N+1
                productos_list = session.query(Productos).filter(Productos.id.in_(producto_ids)).all()
                
                print(f"Productos encontrados: {len(productos_list)} de {len(producto_ids)} esperados")
                
                # Imprimir información detallada de cada producto para depuración
                for p in productos_list:
                    print(f"Producto ID {p.id}: {p.nombre}, Categoría: {getattr(p, 'categoria', 'N/A')}")
                    
                    # Obtener la categoría como string en lugar de objeto
                    categoria_str = None
                    if hasattr(p, 'categoria'):
                        # Si la categoría es un objeto, intentar obtener el nombre de la categoría
                        if hasattr(p.categoria, 'categoria'):
                            categoria_str = p.categoria.categoria
                        elif hasattr(p.categoria, 'id'):
                            # Si solo tenemos el ID de la categoría, intentar buscarla en la base de datos
                            try:
                                from src.models.categorias import Categorias
                                cat = session.query(Categorias).get(p.categoria.id)
                                if cat:
                                    categoria_str = cat.categoria
                            except Exception as e:
                                print(f"Error al obtener categoría por ID: {str(e)}")
                        else:
                            # Si es un valor directo (string o número), convertirlo a string
                            categoria_str = str(p.categoria)
                    
                    # Almacenar la información del producto en el diccionario
                    productos[p.id] = {
                        'id': p.id,
                        'nombre': getattr(p, 'nombre', 'Sin nombre'),
                        'codigo_barras': getattr(p, 'codigo_barras', 'N/A'),
                        'categoria': categoria_str,
                        'porcentaje_iva': float(getattr(p, 'porcentaje_iva', 19))
                    }
            
            # Preparar los datos para la plantilla
            detalles_con_iva = []
            subtotal_calculado = 0
            iva_calculado = 0
            
            for detalle in detalles:
                # Obtener el producto correspondiente a este detalle
                producto = productos.get(detalle.id_producto, {})
                
                # Para depuración: imprimir cada detalle y el producto asociado
                print(f"Procesando detalle: ID={detalle.id}, Producto ID={detalle.id_producto}, " 
                    f"Producto encontrado: {'Sí' if detalle.id_producto in productos else 'No'}")
                
                # Determinar el porcentaje de IVA para este detalle
                porcentaje_iva = 19.0  # Valor predeterminado como float
                
                # IMPORTANTE: Usar el porcentaje de IVA almacenado en el detalle de la factura
                if hasattr(detalle, 'porcentaje_iva') and detalle.porcentaje_iva is not None:
                    porcentaje_iva = float(detalle.porcentaje_iva)
                    print(f"Usando IVA del detalle: {porcentaje_iva}%")
                else:
                    print(f"El detalle no tiene porcentaje_iva, usando predeterminado: {porcentaje_iva}%")
                
                # Calcular valores
                subtotal = float(detalle.subtotal)
                iva = subtotal * (porcentaje_iva / 100.0)
                
                # Acumular totales
                subtotal_calculado += subtotal
                iva_calculado += iva
                
                # Agregar a la lista de detalles
                detalles_con_iva.append({
                    'detalle': detalle,
                    'producto': producto,
                    'porcentaje_iva': porcentaje_iva,
                    'iva': iva,
                    'total_con_iva': subtotal + iva
                })
            
            # Calcular total
            total_calculado = subtotal_calculado + iva_calculado
            
            # Obtener cliente
            cliente = session.query(Cliente).get(factura.id_cliente)
            if cliente:
                print(f"Cliente encontrado: {cliente.nombre_cliente}")
            else:
                print("Cliente no encontrado")
            
            # Obtener empleado con enfoque más robusto
            empleado = None
            try:
                empleado = session.query(Empleado).get(factura.id_empleado)
                if empleado:
                    print(f"Empleado encontrado: ID={empleado.id_empleado}, Nombre={getattr(empleado, 'nombre_apellidos', 'N/A')}")
                    # Asegurarse de que el objeto empleado tenga el atributo 'nombre'
                    if not hasattr(empleado, 'nombre'):
                        print("Añadiendo atributo 'nombre' al empleado")
                        # Si el empleado no tiene un atributo 'nombre' pero tiene 'nombre_apellidos',
                        # usar ese valor en su lugar
                        empleado.nombre = getattr(empleado, 'nombre_apellidos', 'Vendedor no especificado')
                else:
                    print("Empleado no encontrado")
                    # Crear un objeto simple con la información mínima necesaria
                    empleado = type('EmpleadoSimple', (), {'nombre': 'Vendedor no especificado'})
            except Exception as e:
                print(f"Error al obtener empleado: {str(e)}")
                empleado = type('EmpleadoSimple', (), {'nombre': 'Vendedor no especificado'})
            
            
            # Obtener método de pago directamente de la base de datos
            metodo_pago = "CRÉDITO"  # Valor predeterminado
            try:
                # Si no hay relación directa, intentar buscar en la tabla intermedia con enfoque diferente
                from sqlalchemy import text
                
                # Primero intentamos obtener el método de pago por la relación muchos a muchos
                if hasattr(factura, 'metodos_pago') and factura.metodos_pago:
                    # Si hay métodos de pago asociados a la factura
                    if len(factura.metodos_pago) > 0:
                        # Obtener el primer método de pago
                        metodo = factura.metodos_pago[0]
                        # Verificar si el método tiene el atributo 'nombre' o 'nombre_metodo'
                        if hasattr(metodo, 'nombre'):
                            metodo_pago = metodo.nombre
                        elif hasattr(metodo, 'nombre_metodo'):
                            metodo_pago = metodo.nombre_metodo
                        print(f"Método de pago encontrado por relación directa: {metodo_pago}")
                    else:
                        print("La factura tiene metodos_pago pero está vacío")
                else:
                    # Intentar con SQL directo - usando un enfoque más específico
                    # Asumiendo que factura.id es el valor correcto para la tabla factura_metodo_de_pago.id
                    sql = text("""
                        SELECT mp.nombre_metodo 
                        FROM metodo_de_pago mp, factura_metodo_de_pago fmp
                        WHERE mp.id_metodo_pago = fmp.id_metodo_pago 
                        AND fmp.id = :id_factura
                    """)
                    result = session.execute(sql, {"id_factura": factura.id}).first()
                    
                    if result:
                        metodo_pago = result[0]
                        print(f"Método de pago encontrado mediante SQL: {metodo_pago}")
                    else:
                        # Intentemos una consulta directa a la tabla intermedia para debugging
                        check_sql = text("SELECT * FROM factura_metodo_de_pago WHERE id = :id_factura")
                        check_result = session.execute(check_sql, {"id_factura": factura.id}).fetchall()
                        
                        if check_result:
                            print(f"Encontradas {len(check_result)} relaciones en tabla intermedia:")
                            for rel in check_result:
                                print(f"  ID Factura: {rel[0]}, ID Método Pago: {rel[1]}")
                                
                                # Intentar obtener el nombre del método de pago directamente
                                method_sql = text("SELECT nombre_metodo FROM metodo_de_pago WHERE id_metodo_pago = :id")
                                method_result = session.execute(method_sql, {"id": rel[1]}).first()
                                
                                if method_result:
                                    metodo_pago = method_result[0]
                                    print(f"  Nombre del método: {metodo_pago}")
                                else:
                                    print(f"  No se encontró método de pago con ID {rel[1]}")
                        else:
                            print(f"No se encontraron relaciones en factura_metodo_de_pago para factura ID {factura.id}")
                            
                        # Último intento - buscar en la tabla de facturas si hay alguna columna directa
                        try:
                            forma_pago_sql = text("""
                                SELECT forma_pago FROM factura WHERE id = :id_factura
                            """)
                            forma_pago_result = session.execute(forma_pago_sql, {"id_factura": factura.id}).first()
                            
                            if forma_pago_result and forma_pago_result[0]:
                                metodo_pago = forma_pago_result[0]
                                print(f"Método de pago encontrado en columna forma_pago: {metodo_pago}")
                        except Exception as e:
                            print(f"Error al buscar columna forma_pago: {str(e)}")
                        
                        print("No se encontraron métodos de pago, usando predeterminado")
            except Exception as e:
                print(f"Error al obtener método de pago: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Convertir el total a letras
            valor_en_letras = self._convertir_numero_a_letras(total_calculado)
            
            # Crear el objeto factura_valores para la plantilla
            factura_valores = {
                'subtotal': subtotal_calculado,
                'IVA': iva_calculado,
                'total': total_calculado
            }
            
            print(f"Renderizando plantilla con: Subtotal={subtotal_calculado}, IVA={iva_calculado}, Total={total_calculado}")
            
            # Renderizar la plantilla
            return render_template(
                'factura_template.html',
                factura=factura,
                cliente=cliente,
                empleado=empleado,
                detalles=detalles_con_iva,
                productos=productos,
                factura_valores=factura_valores,
                valor_en_letras=valor_en_letras,
                metodo_pago=metodo_pago,
                imprimir=request.args.get('print', 'false').lower() == 'true',
                debug=False  # Cambiar a True para mostrar información de depuración
            )
            
        except Exception as e:
            print(f"Error al mostrar factura: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error al cargar la factura: {str(e)}', 'error')
            return redirect(url_for('facturas.index'))
    
    
    # ===============================
    # API Endpoints de Clientes
    # ===============================

    @route('/api/clientes/buscar/<query>', methods=['GET'])
    @login_required
    @check_permission('read')
    def buscar_clientes(self, query):
        """
        Endpoint para búsqueda en tiempo real de clientes.
        """
        try:
            # Validación de entrada
            if not query or len(query.strip()) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Término de búsqueda vacío'
                }), 400

            query = query.strip()
            
            # Determinar si la búsqueda es por ID o nombre
            is_id_search = query.isdigit()
            
            # Construir la consulta base
            base_query = session.query(Cliente).filter(Cliente.activo == True)
            
            # Aplicar criterios de búsqueda
            if is_id_search:
                clientes = base_query.filter(
                    Cliente.id_cliente.ilike(f'%{query}%')
                )
            else:
                clientes = base_query.filter(
                    func.lower(Cliente.nombre_cliente).ilike(f'%{query.lower()}%')
                )
            
            # Ejecutar la consulta
            clientes = clientes.limit(5).all()

            # Formatear resultados
            clientes_data = [{
                'id': str(c.id_cliente),
                'nombre': c.nombre_cliente,
                'telefono': getattr(c, 'telefono', '') or '',
                'email': getattr(c, 'correo_electronico', '') or ''
            } for c in clientes]

            return jsonify({
                'success': True,
                'clientes': clientes_data,
            })

        except Exception as e:
            print(f"Error en búsqueda de clientes: {str(e)}")
            session.rollback()
            return jsonify({
                'success': False,
                'error': 'Error en la búsqueda',
                'details': str(e)
            }), 500

    @route('/api/clientes/<id_cliente>', methods=['GET'])
    @login_required
    @check_permission('read')
    def verificar_cliente(self, id_cliente):
        """Endpoint para verificar si existe un cliente específico."""
        try:
            id_cliente = id_cliente.strip()
            session.rollback()
            
            # Búsqueda del cliente
            cliente = session.query(Cliente)\
                .filter(
                    and_(
                        Cliente.id_cliente == str(id_cliente),
                        Cliente.activo == True
                    )
                )\
                .first()
            
            if cliente:
                return jsonify({
                    'success': True,
                    'cliente': {
                        'id': str(cliente.id_cliente),
                        'nombre': cliente.nombre_cliente,
                        'encontrado': True  # Flag adicional para confirmar
                    }
                })
            
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado',
                'encontrado': False
            }), 404

        except Exception as e:
            print(f"Error al verificar cliente: {str(e)}")
            session.rollback()
            return jsonify({
                'success': False,
                'error': 'Error en la verificación',
                'details': str(e)
            }), 500
    
    @route('/api/clientes/menor-cuantia', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_cliente_menor_cuantia(self):
        
        try:
            # Configuramos el cliente de menor cuantía predeterminado
            cliente_menor_cuantia = {
                'id': '22222222222',  # Identificador estándar para cliente de menor cuantía
                'nombre': 'Menor Cuantía'  # Nombre descriptivo
            }
            
            # Retornamos la respuesta con el formato estándar de éxito
            return jsonify({
                'success': True,
                'cliente': cliente_menor_cuantia
            })
            
        except Exception as e:
            # Registramos el error utilizando el logger de la instancia
            self.logger.error(f"Error al obtener cliente menor cuantía: {str(e)}")
            
            # Retornamos un mensaje de error genérico al cliente
            return jsonify({
                'success': False,
                'error': 'Error al obtener cliente de menor cuantía'
            }), 500
                
    # ===============================
    # API Endpoints Factura
    # ===============================

    @route('/api/lista', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_lista_facturas(self):
        """Endpoint para obtener la lista de facturas en formato JSON."""
        try:
            facturas = session.query(Factura)\
                .join(Factura.empleado)\
                .join(Factura.cliente)\
                .filter(Factura.activa == True)\
                .all()

            facturas_json = []
            
            for f in facturas:
                # Recalcular el total para cada factura
                total_calculado = f.total  # Valor por defecto
                
                try:
                    # Obtener detalles de la factura para recalcular el total
                    detalles = session.query(DetalleFactura).filter_by(id_factura=f.id).all()
                    
                    if detalles:
                        # Calcular subtotal
                        subtotal = sum(float(detalle.subtotal) for detalle in detalles)
                        
                        # Obtener productos para calcular IVA
                        producto_ids = [d.id_producto for d in detalles]
                        productos = {}
                        
                        if producto_ids:
                            productos_list = session.query(Productos).filter(Productos.id.in_(producto_ids)).all()
                            for p in productos_list:
                                productos[p.id] = getattr(p, 'porcentaje_iva', 0)
                        
                        # Calcular IVA
                        iva = 0
                        for detalle in detalles:
                            porcentaje_iva = productos.get(detalle.id_producto, 0)
                            iva += float(detalle.subtotal) * (float(porcentaje_iva) / 100)
                        
                        # Total recalculado
                        total_calculado = subtotal + iva
                        
                        print(f"Factura {f.id}: Total almacenado={f.total}, Total recalculado={total_calculado}")
                except Exception as e:
                    print(f"Error al recalcular total para factura {f.id}: {str(e)}")
                
                factura_json = {
                    'id': f.id,
                    'numero_factura': f.numero_factura,
                    'fecha': f.fecha.isoformat() if f.fecha else None,
                    'cliente': {
                        'id': f.cliente.id_cliente,
                        'nombre': f.cliente.nombre_cliente if hasattr(f.cliente, 'nombre_cliente') else ''
                    },
                    'total': float(total_calculado),  # Usar el total recalculado
                    'estado': f.estado,
                    'activa': f.activa
                }
                
                facturas_json.append(factura_json)

            return jsonify(facturas_json)

        except Exception as e:
            print(f"Error al cargar facturas: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @route('/api/facturas/crear', methods=['POST'])
    @login_required
    @check_permission('write')
    def crear_factura_api(self):
        """Endpoint para crear una nueva factura con sus productos."""
        try:
            datos = request.get_json()

            # Validar datos requeridos
            if not self._validar_datos_factura(datos):
                return jsonify({
                    'success': False,
                    'error': 'Faltan datos requeridos'
                }), 400

            # Mostrar los datos recibidos para debugging
            print("Datos de factura recibidos:", datos)

            # Obtener y validar resolución DIAN
            resolucion = self._obtener_resolucion_activa()
            if not resolucion:
                return jsonify({
                    'success': False,
                    'error': 'No hay resolución DIAN activa'
                }), 400

            # Validar que el cliente exista
            cliente = session.query(Cliente).get(datos['id_cliente'])
            if not cliente:
                return jsonify({
                    'success': False,
                    'error': 'Cliente no encontrado'
                }), 400

            # Asegurarse de que no haya transacciones activas
            if hasattr(session, 'is_active') and session.is_active:
                session.rollback()

            # Crear la factura base (sin productos todavía)
            nueva_factura = self._crear_factura(datos, resolucion)
                
            # Guardar la factura para obtener un ID
            session.add(nueva_factura)
            session.flush()
            
            if 'forma_pago' in datos and datos['forma_pago']:
                try:
                    # Obtener el método de pago por su nombre
                    metodo_pago = session.query(MetodoDePago).filter(
                        MetodoDePago.nombre_metodo == datos['forma_pago']
                    ).first()
                    
                    if metodo_pago:
                        print(f"Método de pago encontrado: {metodo_pago.nombre_metodo} (ID: {metodo_pago.id_metodo_pago})")
                        
                        # Inserción directa en la tabla intermedia usando SQL
                        from sqlalchemy import text
                        
                        # Verificar si ya existe la relación para evitar duplicados
                        check_sql = text("""
                            SELECT id FROM factura_metodo_de_pago 
                            WHERE id = :id_factura AND id_metodo_pago = :id_metodo_pago
                        """)
                        
                        existing = session.execute(check_sql, {
                            "id_factura": nueva_factura.id,
                            "id_metodo_pago": metodo_pago.id_metodo_pago
                        }).first()
                        
                        if not existing:
                            # Insertar nueva relación
                            insert_sql = text("""
                                INSERT INTO factura_metodo_de_pago (id, id_metodo_pago)
                                VALUES (:id_factura, :id_metodo_pago)
                            """)
                            
                            session.execute(insert_sql, {
                                "id_factura": nueva_factura.id,
                                "id_metodo_pago": metodo_pago.id_metodo_pago
                            })
                            
                            print(f"Relación creada entre factura {nueva_factura.id} y método de pago {metodo_pago.id_metodo_pago}")
                        else:
                            print(f"La relación ya existe entre factura {nueva_factura.id} y método de pago {metodo_pago.id_metodo_pago}")
                    else:
                        print(f"Método de pago '{datos['forma_pago']}' no encontrado")
                except Exception as e:
                    print(f"Error al asignar método de pago: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Variable para acumular el IVA total basado en productos individuales
            iva_total = 0.0
            
            # Agregar productos a la factura con sus IVAs específicos
            for item in datos['productos']:
                # Debug: Mostrar la información del producto que se está procesando
                print(f"Procesando producto: {item}")
                
                # Obtener el porcentaje de IVA específico para este producto (convertir a float)
                porcentaje_iva = float(item.get('iva', 0))
                
                # Obtener producto desde la base de datos
                producto = session.query(Productos).get(item['id'])
                if not producto:
                    session.rollback()
                    return jsonify({
                        'success': False,
                        'error': f"Producto con ID {item['id']} no encontrado"
                    }), 404
                    
                # Calcular el subtotal para este producto (asegurar float)
                subtotal_producto = float(item['precio']) * float(item['cantidad'])
                
                # Calcular el IVA para este producto según su porcentaje específico
                iva_producto = subtotal_producto * (porcentaje_iva / 100.0)
                
                # Acumular el IVA total
                iva_total += iva_producto
                
                # Crear el detalle de factura con el IVA específico
                try:
                    # Al usar el método agregar_producto de la clase Factura, 
                    # pasar explícitamente el porcentaje de IVA específico
                    detalle = nueva_factura.agregar_producto(
                        id_producto=item['id'],
                        cantidad=float(item['cantidad']),
                        precio_unitario=float(item['precio']),
                        porcentaje_iva=porcentaje_iva  # Pasar explícitamente el porcentaje de IVA
                    )
                    
                    print(f"Detalle creado: ID={detalle.id}, IVA={porcentaje_iva}%")
                    
                except Exception as e:
                    print(f"Error al agregar producto: {e}")
                    session.rollback()
                    return jsonify({
                        'success': False,
                        'error': f"Error al agregar producto: {str(e)}"
                    }), 500

            # Actualizar el IVA total de la factura con el valor calculado
            nueva_factura.IVA = float(iva_total)
            
            # Recalcular el total
            nueva_factura.total = float(nueva_factura.subtotal) + float(iva_total)
            
            # Asignar método de pago si se proporcionó
            if 'forma_pago' in datos and datos['forma_pago']:
                try:
                    # Buscar el método de pago por nombre
                    metodo_pago = session.query(MetodoDePago).filter_by(
                        nombre_metodo=datos['forma_pago']
                    ).first()
                    
                    if metodo_pago:
                        print(f"Método de pago encontrado: {metodo_pago.nombre_metodo}")
                        
                        # Asegurarse de que la relación metodos_pago esté inicializada
                        if not hasattr(nueva_factura, 'metodos_pago') or nueva_factura.metodos_pago is None:
                            nueva_factura.metodos_pago = []
                        
                        # Agregar el método de pago a la factura
                        nueva_factura.metodos_pago.append(metodo_pago)
                    else:
                        print(f"Método de pago no encontrado: {datos['forma_pago']}")
                except Exception as e:
                    print(f"Error al asignar método de pago: {str(e)}")
                    
            # Actualizar el historial de compras del cliente
            if cliente and nueva_factura.id:
                try:
                    # Construir la lista de productos comprados para el historial
                    productos_comprados = []
                    for item in datos['productos']:
                        producto = session.query(Productos).get(item['id'])
                        if producto:
                            # Añadir el nombre del producto y la cantidad
                            productos_comprados.append(f"{producto.nombre} (x{item['cantidad']})")
                    
                    # Si hay productos para agregar al historial
                    if productos_comprados:
                        # Crear una entrada con formato: Fecha, Número de factura, lista de productos
                        entrada_historial = f"{nueva_factura.fecha.strftime('%Y-%m-%d')}, Factura #{nueva_factura.numero_factura}: {', '.join(productos_comprados)}"
                        
                        # Agregar la entrada al historial del cliente
                        cliente.agregar_compra(entrada_historial)
                        
                        print(f"Historial de compras actualizado para cliente {cliente.id_cliente}")
                except Exception as e:
                    print(f"Error al actualizar historial de compras: {str(e)}")
            
            # Confirmar todos los cambios
            session.commit()

            return jsonify({
                'success': True,
                'message': 'Factura creada exitosamente',
                'factura': self._formatear_factura(nueva_factura)
            }), 201

        except Exception as e:
            session.rollback()
            print(f"Error al crear factura: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
              
    @route('/api/facturas/<int:factura_id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def obtener_factura_con_detalles(self, factura_id):
        """Endpoint para obtener los detalles completos de una factura."""
        try:
            # Obtener la factura
            factura = session.query(Factura).get(factura_id)
                
            if not factura:
                return jsonify({
                    'success': False,
                    'error': 'Factura no encontrada'
                }), 404
            
            # Obtener cliente
            cliente = session.query(Cliente).get(factura.id_cliente)
            
            # Obtener detalles de la factura
            detalles = session.query(DetalleFactura).filter_by(id_factura=factura_id).all()
            
            # Obtener IDs de productos
            producto_ids = [d.id_producto for d in detalles]
            
            # Obtener productos en una sola consulta
            productos = {}
            if producto_ids:
                productos_query = session.query(Productos).filter(Productos.id.in_(producto_ids)).all()
                productos = {p.id: p for p in productos_query}
            
            # Formatear detalles
            detalles_json = []
            for d in detalles:
                producto = productos.get(d.id_producto)
                if producto:
                    detalles_json.append({
                        'id': d.id,
                        'producto': {
                            'id': producto.id,
                            'nombre': producto.nombre,
                            'codigo_barras': getattr(producto, 'codigo_barras', 'N/A')
                        },
                        'cantidad': float(d.cantidad),
                        'precio_unitario': float(d.precio_unitario),
                        'subtotal': float(d.subtotal)
                    })
            
            # Obtener notas asociadas (crédito y débito)
            notas_asociadas = factura.obtener_notas_asociadas()
            
            # Preparar respuesta JSON
            factura_json = {
                'id': factura.id,
                'numero_factura': factura.numero_factura,
                'fecha': factura.fecha.isoformat() if factura.fecha else None,
                'subtotal': float(factura.subtotal),
                'iva': float(factura.IVA),
                'total': float(factura.total),
                'cliente': {
                    'id': factura.id_cliente,
                    'nombre': cliente.nombre_cliente if cliente else 'Cliente no especificado'
                },
                'estado': factura.estado,
                'productos': detalles_json,
                'notas_credito': notas_asociadas['notas_credito'],
                'notas_debito': notas_asociadas['notas_debito']
            }
            
            return jsonify({
                'success': True,
                'factura': factura_json
            })
                
        except Exception as e:
            print(f"Error al obtener detalles de factura: {str(e)}")
            session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
                    
    # ===============================
    # API Endpoints para Imprimir y Compartir Facturas
    # ===============================
    
    @route('/api/compartir/<int:factura_id>', methods=['POST'])
    @login_required
    @check_permission('read')
    def compartir_factura(self, factura_id):
        """
        Endpoint para enviar la factura por correo electrónico.
        
        Args:
            factura_id: ID de la factura a compartir
            
        Returns:
            JSON con el resultado del envío
        """
        try:
            datos = request.get_json()
            
            # Validar datos requeridos
            if not datos or 'email' not in datos:
                return jsonify({
                    'success': False,
                    'error': 'Faltan datos requeridos'
                }), 400
                
            email_destino = datos['email']
            asunto = datos.get('asunto', f'Factura #{factura_id} - PERFUMERÍA ELLAS & ELLOS')
            mensaje = datos.get('mensaje', 'Adjuntamos su factura de compra. Gracias por su preferencia.')
            
            # Mostrar mensaje informativo en lugar de enviar por correo
            # ya que no podemos generar PDF sin WeasyPrint
            return jsonify({
                'success': True,
                'message': f'Para compartir la factura, impríme como PDF y envía manualmente a {email_destino}'
            })
            
        except Exception as e:
            self.logger.error(f"Error al compartir factura: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Reemplazamos el método original por uno que muestre un mensaje informativo
    @route('/api/pdf/<int:factura_id>', methods=['GET'])
    @login_required
    @check_permission('read')
    def descargar_pdf_factura(self, factura_id):
        """
        Endpoint para informar sobre la impresión de facturas
        
        Args:
            factura_id: ID de la factura
        """
        try:
            # Redirigir al usuario a la vista de la factura con un parámetro para imprimir
            return redirect(url_for('facturas.ver_factura', factura_id=factura_id, print=True))
            
        except Exception as e:
            self.logger.error(f"Error al redirigir a impresión: {str(e)}")
            flash(f'Error al preparar la factura para impresión: {str(e)}', 'error')
            return redirect(url_for('facturas.index'))
        
    # ===============================
    # Endpoints de Productos
    # ===============================

    @route('/api/productos/barcode/<codigo>', methods=['GET'])
    @login_required
    @check_permission('read')
    def buscar_producto_por_codigo(self, codigo):
        """
        Endpoint para buscar un producto por su código de barras.
        
        Args:
            codigo (str): Código de barras del producto
            
        Returns:
            JSON con la información del producto o mensaje de error
        """
        try:
            session.rollback()
            
            # Imprimir para debugging
            print(f"Buscando producto con código de barras: {codigo}")
            
            # Asegurarnos de que el código sea string y esté limpio
            codigo_limpio = str(codigo).strip()
            
            # Buscar el producto
            producto = session.query(Productos)\
                .filter(Productos.codigo_barras == codigo_limpio)\
                .filter(Productos.activo == True)\
                .first()
                
            # Debugging: imprimir información del producto encontrado
            if producto:
                print(f"Producto encontrado: {producto.__dict__}")
            else:
                print(f"No se encontró producto con código: {codigo_limpio}")
                return jsonify({
                    'success': False,
                    'error': 'Producto no encontrado'
                }), 404

            # Intentar formatear el producto
            producto_formateado = self._formatear_producto(producto)
            
            return jsonify({
                'success': True,
                'producto': producto_formateado
            })

        except Exception as e:
            print(f"Error al buscar producto por código: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @route('/api/productos/buscar/<query>', methods=['GET'])
    @login_required
    @check_permission('read')
    def buscar_productos(self, query):
        """
        Endpoint para búsqueda en tiempo real de productos por nombre.
        """
        try:
            # Limpiar la consulta
            query = query.strip()
            
            # Realizar la búsqueda
            productos = session.query(Productos)\
                .filter(Productos.nombre.ilike(f'%{query}%'))\
                .filter(Productos.activo == True)\
                .limit(5)\
                .all()
                
            # Formatear resultados
            productos_data = [self._formatear_producto(p) for p in productos]
            
            return jsonify({
                'success': True,
                'productos': productos_data
            })
            
        except Exception as e:
            print(f"Error en búsqueda de productos: {str(e)}")
            session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @route('/api/productos/stock/<int:id_producto>', methods=['GET'])
    @login_required
    @check_permission('read')
    def verificar_stock(self, id_producto):
        """Endpoint para verificar el stock disponible de un producto."""
        try:
            producto = session.query(Productos).get(id_producto)
            if not producto:
                return jsonify({
                    'success': False,
                    'error': 'Producto no encontrado'
                }), 404

            return jsonify({
                'success': True,
                'stock': producto.stock_actual
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    # ===============================
    # Métodos Auxiliares
    # ===============================

    def _obtener_clientes_activos(self):
        """
        Obtiene la lista de clientes activos con manejo de errores mejorado.
        
        Returns:
            Lista de clientes activos o lista vacía en caso de error
        """
        try:
            return session.query(Cliente)\
                .filter_by(activo=True)\
                .order_by(Cliente.nombre_cliente)\
                .all()
        except Exception as e:
            print(f"Error al obtener clientes: {str(e)}")
            session.rollback()
            return []

    def _obtener_empleados_activos(self):
        """Obtiene la lista de empleados activos."""
        try:
            return session.query(Empleado).filter_by(activo=True).all()
        except Exception as e:
            print(f"Error al obtener empleados: {str(e)}")
            return []

    def _validar_datos_factura(self, datos):
        """Valida que estén todos los datos requeridos para crear una factura."""
        campos_requeridos = ['id_cliente', 'productos', 'subtotal', 'iva']
        if not all(key in datos for key in campos_requeridos):
            return False
            
        # Validar que el id_cliente no esté vacío
        if not datos['id_cliente']:
            return False
            
        # Validar que haya productos
        if not datos['productos'] or not isinstance(datos['productos'], list):
            return False
            
        return True

    def _obtener_resolucion_activa(self):
        """Obtiene la resolución DIAN activa."""
        return session.query(ResolucionDIAN)\
            .filter_by(activa=True)\
            .first()

    def _crear_factura(self, datos, resolucion):
        """Crea una nueva instancia de Factura con los datos proporcionados."""
        # Obtener el ID del empleado de la sesión, probando diferentes claves posibles
        empleado_id = flask_session.get('empleado_id')
        
        # Si no se encuentra con 'empleado_id', intentar con 'user_id'
        if empleado_id is None:
            empleado_id = flask_session.get('user_id')
            
        # Si aún no tenemos ID, lanzar un error claro
        if empleado_id is None:
            raise ValueError("No se pudo determinar el ID del empleado desde la sesión")
        
        # Verificar que el subtotal y el IVA sean coherentes con los productos
        subtotal = datos['subtotal']
        iva = datos['iva']
        
        # Crear la factura con el ID del empleado correcto
        factura = Factura(
            fecha=date.today(),
            subtotal=datos['subtotal'],
            IVA=datos['iva'],
            id_cliente=datos['id_cliente'],
            id_empleado=empleado_id,  # Usamos el ID que obtuvimos de la sesión
            id_resolucion=resolucion.id_resolucion
        )
        
        # Si hay forma de pago en los datos, la guardamos
        if 'forma_pago' in datos and datos['forma_pago']:
            try:
                # Buscar el método de pago por nombre
                metodo_pago = session.query(MetodoDePago).filter_by(nombre_metodo=datos['forma_pago']).first()
                if metodo_pago:
                    print(f"Método de pago encontrado: {metodo_pago.nombre_metodo} (ID: {metodo_pago.id_metodo_pago})")
                    
                    # Agregar el método de pago a la relación
                    if not hasattr(factura, 'metodos_pago') or factura.metodos_pago is None:
                        factura.metodos_pago = []
                    
                    factura.metodos_pago.append(metodo_pago)
                    print(f"Método de pago agregado a la factura")
                    
                    # Después de crear la factura y hacer flush, también insertar en la tabla intermedia con SQL directo
                    session.flush()  # Asegurarse de que la factura tenga un ID
                    
                    try:
                        from sqlalchemy import text
                        
                        # Verificar si ya existe la relación
                        check_sql = text("""
                            SELECT id FROM factura_metodo_de_pago 
                            WHERE id = :id_factura AND id_metodo_pago = :id_metodo_pago
                        """)
                        existing = session.execute(check_sql, {
                            "id_factura": factura.id,
                            "id_metodo_pago": metodo_pago.id_metodo_pago
                        }).first()
                        
                        if not existing:
                            # Insertar directamente en la tabla intermedia
                            insert_sql = text("""
                                INSERT INTO factura_metodo_de_pago (id, id_metodo_pago)
                                VALUES (:id_factura, :id_metodo_pago)
                            """)
                            
                            session.execute(insert_sql, {
                                "id_factura": factura.id,
                                "id_metodo_pago": metodo_pago.id_metodo_pago
                            })
                            
                            print(f"Relación creada manualmente entre factura {factura.id} y método de pago {metodo_pago.id_metodo_pago}")
                    except Exception as e:
                        print(f"Error al crear relación manual: {str(e)}")
                        
                else:
                    print(f"Método de pago '{datos['forma_pago']}' no encontrado, se usará un valor predeterminado")
            except Exception as e:
                print(f"Error al asignar método de pago: {str(e)}")
        
        return factura

    def _formatear_factura(self, factura):
        """Formatea los datos de una factura para la respuesta JSON."""
        return {
            'id': factura.id,
            'numero_factura': factura.numero_factura,
            'fecha': factura.fecha.isoformat(),
            'total': float(factura.total),
            'estado': factura.estado
        }

    def _formatear_producto(self, producto):
        """
        Formatea los datos de un producto para la respuesta JSON.
        """
        try:
            # Convertimos a float el precio para asegurar precisión en los cálculos
            precio = float(producto.precio if producto.precio is not None else 0)
            
            return {
                'id': producto.id,                    # ID único del producto
                'nombre': producto.nombre,            # Nombre del producto
                'precio': precio,                     # Precio de venta
                'porcentajeIVA': 19.0,               # IVA estándar en Colombia (19%)
                'codigo_barras': producto.codigo_barras,  # Código de barras para identificación
                'stock': producto.stock               # Cantidad disponible
            }
        except AttributeError as e:
            # Log detallado en caso de error para facilitar el debugging
            print(f"Error al formatear producto: {str(e)}")
            print(f"Atributos disponibles en el producto: {dir(producto)}")
            print(f"Valores del producto: {producto.__dict__}")
            raise ValueError(f"Error al acceder a los datos del producto: {str(e)}")
        
    def _convertir_numero_a_letras(self, numero):
        """
        Convierte un número a su representación en letras.
        """
        try:
            # Convertir el número a letras en español
            # Usando la biblioteca num2words
            texto = num2words(float(numero), lang='es')
            
            # Capitalizar la primera letra
            texto = texto.capitalize()
            
            # Agregar "pesos" al final
            texto += " pesos"
            
            return texto
        except Exception as e:
            self.logger.error(f"Error al convertir número a letras: {str(e)}")
            return f"{float(numero):.2f} pesos"
    
    # Simplificamos _enviar_email para evitar la dependencia de un PDF real
    def _enviar_email(self, email_destino, asunto, mensaje, archivo_adjunto=None):
        """
        Simulación de envío de correo - en un entorno real se enviaría el PDF.
        """
        try:
            self.logger.info(f"Simulando envío de correo a {email_destino}")
            return True
        except Exception as e:
            self.logger.error(f"Error al simular envío de correo: {str(e)}")
            raise
        
    @route('/logout', methods=['GET'])
    def logout(self):
        # Limpiar la sesión
        session.clear()
        # Redirigir al login
        return redirect(url_for('auth.login'))
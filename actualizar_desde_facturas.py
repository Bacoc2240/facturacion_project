#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para actualizar el historial de compras y preferencias de clientes
basado en las facturas existentes.
"""

import sys
import os
import time
from datetime import datetime

# Asegurar que podamos importar desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Importaciones directas para evitar problemas de contexto
from src.models import session
from sqlalchemy import text

def actualizar_historiales_desde_facturas():
    """
    Actualiza el historial de compras y preferencias de clientes
    basado en las facturas existentes.
    """
    try:
        # 1. Obtener todas las facturas activas
        facturas_query = text("""
            SELECT id, numero_factura, fecha, id_cliente
            FROM factura
            WHERE activa = TRUE
            ORDER BY fecha, numero_factura
        """)
        
        facturas = session.execute(facturas_query).fetchall()
        print(f"Se encontraron {len(facturas)} facturas activas.")
        
        # 2. Mapear clientes a sus historiales de compras
        historiales_clientes = {}
        
        # 3. Procesar cada factura
        for factura in facturas:
            # Obtener los detalles de la factura
            detalles_query = text("""
                SELECT df.id_producto, df.cantidad, p.nombre
                FROM detalle_factura df
                JOIN productos p ON df.id_producto = p.id
                WHERE df.id_factura = :id_factura
            """)
            
            detalles = session.execute(detalles_query, {"id_factura": factura.id}).fetchall()
            
            if not detalles:
                print(f"No se encontraron detalles para la factura #{factura.numero_factura}")
                continue
                
            # Formatear fecha
            fecha_str = factura.fecha.strftime('%Y-%m-%d') if isinstance(factura.fecha, datetime) else str(factura.fecha)
            
            # Construir lista de productos para esta factura
            productos_comprados = []
            for detalle in detalles:
                if hasattr(detalle, 'nombre') and detalle.nombre:
                    producto_nombre = detalle.nombre
                    cantidad = detalle.cantidad
                    productos_comprados.append(f"{producto_nombre} (x{cantidad})")
            
            # Si hay productos, crear entrada para el historial
            if productos_comprados:
                entrada_historial = f"{fecha_str}, Factura #{factura.numero_factura}: {' | '.join(productos_comprados)}"
                
                # Agregar al historial del cliente
                if factura.id_cliente not in historiales_clientes:
                    historiales_clientes[factura.id_cliente] = []
                
                historiales_clientes[factura.id_cliente].append(entrada_historial)
        
        # 4. Actualizar el historial de cada cliente
        actualizados = 0
        for id_cliente, entradas in historiales_clientes.items():
            # Obtener historial actual
            cliente_query = text("""
                SELECT historial_compras
                FROM cliente
                WHERE id_cliente = :id_cliente
            """)
            
            cliente_result = session.execute(cliente_query, {"id_cliente": id_cliente}).fetchone()
            
            if cliente_result:
                historial_actual = cliente_result.historial_compras or ""
                
                # Construir nuevo historial
                nuevo_historial = historial_actual
                
                # Agregar nuevas entradas, evitando duplicados
                for entrada in entradas:
                    if entrada not in historial_actual:
                        if nuevo_historial:
                            nuevo_historial += "\n"
                        nuevo_historial += entrada
                
                # Actualizar historial en la base de datos
                if nuevo_historial != historial_actual:
                    update_query = text("""
                        UPDATE cliente
                        SET historial_compras = :historial
                        WHERE id_cliente = :id_cliente
                    """)
                    
                    session.execute(update_query, {
                        "historial": nuevo_historial,
                        "id_cliente": id_cliente
                    })
                    
                    print(f"Cliente {id_cliente}: Historial actualizado")
                    actualizados += 1
                else:
                    print(f"Cliente {id_cliente}: Sin cambios en el historial")
        
        # 5. Commit de los cambios
        session.commit()
        print(f"Se actualizaron los historiales de {actualizados} clientes.")
        
        # 6. Actualizar preferencias basadas en los nuevos historiales
        print("\nActualizando preferencias basadas en los nuevos historiales...")
        
        # Reutilizar la lógica del script anterior para actualizar preferencias
        actualizar_preferencias_para_ids = list(historiales_clientes.keys())
        
        # Obtener clientes actualizados
        clientes_query = text("""
            SELECT id_cliente, nombre_cliente, historial_compras, preferencias
            FROM cliente
            WHERE id_cliente IN :ids
        """)
        
        clientes = session.execute(clientes_query, {"ids": tuple(actualizar_preferencias_para_ids)}).fetchall()
        
        preferencias_actualizadas = 0
        for cliente in clientes:
            if cliente.historial_compras:
                preferencia_antigua = cliente.preferencias if cliente.preferencias else "No aplica"
                
                # Calcular nueva preferencia
                nueva_preferencia = calcular_producto_preferido(cliente.historial_compras)
                
                # Actualizar si hay cambios
                if nueva_preferencia != preferencia_antigua:
                    update_query = text("""
                        UPDATE cliente
                        SET preferencias = :preferencia
                        WHERE id_cliente = :id_cliente
                    """)
                    
                    session.execute(update_query, {
                        "preferencia": nueva_preferencia,
                        "id_cliente": cliente.id_cliente
                    })
                    
                    print(f"Cliente {cliente.id_cliente} - {cliente.nombre_cliente}: Preferencia actualizada de '{preferencia_antigua}' a '{nueva_preferencia}'")
                    preferencias_actualizadas += 1
                else:
                    print(f"Cliente {cliente.id_cliente} - {cliente.nombre_cliente}: Preferencia sin cambios ('{preferencia_antigua}')")
        
        # Commit final
        session.commit()
        print(f"Se actualizaron las preferencias de {preferencias_actualizadas} clientes.")
        
        return actualizados
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            session.rollback()
        except:
            pass
        return 0

def calcular_producto_preferido(historial_compras):
    """
    Calcula el producto más comprado a partir del historial de compras.
    """
    try:
        # Separar el historial en productos individuales
        productos = []
        for linea in historial_compras.split('\n'):
            # Ignorar la fecha y el número de factura
            if ',' in linea and ':' in linea:
                # Obtener la parte después de los dos puntos (lista de productos)
                productos_parte = linea.split(':', 1)[1].strip()
                
                # Dividir en productos individuales y limpiar
                for producto_raw in productos_parte.split(','):
                    # Extraer solo el nombre del producto (sin la cantidad entre paréntesis)
                    if '(' in producto_raw and ')' in producto_raw:
                        producto = producto_raw.split('(')[0].strip()
                        productos.append(producto)
                    else:
                        productos.append(producto_raw.strip())
        
        if not productos:
            return "No aplica"
            
        # Contar frecuencia de productos
        from collections import Counter
        conteo = Counter(productos)
        
        # Obtener el más frecuente
        producto_frecuente = conteo.most_common(1)
        return producto_frecuente[0][0] if producto_frecuente else "No aplica"
        
    except Exception as e:
        print(f"Error al calcular producto preferido: {e}")
        return "No aplica"

if __name__ == "__main__":
    print("Iniciando actualización de historiales y preferencias desde facturas existentes...")
    count = actualizar_historiales_desde_facturas()
    print(f"\nProceso finalizado. Se procesaron datos para {count} clientes.")
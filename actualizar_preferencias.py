#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para actualizar las preferencias de todos los clientes
basado en su historial de compras actual.
"""

import sys
import os
import time

# Asegurar que podamos importar desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Importaciones directas para evitar problemas de contexto
from src.models import session
import sqlalchemy

def actualizar_preferencias_todos_clientes():
    """
    Recorre todos los clientes activos y actualiza sus preferencias
    basándose en el historial de compras actual.
    """
    try:
        # Consultar todos los clientes activos usando SQL directo
        from sqlalchemy import text
        
        # Obtener todos los clientes con consulta SQL directa
        result = session.execute(text("SELECT id_cliente, tipo_documento, nombre_cliente, historial_compras, preferencias FROM cliente WHERE activo = TRUE"))
        
        # Convertir el resultado a una lista que podamos usar
        clientes = [
            {
                'id_cliente': row.id_cliente,
                'tipo_documento': row.tipo_documento,
                'nombre_cliente': row.nombre_cliente,
                'historial_compras': row.historial_compras,
                'preferencias': row.preferencias if hasattr(row, 'preferencias') else None
            }
            for row in result
        ]
        
        print(f"Se encontraron {len(clientes)} clientes activos.")
        
        actualizado_count = 0
        error_count = 0
        
        # Procesar cada cliente
        for i, cliente in enumerate(clientes, 1):
            print(f"\nCliente {i}/{len(clientes)}: {cliente['id_cliente']} - {cliente['nombre_cliente']}")
            
            try:
                historial_compras = cliente['historial_compras']
                
                if historial_compras:
                    # Guardar preferencia anterior para comparación
                    preferencia_antigua = cliente['preferencias'] if cliente['preferencias'] else "No definida"
                    
                    # Calcular la nueva preferencia manualmente
                    nueva_preferencia = "No aplica"
                    try:
                        # Separar el historial en productos individuales
                        productos = [
                            producto.strip()
                            for linea in historial_compras.split('\n')
                            for producto in linea.split(',')
                            if producto.strip()
                        ]

                        if productos:
                            # Contar frecuencia de productos
                            from collections import Counter
                            conteo = Counter(productos)
                            
                            # Obtener el más frecuente
                            producto_frecuente = conteo.most_common(1)
                            nueva_preferencia = producto_frecuente[0][0] if producto_frecuente else "No aplica"
                    except Exception as e:
                        print(f"  Error al calcular preferencias: {e}")
                        nueva_preferencia = "No aplica"
                    
                    print(f"  Preferencia anterior: {preferencia_antigua}")
                    print(f"  Preferencia nueva: {nueva_preferencia}")
                    
                    # Actualizar en la base de datos directamente usando SQL
                    try:
                        update_stmt = text("""
                            UPDATE cliente 
                            SET preferencias = :preferencia 
                            WHERE id_cliente = :id_cliente
                        """)
                        
                        session.execute(update_stmt, {
                            "preferencia": nueva_preferencia,
                            "id_cliente": cliente['id_cliente']
                        })
                        
                        if preferencia_antigua != nueva_preferencia:
                            print(f"  => ACTUALIZADO")
                        else:
                            print(f"  => Sin cambios")
                        
                        actualizado_count += 1
                    except Exception as e:
                        print(f"  Error al actualizar base de datos: {e}")
                        error_count += 1
                else:
                    print(f"  No tiene historial de compras.")
                    # Actualizar a "No aplica" si no hay historial
                    try:
                        update_stmt = text("""
                            UPDATE cliente 
                            SET preferencias = 'No aplica' 
                            WHERE id_cliente = :id_cliente
                        """)
                        
                        session.execute(update_stmt, {
                            "id_cliente": cliente['id_cliente']
                        })
                        
                        print(f"  => Preferencia establecida a 'No aplica'")
                        actualizado_count += 1
                    except Exception as e:
                        print(f"  Error al actualizar base de datos: {e}")
                        error_count += 1
            
            except Exception as e:
                error_count += 1
                print(f"  ERROR: {str(e)}")
                
            # Pequeña pausa para no sobrecargar la base de datos
            if i % 10 == 0:
                time.sleep(0.1)
        
        # Guardar todos los cambios
        try:
            session.commit()
            print("\nCambios guardados en la base de datos.")
        except Exception as e:
            print(f"\nError al guardar cambios: {str(e)}")
            session.rollback()
        
        # Mostrar resumen
        print("\n==== RESUMEN ====")
        print(f"Total de clientes procesados: {len(clientes)}")
        print(f"Clientes actualizados: {actualizado_count}")
        print(f"Errores: {error_count}")
        
        return actualizado_count
    
    except Exception as e:
        print(f"Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            session.rollback()
        except:
            pass
        return 0

if __name__ == "__main__":
    print("Iniciando actualización de preferencias de clientes...")
    try:
        count = actualizar_preferencias_todos_clientes()
    except Exception as e:
        print(f"Error al ejecutar la actualización: {e}")
        count = 0
    print(f"\nProceso finalizado. Se actualizaron {count} clientes.")
from alembic import op
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from src.models import Base, session, engine
from src.models.usuario import Usuario, RolUsuario
from src.models.empleado import Empleado
import bcrypt

def crear_empleados_iniciales():
    """Crear empleados iniciales si no existen"""
    empleados_data = [
        {
            'nombre': 'Admin Principal',
            'documento': '1000000001',
            'cargo': 'Administrador',
            'email': 'admin@empresa.com'
        },
        {
            'nombre': 'Vendedor Principal',
            'documento': '1000000002',
            'cargo': 'Vendedor',
            'email': 'vendedor@empresa.com'
        },
        {
            'nombre': 'Inventarista Principal',
            'documento': '1000000003',
            'cargo': 'Inventarista',
            'email': 'inventario@empresa.com'
        },
        {
            'nombre': 'Visualizador Principal',
            'documento': '1000000004',
            'cargo': 'Visualizador',
            'email': 'visualizador@empresa.com'
        }
    ]

    empleados = []
    for data in empleados_data:
        empleado = session.query(Empleado).filter_by(documento=data['documento']).first()
        if not empleado:
            empleado = Empleado(
                nombre=data['nombre'],
                documento=data['documento'],
                cargo=data['cargo'],
                email=data['email']
            )
            session.add(empleado)
            session.flush()  # Para obtener el id generado
        empleados.append(empleado)

    session.commit()
    return empleados

def crear_usuarios_iniciales(empleados):
    """Crear usuarios iniciales con sus respectivos roles"""
    usuarios_data = [
        {
            'nombre_usuario': 'admin',
            'contraseña': 'admin123',  # Cambiar en producción
            'rol': RolUsuario.ADMIN,
            'empleado': empleados[0]
        },
        {
            'nombre_usuario': 'vendedor1',
            'contraseña': 'vendedor123',  # Cambiar en producción
            'rol': RolUsuario.VENDEDOR,
            'empleado': empleados[1]
        },
        {
            'nombre_usuario': 'inventario1',
            'contraseña': 'inventario123',  # Cambiar en producción
            'rol': RolUsuario.INVENTARIO,
            'empleado': empleados[2]
        },
        {
            'nombre_usuario': 'visualizador1',
            'contraseña': 'visualizador123',  # Cambiar en producción
            'rol': RolUsuario.VISUALIZADOR,
            'empleado': empleados[3]
        }
    ]

    for data in usuarios_data:
        usuario = session.query(Usuario).filter_by(
            nombre_usuario=data['nombre_usuario']
        ).first()

        if not usuario:
            usuario = Usuario(
                nombre_usuario=data['nombre_usuario'],
                contraseña=data['contraseña'],
                rol=data['rol'],
                id_empleado=data['empleado'].id_empleado
            )
            session.add(usuario)

    session.commit()

def ejecutar_migracion():
    """Ejecutar la migración completa"""
    print("Iniciando migración...")

    # Crear todas las tablas si no existen
    Base.metadata.create_all(engine)

    print("Creando empleados iniciales...")
    empleados = crear_empleados_iniciales()

    print("Creando usuarios iniciales...")
    crear_usuarios_iniciales(empleados)

    print("Migración completada exitosamente!")

# 2. Script de ejecución (run_migration.py)
if __name__ == '__main__':
    try:
        ejecutar_migracion()
    except Exception as e:
        print(f"Error durante la migración: {str(e)}")
        session.rollback()
    finally:
        session.close()

# 3. Script para verificar la migración (verify_migration.py)
def verificar_migracion():
    """Verificar que la migración se realizó correctamente"""
    try:
        # Verificar usuarios
        usuarios = session.query(Usuario).all()
        print("\nUsuarios creados:")
        for usuario in usuarios:
            print(f"- {usuario.nombre_usuario} (Rol: {usuario.rol.value})")

        # Verificar roles
        roles = set(usuario.rol for usuario in usuarios)
        print("\nRoles disponibles:")
        for rol in roles:
            print(f"- {rol.value}")

        # Verificar que los campos nuevos estén presentes
        usuario = usuarios[0]
        print("\nCampos nuevos:")
        print(f"- ultima_sesion: {usuario.ultima_sesion}")
        print(f"- fecha_creacion: {usuario.fecha_creacion}")

    except Exception as e:
        print(f"Error durante la verificación: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    verificar_migracion()
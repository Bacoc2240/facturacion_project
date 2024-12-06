# verify_migration.py

from src.models import session
from src.models.usuario import Usuario

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

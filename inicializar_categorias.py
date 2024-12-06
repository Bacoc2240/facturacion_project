from src.models import session
from src.models.categorias import Categorias


# Verificar si ya existen categorías en la tabla
categorias_existentes = session.query(Categorias).count()
if categorias_existentes == 0:
    categorias_iniciales = [
        Categorias(categoria='Perfumes'),
        Categorias(categoria='Ambientadores'),
        Categorias(categoria='Accesorios')
    ]

    # Agregar las categorías iniciales a la sesión y hacer commit
    session.add_all(categorias_iniciales)
    session.commit()
    print("Categorías iniciales creadas exitosamente.")
else:
    print("Ya existen categorías en la base de datos.")



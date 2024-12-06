import os

# Guárdalo como check_structure.py y ejecútalo
def check_project_structure():
    print("Verificando estructura del proyecto...")
    
    # Verifica el directorio actual
    print(f"Directorio actual: {os.getcwd()}")
    
    # Verifica la existencia de directorios clave
    paths_to_check = [
        "src/templates",
        "src/controllers",
        "src/models"
    ]
    
    for path in paths_to_check:
        full_path = os.path.join(os.getcwd(), path)
        exists = os.path.exists(full_path)
        print(f"¿Existe {path}?: {'Sí' if exists else 'No'}")
        
        if path == "src/templates":
            # Verifica si login.html existe
            login_path = os.path.join(full_path, "login.html")
            login_exists = os.path.exists(login_path)
            print(f"¿Existe login.html?: {'Sí' if login_exists else 'No'}")
            if login_exists:
                print(f"Ruta completa a login.html: {login_path}")

if __name__ == "__main__":
    check_project_structure()
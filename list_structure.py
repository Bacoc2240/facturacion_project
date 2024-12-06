# save as list_structure.py
import os

def list_directory_structure(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

if __name__ == "__main__":
    # Ajusta esta ruta a la ubicación de tu proyecto
    project_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Project path: {project_path}")
    list_directory_structure(project_path)
    

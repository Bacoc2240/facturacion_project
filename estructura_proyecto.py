#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse

def print_directory_structure(startpath, exclude_dirs=None, exclude_files=None, output_file=None):
    """
    Imprime la estructura de directorios desde la ruta startpath.
    
    Args:
        startpath (str): Ruta inicial desde donde comenzar a imprimir la estructura.
        exclude_dirs (list): Lista de nombres de directorios a excluir.
        exclude_files (list): Lista de nombres de archivos a excluir.
        output_file (str): Archivo donde guardar la estructura, si es None se imprime por consola.
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'venv', 'env', '.venv', '.env', 'node_modules']
    
    if exclude_files is None:
        exclude_files = ['.pyc', '.pyo', '.pyd', '.git', '.DS_Store']
    
    output_lines = []
    
    # Añadir encabezado
    output_lines.append(f"Estructura del proyecto: {os.path.basename(startpath)}")
    output_lines.append("=" * 50)
    
    for root, dirs, files in os.walk(startpath):
        # Excluir directorios no deseados
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not any(d.endswith(ed) for ed in exclude_dirs)]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        output_lines.append(f"{indent}├── {os.path.basename(root)}/")
        
        sub_indent = '│   ' * (level + 1)
        
        # Ordenar archivos alfabéticamente
        files.sort()
        
        for i, file in enumerate(files):
            # Excluir archivos no deseados
            if any(file.endswith(ef) for ef in exclude_files):
                continue
                
            if i == len(files) - 1:
                output_lines.append(f"{sub_indent}└── {file}")
            else:
                output_lines.append(f"{sub_indent}├── {file}")
    
    # Unir todas las líneas
    output_text = "\n".join(output_lines)
    
    # Guardar en archivo o imprimir por consola
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Estructura guardada en: {output_file}")
    else:
        print(output_text)
    
    return output_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Imprime la estructura de directorios de un proyecto.')
    parser.add_argument('-p', '--path', default='.', help='Ruta del proyecto (por defecto: directorio actual)')
    parser.add_argument('-o', '--output', help='Archivo donde guardar la estructura')
    parser.add_argument('-ed', '--exclude-dirs', nargs='+', help='Directorios adicionales a excluir')
    parser.add_argument('-ef', '--exclude-files', nargs='+', help='Extensiones de archivo adicionales a excluir')
    
    args = parser.parse_args()
    
    exclude_dirs = ['.git', '__pycache__', 'venv', 'env', '.venv', '.env', 'node_modules']
    exclude_files = ['.pyc', '.pyo', '.pyd', '.git', '.DS_Store']
    
    if args.exclude_dirs:
        exclude_dirs.extend(args.exclude_dirs)
    
    if args.exclude_files:
        exclude_files.extend(args.exclude_files)
    
    print_directory_structure(args.path, exclude_dirs, exclude_files, args.output)
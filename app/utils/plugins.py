import os
import importlib.util
import streamlit as st

def obtener_plugins(tipo):
    """
    Carga todos los plugins desde una subcarpeta bajo 'plugins' correspondiente al tipo dado.
    
    Args:
        tipo (str): El nombre de la subcarpeta en 'plugins' donde están los plugins (ejemplo: "stocks").
    
    Returns:
        list[dict]: Una lista de diccionarios con la información de cada plugin (nombre, descripcion, tipo, render).
    """
    plugins_dir = os.path.join("plugins", tipo)
    plugins = []

    if not os.path.exists(plugins_dir):
        raise FileNotFoundError(f"No se encontró el directorio '{plugins_dir}'.")

    for archivo in os.listdir(plugins_dir):
        # Ignorar directorios __pycache__
        if archivo == "__pycache__":
            continue

        ruta_plugin = os.path.join(plugins_dir, archivo)
        # Solo procesar si es un directorio y contiene un archivo Python con el mismo nombre
        if os.path.isdir(ruta_plugin):
            plugin_file = os.path.join(ruta_plugin, f"{archivo}.py")
            if not os.path.exists(plugin_file):
                continue  # Omitir si el archivo Python no existe

            plugin_name = os.path.splitext(archivo)[0]
            
            # Cargar el módulo dinámicamente
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Verificar que el plugin tenga los atributos requeridos
            if hasattr(module, "nombre") and hasattr(module, "descripcion") and hasattr(module, "tipo") and hasattr(module, "render"):
                plugins.append({
                    "nombre": module.nombre,
                    "descripcion": module.descripcion,
                    "tipo": module.tipo,
                    "render": module.render,
                    "module": module,  # Incluye el módulo completo
                })
            else:
                st.toast(f"El plugin '{plugin_name}' no tiene los atributos necesarios y será omitido.")
    
    return plugins

import os
import importlib.util

def load_widgets(folder=""):
    """
    Carga dinámicamente todos los archivos .py en 'folder'
    como módulos de Python, retornando una lista de módulos.
    """
    if not folder:
        # Si no especificas nada, por defecto usamos la misma carpeta donde está este script
        folder = os.path.dirname(__file__)

    indicator_modules = []
    # Recorremos los archivos de la carpeta
    for file in os.listdir(folder):
        if file.endswith(".py") and file != "__init__.py" and file != "load_indicators.py":
            file_path = os.path.join(folder, file)                # Ruta absoluta
            module_name = os.path.splitext(file)[0]              # Nombre sin ".py"

            print(f"Cargando archivo: {file_path}")

            # 1) Creamos un spec a partir de la ruta
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            # 2) Creamos un módulo vacío usando ese spec
            module = importlib.util.module_from_spec(spec)
            # 3) Ejecutamos (load) el código del .py dentro del módulo
            spec.loader.exec_module(module)

            # Agregamos el módulo a la lista
            indicator_modules.append(module)

    return indicator_modules
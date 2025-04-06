import streamlit as st
from utils.config_manager import ConfigManager
from utils.plugins import obtener_plugins
from streamlit_theme import st_theme

def render():
    st.subheader("Dashboard")
    
    # Cargar configuración global del dashboard
    config_path = "config.yaml"
    config = ConfigManager(config_path)
    
    # Obtener número de columnas desde la configuración
    num_columnas = config.get("dashboard.num_columnas", 2)
    
    # Cargar todos los plugins de tipo "dashboard" (o varios tipos, si lo deseas)
    plugins = obtener_plugins("dashboard")
    
    # Recuperar la configuración de los widgets definidos en dashboard.widget
    widgets_config = config.get("dashboard.widget", {})
    
    if not widgets_config:
        st.warning("No hay widgets configurados en 'dashboard.widget'.")
        return
    
    # Ordenar los widgets por la propiedad "position" (valor por defecto 0 si no existe)
    widget_items = sorted(widgets_config.items(), key=lambda x: x[1].get("position", 0))
    
    # Crear columnas para mostrar los widgets
    columnas = st.columns(num_columnas)
    
    # Detectar el tema para ajustar colores en los plugins
    theme = st_theme()
    is_dark = (theme.get("base") == "dark") if theme is not None else True

    # Iterar por cada widget ordenado
    for i, (widget_name, widget_conf) in enumerate(widget_items):
        widget_type = widget_conf.get("type")
        if not widget_type:
            st.error(f"El widget '{widget_name}' no tiene la propiedad 'type'.")
            continue
        
        # Buscar un plugin cuyo "tipo" coincida con el definido en la config del widget
        plugin = next((p for p in plugins if p["tipo"] == widget_type), None)
        if plugin is None:
            st.error(f"No se encontró un plugin para '{widget_name}' con tipo '{widget_type}'.")
            continue
        
        with columnas[i % num_columnas]:
            # Si se definió "height" en la configuración, se pasa al contenedor
            if "height" in widget_conf:
                height_val = widget_conf["height"]
                with st.container(height=height_val):
                    widget_conf["is_dark"] = is_dark
                    plugin["render"](widget_conf)
            else:
                with st.container(border=True):
                    widget_conf["is_dark"] = is_dark
                    plugin["render"](widget_conf)

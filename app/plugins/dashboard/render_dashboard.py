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
    
    widget_items = list(widgets_config.items())
    
    # Crear columnas para mostrar los widgets
    columnas = st.columns(num_columnas)
    
    # Detectar el tema para ajustar colores en los plugins
    theme = st_theme()
    if theme is not None:
        is_dark = (theme.get("base") == "dark")
    else:
        is_dark = True  # Valor por defecto si no se puede detectar el tema

    # Iterar por cada widget
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
        
        # Mostrar el widget en la columna correspondiente
        with columnas[i % num_columnas]:
            with st.container():
                # Pasar is_dark para que el plugin ajuste sus colores
                widget_conf["is_dark"] = is_dark
                plugin["render"](widget_conf)

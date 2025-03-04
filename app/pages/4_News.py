import streamlit as st
from utils.plugins import obtener_plugins
import utils.set_logo as set_logo

set_logo.set_logo()

# Obtener y mostrar plugins para noticias
plugins = obtener_plugins("news")

if plugins:
    st.sidebar.write("### Selección de plugin")
    selected_plugin_name = st.sidebar.selectbox(
        "Selecciona un plugin:",
        [plugin["nombre"] for plugin in plugins],
        index=0  # Cargar automáticamente el primer plugin
    )
    
    # Mostrar detalles del plugin seleccionado
    selected_plugin = next(
        (plugin for plugin in plugins if plugin["nombre"] == selected_plugin_name),
        None
    )
    
    if selected_plugin and selected_plugin.get("render"):
        selected_plugin["render"]()

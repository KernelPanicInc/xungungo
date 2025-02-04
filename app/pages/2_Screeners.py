import streamlit as st
from utils.config_manager import ConfigManager
from utils.plugins import obtener_plugins
from pages.screeners.screeners_config import render_screeners_config
from pages.screeners.dialog_config import render_dialog
from pages.screeners.dialog_agregar_screener import render_dialog_agregar_screener
import utils.set_logo as set_logo


set_logo.set_logo()
# Cargar configuración
config = ConfigManager("config.yaml")
screeners = config.get("screener", [])

# Definir un menú lateral con las opciones
st.sidebar.title("Screeners")

# Botón para abrir el diálogo de "Agregar nuevo Screener"
if st.sidebar.button("Agregar nuevo Screener", key="btn_agregar_screener"):
    render_dialog_agregar_screener(config)


screener_names = [screener.get("nombre", "Desconocido") for screener in screeners]
selected_screener = st.sidebar.selectbox("Seleccione un Screener", screener_names)

# Buscar la configuración del screener seleccionado
screener_config = next((s for s in screeners if s.get("nombre") == selected_screener), None)

if screener_config:
    screener_type = screener_config.get("tipo", "")
    plugins = obtener_plugins("screeners")
    # Buscar el plugin correspondiente al screener seleccionado
    plugin = next((p for p in plugins if p["tipo"] == screener_type), None)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### Screener seleccionado: {selected_screener}")
    with col2:
        st.button("Config", key="update_screener", icon=":material/settings:", on_click=render_dialog, args=(plugin,screener_config,config,))

    if plugin:
        # Ejecutar la función render del plugin
        plugin["render"](screener_config)
    else:
        st.error(f"No se encontró un plugin válido para el screener de tipo: {screener_type}.")
else:
    st.warning("No hay screeners configurados en el archivo YAML.")


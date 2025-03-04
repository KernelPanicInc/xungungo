import streamlit as st
from streamlit_searchbox import st_searchbox
from models.datasource.yahoo_datasource import search_service
from utils.plugins import obtener_plugins
import utils.set_logo as set_logo

set_logo.set_logo()

# 1) Inicializa contadores y selección en session_state
if "refresh_counter" not in st.session_state:
    st.session_state["refresh_counter"] = 0
if "selected_plugin" not in st.session_state:
    st.session_state["selected_plugin"] = None

selected_value = st_searchbox(
    search_service,
    placeholder="Search Symbol...",
    key="yahoo_ticker",
    debounce=1000,
)

if selected_value:
    plugins = obtener_plugins("stocks")

    # Muestra el selectbox de plugins
    st.sidebar.write("### Selección de plugin")
    plugin_names = [p["nombre"] for p in plugins]

    # Selecciona el plugin; si no hay uno en session_state, coge el primero de la lista
    if st.session_state["selected_plugin"] not in plugin_names:
        # Primer arranque o el plugin previo ya no existe
        st.session_state["selected_plugin"] = plugin_names[0] if plugin_names else None

    selected_plugin_name = st.sidebar.selectbox(
        "Selecciona un plugin:",
        plugin_names,
        index=plugin_names.index(st.session_state["selected_plugin"]) 
               if st.session_state["selected_plugin"] in plugin_names else 0
    )

    # 2) Si cambia el plugin, forzamos un “refresh”
    if selected_plugin_name != st.session_state["selected_plugin"]:
        st.session_state["selected_plugin"] = selected_plugin_name
        st.session_state["refresh_counter"] += 1

    # 3) Botón de refresco
    if st.button("Refresh"):
        st.session_state["refresh_counter"] += 1

    # 4) Renderizar el plugin
    selected_plugin = next(
        (plugin for plugin in plugins if plugin["nombre"] == st.session_state["selected_plugin"]),
        None
    )

    # Generamos una key distinta para el contenedor cada vez que cambiamos el contador
    container_key = f"plugin_render_container_{st.session_state['selected_plugin']}_{st.session_state['refresh_counter']}"

    # Con st.empty() forzamos un contenedor independiente por cada nuevo “refresh_counter”
    container = st.empty()
    with container.container():
        if selected_plugin:
            # Llamamos a la función render del plugin
            selected_plugin.get("render")(selected_value)

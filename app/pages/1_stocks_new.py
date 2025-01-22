import streamlit as st
from streamlit_searchbox import st_searchbox
from models.datasource.yahoo_datasource import search_service
from utils.plugins import obtener_plugins


# pass search function and other options as needed
print("SELECT")
selected_value = st_searchbox(
    search_service,
    placeholder="Search Symbol... ",
    key="yahoo_ticker",
    debounce=1000,
)

if selected_value:
    # Obtener y mostrar plugins
    plugins = obtener_plugins("stocks")
    st.sidebar.write("### Selección de plugin")
    selected_plugin_name = st.sidebar.selectbox(
        "Selecciona un plugin:",
        [plugin["nombre"] for plugin in plugins]
    )

    # Mostrar detalles del plugin seleccionado
    if selected_plugin_name:
        # Encontrar el plugin seleccionado en la lista
        selected_plugin = next(
            (plugin for plugin in plugins if plugin["nombre"] == selected_plugin_name),
            None
        )

        if selected_plugin:
            selected_plugin.get("render")(selected_value)
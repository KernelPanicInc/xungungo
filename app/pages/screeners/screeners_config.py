import streamlit as st
import yaml
from utils.config_manager import ConfigManager
from utils.plugins import obtener_plugins

CONFIG_FILE = "config.yaml"

def cargar_configuracion():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def guardar_configuracion(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, allow_unicode=True)

def obtener_tipos_plugins():
    plugins = obtener_plugins("screeners")
    return [plugin["tipo"] for plugin in plugins]

def obtener_parametros_plugin(tipo):
    plugins = obtener_plugins("screeners")
    plugin = next((p for p in plugins if p["tipo"] == tipo), None)
    if plugin and hasattr(plugin["module"], "get_parametros_config"):
        return plugin["module"].get_parametros_config()
    return {}

def render_screeners_config():
    config = cargar_configuracion()
    screeners = config.get("screener", [])

    st.sidebar.title("Configuración de Screeners")
    modo = st.sidebar.radio("Modo", ["Ver screeners", "Agregar screener"])

    tipos_plugins = obtener_tipos_plugins()

    if modo == "Ver screeners":
        st.title("Configuración de Screeners")
        if not screeners:
            st.warning("No hay screeners configurados.")
        else:
            for i, screener in enumerate(screeners):
                with st.expander(f"Screener {i + 1}: {screener.get('nombre', 'Sin nombre')}"):
                    screener["nombre"] = st.text_input("Nombre", value=screener.get("nombre", ""), key=f"nombre_{i}")
                    screener["tipo"] = st.selectbox("Tipo", tipos_plugins, index=tipos_plugins.index(screener.get("tipo", tipos_plugins[0])), key=f"tipo_{i}")
                    screener["descripcion"] = st.text_area("Descripción", value=screener.get("descripcion", ""), key=f"descripcion_{i}")

                    parametros = obtener_parametros_plugin(screener["tipo"])
                    for param, detalles in parametros.items():
                        screener[param] = st.text_input(
                            detalles.get("label", param),
                            value=screener.get(param, detalles.get("default", "")),
                            key=f"{param}_{i}"
                        )

            if st.button("Guardar cambios"):
                guardar_configuracion(config)
                st.success("¡Cambios guardados correctamente!")

    elif modo == "Agregar screener":
        st.title("Agregar un nuevo Screener")
        nuevo_screener = {
            "nombre": st.text_input("Nombre del Screener"),
            "tipo": st.selectbox("Tipo de Screener", tipos_plugins),
            "descripcion": st.text_area("Descripción del Screener")
        }

        parametros = obtener_parametros_plugin(nuevo_screener["tipo"])
        for param, detalles in parametros.items():
            nuevo_screener[param] = st.text_input(
                detalles.get("label", param),
                value=detalles.get("default", "")
            )

        if st.button("Agregar Screener"):
            screeners.append(nuevo_screener)
            guardar_configuracion(config)
            st.success("¡Screener agregado correctamente!")
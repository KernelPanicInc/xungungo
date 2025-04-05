import streamlit as st
import streamlit.components.v1 as components

nombre = "Custom Content Widget"
descripcion = "Plugin que permite crear contenido personalizado mediante Markdown o HTML."
tipo = "custom_content"

default_config = {
    "mode": "markdown",  # Opciones: "markdown" o "html"
    "content": "## Hola Mundo\n\nEste es un widget de contenido personalizado. \n\n*Puedes usar Markdown*."
}

def config(current_config: dict) -> dict:
    st.write("### Configuración del Widget de Contenido Personalizado")
    mode = st.radio(
        "Selecciona el modo:",
        options=["markdown", "html"],
        index=0 if current_config.get("mode", default_config["mode"]) == "markdown" else 1,
        help="Elige 'markdown' para contenido en Markdown o 'html' para contenido en HTML."
    )
    content = st.text_area(
        "Contenido",
        value=current_config.get("content", default_config["content"]),
        height=300,
        help="Escribe aquí el contenido personalizado. Puedes usar sintaxis Markdown o HTML, según el modo seleccionado."
    )
    return {"mode": mode, "content": content}

def render(config: dict):
    st.write("### Contenido Personalizado")
    mode = config.get("mode", default_config["mode"])
    content = config.get("content", default_config["content"])
    if mode == "markdown":
        st.markdown(content, unsafe_allow_html=True)
    elif mode == "html":
        # En este ejemplo se fija un ancho y alto para el contenedor HTML; puedes hacerlo configurable si lo deseas.
        components.html(content, width=700, height=400)
    else:
        st.write("Modo desconocido.")

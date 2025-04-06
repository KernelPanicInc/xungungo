import streamlit as st
import streamlit.components.v1 as components

nombre = "IFrame Widget"
descripcion = "Plugin para integrar un iframe en el dashboard."
tipo = "iframe"

default_config = {
    "src": "https://www.example.com",  # URL del iframe
    "width": None,  # Si es None, ocupa todo el ancho disponible
    "height": 800,
    "scrolling": False
}

def config(current_config: dict) -> dict:
    st.write("### Configuración del IFrame Widget")
    
    src = st.text_input(
        "URL (src)",
        value=current_config.get("src", default_config["src"]),
        help="URL del iframe."
    )
    width_str = st.text_input(
        "Ancho (width)",
        value=str(current_config.get("width", default_config["width"])) if current_config.get("width", default_config["width"]) is not None else "",
        help="Ancho en píxeles. Deja vacío para ocupar todo el ancho."
    )
    height = st.number_input(
        "Alto (height)",
        min_value=100,
        max_value=2000,
        value=current_config.get("height", default_config["height"]),
        step=10
    )
    scrolling = st.checkbox(
        "Activar scrolling",
        value=current_config.get("scrolling", default_config["scrolling"])
    )
    
    # Convertir width a int si se ingresa un valor, o dejarlo como None
    if width_str.strip() == "":
        width_val = None
    else:
        try:
            width_val = int(width_str)
        except Exception:
            width_val = None

    return {
        "src": src,
        "width": width_val,
        "height": height,
        "scrolling": scrolling
    }

def render(config: dict):
    st.write("### IFrame Widget")
    src = config.get("src", default_config["src"])
    width = config.get("width", default_config["width"])
    height = config.get("height", default_config["height"])
    scrolling = config.get("scrolling", default_config["scrolling"])
    
    # Renderizar el iframe usando components.iframe
    components.iframe(src=src, width=width, height=height, scrolling=scrolling)

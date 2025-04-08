import datetime as dt
import streamlit as st
import requests
import plotly.graph_objects as go

nombre = "CNN Fear & Greed"
descripcion = "Plugin que muestra el Fear Score y el Rating como un indicador tipo gauge, adaptado al modo oscuro según configuración."
tipo = "feargreed"

# Configuración por defecto del plugin
default_config = {
    "url": "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
    "height": 400,
    "line_color": "#1f77b4",  # Azul predeterminado
    "bg_color": "#ffffff",    # Fondo claro por defecto
    "text_color": "#000000"   # Texto oscuro por defecto
    # "is_dark" se espera que venga desde dashboard_render
}

def config(current_config: dict) -> dict:
    """
    Muestra los inputs para configurar el plugin y retorna un diccionario
    con los valores que el usuario haya seleccionado.
    NOTA: El modo oscuro se configura globalmente (desde dashboard_render) y no se pide aquí.
    """
    url_value = current_config.get("url", default_config["url"])
    chart_height_value = int(current_config.get("height", default_config["height"]))
    line_color_value = current_config.get("line_color", default_config["line_color"])
    bg_color_value = current_config.get("bg_color", default_config["bg_color"])
    text_color_value = current_config.get("text_color", default_config["text_color"])

    st.write("### Configuración CNN Fear & Greed")
    url = st.text_input(
        "URL del endpoint",
        value=url_value,
        help="URL para obtener los datos. No modificar si se usa el valor predeterminado."
    )
    chart_height = st.slider(
        "Altura del gráfico (px)",
        min_value=200, max_value=800,
        value=chart_height_value, step=50
    )
    line_color = st.color_picker("Color de la línea", value=line_color_value)
    bg_color = st.color_picker("Color de fondo", value=bg_color_value)
    text_color = st.color_picker("Color del texto", value=text_color_value)

    return {
        "url": url,
        "height": chart_height,
        "line_color": line_color,
        "bg_color": bg_color,
        "text_color": text_color
    }

def render(config: dict):
    """
    Descarga los datos del índice CNN Fear & Greed y muestra un indicador tipo gauge
    con Plotly. Los colores se ajustan según config["is_dark"] (pasado desde dashboard_render)
    y el alto es configurable.
    """
    st.write("Fear & Greed")

    url = config.get("url", default_config["url"])
    height = int(config.get("height", default_config["height"]))-74  # Ajustar altura para evitar scroll
    # Colores personalizados o por defecto
    line_color = config.get("line_color", default_config["line_color"])
    bg_color = config.get("bg_color", default_config["bg_color"])
    text_color = config.get("text_color", default_config["text_color"])
    is_dark = config.get("is_dark", False)  # Viene desde dashboard_render

    # Si estamos en modo oscuro y los colores no han sido personalizados, se ajustan
    if is_dark:
        if bg_color == default_config["bg_color"]:
            bg_color = "#2c2c2c"
        if text_color == default_config["text_color"]:
            text_color = "#ffffff"

    # Imitar a un navegador configurando headers
    headers = {
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Origin": "https://edition.cnn.com",
        "Referer": "https://edition.cnn.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data_json = response.json()
    except Exception as e:
        st.error(f"Error al obtener los datos: {e}")
        return

    # Extraer los datos actuales
    fear_greed = data_json.get("fear_and_greed", {})
    score = fear_greed.get("score")
    rating = fear_greed.get("rating")

    if score is None or rating is None:
        st.warning("No se encontraron datos de 'score' o 'rating'.")
        return

    try:
        score_val = float(score)
    except Exception:
        st.warning(f"No se pudo convertir el 'score': {score}")
        return

    # Crear el indicador gauge con Plotly
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_val,
        title={'text': rating.upper(), 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2},
            'bar': {'color': text_color},
            'steps': [
                {'range': [0, 25], 'color': '#ff9999'},
                {'range': [25, 50], 'color': '#ffc107'},
                {'range': [50, 75], 'color': '#c2f7b0'},
                {'range': [75, 100], 'color': '#7acf66'}
            ],
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    # Usar chart_height en el layout
    fig.update_layout(
        height=height,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor=bg_color,
        font={'color': text_color}
    )

    st.plotly_chart(fig, use_container_width=True)

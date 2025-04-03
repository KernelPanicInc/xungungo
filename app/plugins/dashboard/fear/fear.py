import streamlit as st
import requests
import plotly.graph_objects as go

nombre = "CNN Fear & Greed"
descripcion = "Plugin que muestra únicamente el Fear Score y el Rating como un indicador tipo gauge."
tipo = "feargreed"

# Configuración por defecto (si deseas que el usuario configure la URL, puedes ajustarlo)
default_config = {
    "url": "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
}

def config(current_config: dict) -> dict:
    """
    Si deseas permitir la configuración de la URL o algún otro parámetro, puedes
    mostrar inputs aquí. En este ejemplo, solo permitimos ajustar la URL.
    """
    url_value = current_config.get("url", default_config["url"])
    
    st.write("### Configuración CNN Fear & Greed (Gauge)")
    url = st.text_input(
        "URL del endpoint",
        value=url_value,
        help="URL para obtener los datos del Fear & Greed."
    )
    
    return {
        "url": url
    }

def render(config: dict):
    """
    Descarga los datos de Fear & Greed, extrae 'score' y 'rating' y muestra un
    indicador de tipo gauge con Plotly.
    """
    st.title("Fear & Greed Gauge")

    url = config.get("url", default_config["url"])

    # Cabeceras para imitar un navegador y evitar errores 4xx
    headers = {
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Origin": "https://edition.cnn.com",
        "Referer": "https://edition.cnn.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    # Intentar obtener los datos
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data_json = response.json()
    except Exception as e:
        st.error(f"Error al obtener los datos: {e}")
        return

    # Estructura esperada: data_json["fear_and_greed"] con "score" y "rating"
    fear_greed = data_json.get("fear_and_greed", {})
    score = fear_greed.get("score", None)
    rating = fear_greed.get("rating", None)

    if score is None or rating is None:
        st.warning("No se encontraron datos de 'score' o 'rating' en la respuesta.")
        return

    # Convertir a float en caso de que venga como string
    try:
        score_val = float(score)
    except:
        st.warning(f"No se pudo convertir el 'score' a número: {score}")
        return

    # Crear el indicador tipo gauge con Plotly
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_val,
        title={'text': rating.upper(), 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2},
            'bar': {'color': 'black'},  # Color de la aguja
            # Pasos de color (0-25, 25-50, 50-75, 75-100)
            'steps': [
                {'range': [0, 25], 'color': '#ff9999'},      # Extreme Fear (rojo claro)
                {'range': [25, 50], 'color': '#ffc107'},     # Fear (naranja)
                {'range': [50, 75], 'color': '#c2f7b0'},     # Greed (verde claro)
                {'range': [75, 100], 'color': '#7acf66'}     # Extreme Greed (verde intenso)
            ],
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    fig.update_layout(
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor="white",   # Fondo del "papel"
        font={'color': 'black'}  # Color del texto en general
    )

    st.plotly_chart(fig, use_container_width=True)

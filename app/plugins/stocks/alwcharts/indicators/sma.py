import streamlit as st
import pandas as pd


"""
Plugin que calcula tres SMAs y las muestra en el gráfico 
como tres líneas de colores configurables, con ancho, opacidad y nombre definidos.
"""
name = "SMA (3 Medias Móviles)"
description = "Calcula y traza 3 SMA de distintos periodos, permitiendo configurar el ancho de línea, opacidad y nombre de cada una."

def get_user_params(data: pd.DataFrame) -> dict:
    """
    Solicita al usuario los parámetros (periodos, colores, ancho, opacidad y nombre) 
    para cada una de las SMA.
    """
    st.sidebar.markdown("**Parámetros de las 3 SMA**")
    # SMA 1
    period1 = st.sidebar.number_input(
        "Periodo SMA 1",
        min_value=2, max_value=500, value=20, step=1,
        help="Cantidad de velas para la primera media móvil."
    )
    color1 = st.sidebar.color_picker(
        "Color SMA 1",
        value="#2962FF",
        help="Color de la primera SMA en el gráfico."
    )
    line_width1 = st.sidebar.number_input(
        "Ancho de Línea SMA 1",
        min_value=1, max_value=10, value=2, step=1,
        help="Ancho de la línea para la primera SMA."
    )
    opacity1 = st.sidebar.slider(
        "Opacidad SMA 1",
        min_value=0.0, max_value=1.0, value=1.0, step=0.1,
        help="Opacidad de la línea para la primera SMA."
    )
    name1 = st.sidebar.text_input(
        "Nombre SMA 1",
        value="SMA 1",
        help="Nombre o etiqueta para la primera SMA."
    )
    
    # SMA 2
    period2 = st.sidebar.number_input(
        "Periodo SMA 2",
        min_value=2, max_value=500, value=50, step=1,
        help="Cantidad de velas para la segunda media móvil."
    )
    color2 = st.sidebar.color_picker(
        "Color SMA 2",
        value="#F44336",
        help="Color de la segunda SMA en el gráfico."
    )
    line_width2 = st.sidebar.number_input(
        "Ancho de Línea SMA 2",
        min_value=1, max_value=10, value=2, step=1,
        help="Ancho de la línea para la segunda SMA."
    )
    opacity2 = st.sidebar.slider(
        "Opacidad SMA 2",
        min_value=0.0, max_value=1.0, value=1.0, step=0.1,
        help="Opacidad de la línea para la segunda SMA."
    )
    name2 = st.sidebar.text_input(
        "Nombre SMA 2",
        value="SMA 2",
        help="Nombre o etiqueta para la segunda SMA."
    )
    
    # SMA 3
    period3 = st.sidebar.number_input(
        "Periodo SMA 3",
        min_value=2, max_value=500, value=100, step=1,
        help="Cantidad de velas para la tercera media móvil."
    )
    color3 = st.sidebar.color_picker(
        "Color SMA 3",
        value="#4CAF50",
        help="Color de la tercera SMA en el gráfico."
    )
    line_width3 = st.sidebar.number_input(
        "Ancho de Línea SMA 3",
        min_value=1, max_value=10, value=2, step=1,
        help="Ancho de la línea para la tercera SMA."
    )
    opacity3 = st.sidebar.slider(
        "Opacidad SMA 3",
        min_value=0.0, max_value=1.0, value=1.0, step=0.1,
        help="Opacidad de la línea para la tercera SMA."
    )
    name3 = st.sidebar.text_input(
        "Nombre SMA 3",
        value="SMA 3",
        help="Nombre o etiqueta para la tercera SMA."
    )

    return {
        "period1": period1, "color1": color1, "line_width1": line_width1, "opacity1": opacity1, "name1": name1,
        "period2": period2, "color2": color2, "line_width2": line_width2, "opacity2": opacity2, "name2": name2,
        "period3": period3, "color3": color3, "line_width3": line_width3, "opacity3": opacity3, "name3": name3,
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    """
    Calcula las 3 SMA en base a la columna 'Close' y 
    las añade como 3 series de tipo 'Line' en el charts_config, 
    utilizando los parámetros configurados (color, ancho, opacidad y nombre).
    """
    if "Close" not in data.columns:
        st.warning("No se encontró la columna 'Close' en los datos. No se calculará la SMA.")
        return

    # Extraer parámetros para cada SMA
    period1, color1 = user_params.get("period1"), user_params.get("color1")
    line_width1, opacity1 = user_params.get("line_width1"), user_params.get("opacity1")
    name1 = user_params.get("name1")
    
    period2, color2 = user_params.get("period2"), user_params.get("color2")
    line_width2, opacity2 = user_params.get("line_width2"), user_params.get("opacity2")
    name2 = user_params.get("name2")
    
    period3, color3 = user_params.get("period3"), user_params.get("color3")
    line_width3, opacity3 = user_params.get("line_width3"), user_params.get("opacity3")
    name3 = user_params.get("name3")

    # Calcular 3 SMA
    data[f"SMA_{period1}"] = data["Close"].rolling(window=period1).mean()
    data[f"SMA_{period2}"] = data["Close"].rolling(window=period2).mean()
    data[f"SMA_{period3}"] = data["Close"].rolling(window=period3).mean()

    # Para cada SMA, construir los puntos (time/value) y añadir la serie al charts_config
    for period, color, line_width, opacity, series_name in [
        (period1, color1, line_width1, opacity1, name1),
        (period2, color2, line_width2, opacity2, name2),
        (period3, color3, line_width3, opacity3, name3)
    ]:
        sma_col = f"SMA_{period}"
        sma_data = []
        for _, row in data.iterrows():
            if pd.notna(row[sma_col]):
                time_val = int(row["Fecha"].timestamp())
                sma_data.append({
                    "time": time_val,
                    "value": float(row[sma_col])
                })

        # Añadir la serie de SMA como una 'Line' con las opciones configuradas, incluyendo el nombre
        charts_config[0]["series"].append({
            "type": "Line",
            "data": sma_data,
            "options": {
                "lineWidth": line_width,
                "color": color,
                "opacity": opacity,
                "title": series_name
            }
        })

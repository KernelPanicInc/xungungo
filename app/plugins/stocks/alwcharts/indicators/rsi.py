import streamlit as st
import pandas as pd

"""
Plugin que agrega el RSI (Relative Strength Index) al gráfico.
Permite personalizar el período, color, opacidad y ancho de la línea.
"""

name = "RSI (Índice de Fuerza Relativa)"
description = "Calcula el RSI basado en el cierre de la vela y lo grafica como una línea."

def get_user_params(data: pd.DataFrame) -> dict:
    """
    Solicita al usuario los parámetros para el cálculo del RSI.
    """
    st.sidebar.markdown("**Parámetros del RSI**")
    
    period = st.sidebar.number_input(
        "Período del RSI",
        min_value=2, max_value=50, value=14, step=1,
        help="Número de velas utilizadas para calcular el RSI."
    )
    
    color = st.sidebar.color_picker(
        "Color de la línea RSI",
        value="#FF9800",
        help="Color de la línea RSI en el gráfico."
    )
    
    line_width = st.sidebar.number_input(
        "Ancho de Línea",
        min_value=1, max_value=10, value=2, step=1,
        help="Ancho de la línea del RSI."
    )
    
    opacity = st.sidebar.slider(
        "Opacidad de la Línea",
        min_value=0.0, max_value=1.0, value=1.0, step=0.1,
        help="Opacidad de la línea del RSI."
    )

    return {
        "period": period,
        "color": color,
        "line_width": line_width,
        "opacity": opacity
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    """
    Calcula el RSI y lo añade como una serie de tipo 'Line' en el charts_config.
    """
    if "Close" not in data.columns:
        st.warning("No se encontró la columna 'Close' en los datos. No se calculará el RSI.")
        return

    period = user_params["period"]
    
    # Cálculo del RSI
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # Formato de datos para el gráfico
    rsi_data = []
    for _, row in data.iterrows():
        if pd.notna(row["RSI"]):
            time_val = int(row["Fecha"].timestamp())
            rsi_data.append({
                "time": time_val,
                "value": float(row["RSI"])
            })

    # Añadir el RSI como gráfico independiente
    rsi_chart = {
        "chart": {
            "height": 150,  # Altura del gráfico RSI
            "layout": {
                "background": {"type": "solid", "color": "#FFFFFF"},
                "textColor": "black"
            },
            "timeScale": charts_config[0]["chart"]["timeScale"],  # Sincronizar escala de tiempo
        },
        "series": [
            {
                "type": "Line",
                "data": rsi_data,
                "options": {
                    "color": user_params["color"],
                    "lineWidth": user_params["line_width"],
                    "opacity": user_params["opacity"],
                }
            }
        ]
    }

    charts_config.append(rsi_chart)

import streamlit as st
import pandas as pd

"""
Plugin que agrega un histograma de volumen al gráfico.
Permite personalizar el color, opacidad y ancho de barra.
"""

name = "Volumen"
description = "Muestra el volumen de operaciones como un histograma debajo del gráfico de velas."

def get_user_params(data: pd.DataFrame) -> dict:
    """
    Solicita al usuario parámetros para personalizar el gráfico de volumen.
    """
    st.sidebar.markdown("**Parámetros del Volumen**")
    
    color = st.sidebar.color_picker(
        "Color del volumen",
        value="#1565C0",
        help="Color de las barras del volumen."
    )
    
    opacity = st.sidebar.slider(
        "Opacidad del volumen",
        min_value=0.0, max_value=1.0, value=0.8, step=0.1,
        help="Opacidad de las barras del volumen."
    )
    
    line_width = st.sidebar.number_input(
        "Ancho de barra",
        min_value=1, max_value=10, value=2, step=1,
        help="Ancho de cada barra del volumen."
    )

    return {
        "color": color,
        "opacity": opacity,
        "line_width": line_width
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    """
    Agrega el volumen como un histograma debajo del gráfico de velas.
    """
    if "Volume" not in data.columns:
        st.warning("No se encontró la columna 'Volume' en los datos. No se graficará el volumen.")
        return

    volume_data = []
    for _, row in data.iterrows():
        if pd.notna(row["Volume"]):
            time_val = int(row["Fecha"].timestamp())
            volume_data.append({
                "time": time_val,
                "value": float(row["Volume"])
            })

    # Ajustar la configuración del gráfico de volumen para que coincida con el candlestick
    volume_chart = {
        "chart": {
            "height": 200,  # Altura del gráfico de volumen
            "layout": {
                "background": {"type": "solid", "color": "#FFFFFF"},
                "textColor": "black"
            },
            "timeScale": {
                    "visible": False,
                },
        },
        "series": [
            {
                "type": "Histogram",
                "data": volume_data,
                "options": {
                    "color": user_params.get("color"),
                    "opacity": user_params.get("opacity"),
                    "lineWidth": user_params.get("line_width"),
                    "priceFormat": {
                        "type": 'volume',
                    },
                }
            }
        ]
    }

    charts_config.append(volume_chart)


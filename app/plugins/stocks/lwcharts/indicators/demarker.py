import streamlit as st
import pandas as pd

"""
Plugin que agrega el DeMarker (Tom Demark) al gráfico.
Permite personalizar el período, color, opacidad y ancho de la línea.
"""

name = "DeMarker (Tom Demark)"
description = "Calcula el indicador DeMarker y lo grafica como una línea."

def get_user_params(data: pd.DataFrame) -> dict:
    """
    Solicita al usuario los parámetros para el cálculo del DeMarker.
    """
    with st.sidebar.expander("🔧 Parámetros del DeMarker", expanded=True):
        period = st.number_input(
            "Período",
            min_value=2, max_value=50, value=14, step=1,
            help="Número de velas utilizadas para calcular el DeMarker."
        )

        color = st.color_picker(
            "Color de la línea",
            value="#2196F3",
            help="Color de la línea del DeMarker en el gráfico."
        )

        line_width = st.number_input(
            "Ancho de línea",
            min_value=1, max_value=10, value=2, step=1,
            help="Ancho de la línea del DeMarker."
        )

        opacity = st.slider(
            "Opacidad de la línea",
            min_value=0.0, max_value=1.0, value=1.0, step=0.1,
            help="Opacidad de la línea del DeMarker."
        )

    return {
        "period": period,
        "color": color,
        "line_width": line_width,
        "opacity": opacity
    }

def apply(charts_config: list, data, user_params: dict):
    """
    Calcula el indicador DeMarker y lo añade como una serie de tipo 'Baseline' en charts_config.
    Además, traza líneas horizontales en 0.3 y 0.7.
    """
    import streamlit as st
    import pandas as pd

    if not {"High", "Low"}.issubset(data.columns):
        st.warning("No se encontraron las columnas 'High' y 'Low' en los datos. No se calculará el DeMarker.")
        return
    is_dark = user_params["is_dark"]
    # --- Configuración de colores según el tema activo ---
    if is_dark:
        chart_background = "#1E1E1E"
        text_color = "#FFFFFF"
        watermark_color = "rgba(255, 255, 255, 0.1)"
        # Colores Baseline
        top_line_color = "#4CAF50"     # Verde para la parte superior
        bottom_line_color = "#FF5252"  # Rojo para la parte inferior
        top_fill_1 = "rgba(76, 175, 80, 0.4)"
        top_fill_2 = "rgba(76, 175, 80, 0.0)"
        bottom_fill_1 = "rgba(255, 82, 82, 0.4)"
        bottom_fill_2 = "rgba(255, 82, 82, 0.0)"
        # Color para las líneas horizontales en formato RGBA
        horizontal_line_color = "rgba(255, 193, 7, 0.5)"
        grid =  {
                    "vertLines": { "color": '#444' },
                    "horzLines": { "color": '#444' },
                }
    else:
        chart_background = "#FFFFFF"
        text_color = "black"
        watermark_color = "rgba(0, 0, 0, 0.1)"
        # Colores Baseline
        top_line_color = "#4CAF50"
        bottom_line_color = "#FF5252"
        top_fill_1 = "rgba(76, 175, 80, 0.4)"
        top_fill_2 = "rgba(76, 175, 80, 0.0)"
        bottom_fill_1 = "rgba(255, 82, 82, 0.4)"
        bottom_fill_2 = "rgba(255, 82, 82, 0.0)"
        # Color para las líneas horizontales en formato RGBA
        horizontal_line_color = "rgba(255, 87, 34, 0.5)"
        grid =  None

    period = user_params["period"]

    # --- Cálculo del DeMarker ---
    dem_up = data["High"].diff().clip(lower=0)
    dem_down = -data["Low"].diff().clip(upper=0)

    dem_up_sum = dem_up.rolling(window=period, min_periods=1).sum()
    dem_down_sum = dem_down.rolling(window=period, min_periods=1).sum()

    data["DeMarker"] = dem_up_sum / (dem_up_sum + dem_down_sum)

    # --- Datos para el gráfico principal (Baseline) ---
    demarker_data = []
    for _, row in data.iterrows():
        if pd.notna(row["DeMarker"]):
            time_val = int(row["Fecha"].timestamp())
            demarker_data.append({"time": time_val, "value": float(row["DeMarker"])})

    # --- Líneas horizontales en 0.3 y 0.7 ---
    horizontal_line_03_data = []
    horizontal_line_07_data = []
    for point in demarker_data:
        horizontal_line_03_data.append({"time": point["time"], "value": 0.3})
        horizontal_line_07_data.append({"time": point["time"], "value": 0.7})

    # --- Configuración del gráfico ---
    demarker_chart = {
        "chart": {
            "height": 150,
            "layout": {
                "background": {"type": "solid", "color": chart_background},
                "textColor": text_color
            },
            "timeScale": charts_config[0]["chart"]["timeScale"],
            "watermark": {
                "text": "demarker",
                "visible": True,
                "fontSize": 20,
                "color": watermark_color,
                "horzAlign": "left",
                "vertAlign": "top"
            },
            "grid" : grid
        },
        "series": [
            # --- Serie Baseline del DeMarker ---
            {
                "type": "Baseline",
                "data": demarker_data,
                "options": {
                    # Línea base a 0.5
                    "baseValue": {
                        "type": "price",
                        "price": 0.5
                    },
                    "relativeGradient" : True,
                    # Colores de la línea en la parte superior/inferior
                    "topLineColor": top_line_color,
                    "bottomLineColor": bottom_line_color,
                    # Colores de relleno en la parte superior/inferior
                    "topFillColor1": top_fill_1,
                    "topFillColor2": top_fill_2,
                    "bottomFillColor1": bottom_fill_1,
                    "bottomFillColor2": bottom_fill_2,
                    # Ajustes de línea
                    "lineWidth": user_params["line_width"],
                    "lineStyle": 0,  # 0=Solid, 1=Dotted, 2=Dashed...
                    "lineType": 0,   # 0=Simple, 1=WithSteps
                    "opacity": user_params["opacity"]
                }
            },
            # --- Línea horizontal en 0.3 ---
            {
                "type": "Line",
                "data": horizontal_line_03_data,
                
                "options": {
                    "color": horizontal_line_color,
                    "lineWidth": 1,
                    "lineStyle": 2,  # 2=Dashed
                    "priceLineVisible": False,
                    "lastValueVisible": False
                }
            },
            # --- Línea horizontal en 0.7 ---
            {
                "type": "Line",
                "data": horizontal_line_07_data,
                "options": {
                    "color": horizontal_line_color,
                    "lineWidth": 1,
                    "lineStyle": 2,
                    "priceLineVisible": False,
                    "lastValueVisible": False
                }
            }
        ]
    }

    charts_config.append(demarker_chart)

# macd.py
import streamlit as st
import pandas as pd
import numpy as np

name = "MACD"
description = "Muestra el MACD, su señal y su histograma en un panel separado debajo del gráfico principal."

def get_user_params(data: pd.DataFrame) -> dict:
    """
    Solicita al usuario los parámetros y estilos para el MACD.
    """
    st.sidebar.markdown("**Parámetros del MACD**")
    fast_period = st.sidebar.number_input(
        "Periodo Rápido (EMA)",
        min_value=1, max_value=500, value=12, step=1
    )
    slow_period = st.sidebar.number_input(
        "Periodo Lento (EMA)",
        min_value=1, max_value=500, value=26, step=1
    )
    signal_period = st.sidebar.number_input(
        "Periodo Señal (EMA)",
        min_value=1, max_value=500, value=9, step=1
    )

    st.sidebar.markdown("**Estilos MACD**")
    color_macd = st.sidebar.color_picker("Color Línea MACD", value="#2962FF")
    line_width_macd = st.sidebar.number_input("Ancho Línea MACD", 1, 10, 2, 1)

    st.sidebar.markdown("**Estilos Señal**")
    color_signal = st.sidebar.color_picker("Color Línea Señal", value="#F44336")
    line_width_signal = st.sidebar.number_input("Ancho Línea Señal", 1, 10, 2, 1)

    st.sidebar.markdown("**Estilos Histograma**")
    color_hist_up = st.sidebar.color_picker("Color (+)", value="#26a69a")
    color_hist_down = st.sidebar.color_picker("Color (-)", value="#ef5350")

    return {
        "fast_period": fast_period,
        "slow_period": slow_period,
        "signal_period": signal_period,
        "color_macd": color_macd,
        "line_width_macd": line_width_macd,
        "color_signal": color_signal,
        "line_width_signal": line_width_signal,
        "color_hist_up": color_hist_up,
        "color_hist_down": color_hist_down,
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    """
    Calcula y dibuja MACD, línea de señal e histograma en un panel separado (similar a Volumen).
    """
    if "Close" not in data.columns:
        st.warning("No se encontró la columna 'Close' en los datos. No se calculará el MACD.")
        return

    # Extraer parámetros
    fast_period = user_params["fast_period"]
    slow_period = user_params["slow_period"]
    signal_period = user_params["signal_period"]
    color_macd = user_params["color_macd"]
    line_width_macd = user_params["line_width_macd"]
    color_signal = user_params["color_signal"]
    line_width_signal = user_params["line_width_signal"]
    color_hist_up = user_params["color_hist_up"]
    color_hist_down = user_params["color_hist_down"]

    # Asegurarnos de no causar errores si fast_period >= slow_period
    if fast_period >= slow_period:
        st.warning("El periodo rápido debería ser menor al periodo lento para un MACD típico.")
        return

    # Cálculo del MACD
    data["EMA_fast"] = data["Close"].ewm(span=fast_period, adjust=False).mean()
    data["EMA_slow"] = data["Close"].ewm(span=slow_period, adjust=False).mean()

    data["MACD"] = data["EMA_fast"] - data["EMA_slow"]
    data["MACD_signal"] = data["MACD"].ewm(span=signal_period, adjust=False).mean()
    data["MACD_hist"] = data["MACD"] - data["MACD_signal"]

    macd_line = []
    signal_line = []
    histogram_bars = []

    for _, row in data.iterrows():
        time_val = int(row["Fecha"].timestamp())

        # MACD
        if pd.notna(row["MACD"]):
            macd_line.append({
                "time": time_val,
                "value": float(row["MACD"])
            })

        # Señal
        if pd.notna(row["MACD_signal"]):
            signal_line.append({
                "time": time_val,
                "value": float(row["MACD_signal"])
            })

        # Histograma
        if pd.notna(row["MACD_hist"]):
            hist_value = float(row["MACD_hist"])
            color = color_hist_up if hist_value >= 0 else color_hist_down
            histogram_bars.append({
                "time": time_val,
                "value": hist_value,
                "color": color
            })

    # Crear un nuevo panel, similar al plugin de Volumen
    macd_chart = {
        "chart": {
            "height": 200,
            "layout": {
                "background": {"type": "solid", "color": "#FFFFFF"},
                "textColor": "black"
            },
            "timeScale": {
                "visible": False,
            },
        },
        "series": []
    }

    # Línea MACD
    macd_chart["series"].append({
        "type": "Line",
        "data": macd_line,
        "options": {
            "lineWidth": line_width_macd,
            "color": color_macd,
            "title": "MACD"
        }
    })

    # Línea de señal
    macd_chart["series"].append({
        "type": "Line",
        "data": signal_line,
        "options": {
            "lineWidth": line_width_signal,
            "color": color_signal,
            "title": "MACD Signal"
        }
    })

    # Histograma
    macd_chart["series"].append({
        "type": "Histogram",
        "data": histogram_bars,
        "options": {
            "priceFormat": {"type": "price", "precision": 4, "minMove": 0.0001},
            "priceScaleId": "",
            "base": 0,
        }
    })

    # Añadimos el nuevo chart (panel) al final de charts_config
    charts_config.append(macd_chart)

import streamlit as st
import pandas as pd

"""
Plugin que calcula y dibuja niveles de retrocesos de Fibonacci sobre el gráfico de velas.
Permite definir manualmente los extremos (precio alto y bajo) o calcularlos automáticamente a partir de los datos.
Se pueden configurar los niveles de Fibonacci, así como el color (en formato RGBA) y el ancho de las líneas.
"""

name = "Retrocesos de Fibonacci"
description = "Calcula y traza niveles de retrocesos de Fibonacci basados en los extremos de precio o valores definidos manualmente."

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_user_params(data: pd.DataFrame) -> dict:
    st.sidebar.markdown("**Parámetros de Retrocesos de Fibonacci**")
    manual = st.sidebar.checkbox(
        "Definir manualmente extremos",
        value=False,
        help="Si se activa, permite definir manualmente el precio alto y bajo para calcular el retroceso."
    )
    if manual:
        default_high = float(data["High"].max()) if "High" in data.columns else 0.0
        default_low = float(data["Low"].min()) if "Low" in data.columns else 0.0
        high_price = st.sidebar.number_input(
            "Precio Alto",
            value=default_high,
            help="Precio máximo para calcular el retroceso."
        )
        low_price = st.sidebar.number_input(
            "Precio Bajo",
            value=default_low,
            help="Precio mínimo para calcular el retroceso."
        )
    else:
        high_price = None
        low_price = None

    color = st.sidebar.color_picker(
        "Color de las líneas Fibonacci",
        value="#FFA500",
        help="Color base para las líneas de retroceso. Se convertirá a formato RGBA usando el valor de opacidad."
    )
    line_width = st.sidebar.number_input(
        "Ancho de línea",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help="Ancho de las líneas de retroceso."
    )
    # Se solicita la opacidad, que se combinará con el color en formato RGBA.
    opacity = st.sidebar.slider(
        "Opacidad de las líneas",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.1,
        help="Opacidad de las líneas de retroceso."
    )
    levels_str = st.sidebar.text_input(
        "Niveles de Fibonacci (separados por coma)",
        value="0%,23.6%,38.2%,50%,61.8%,100%",
        help="Introduce los niveles de Fibonacci que deseas mostrar, separados por comas."
    )
    try:
        levels = [float(x.replace("%", "").strip())/100.0 for x in levels_str.split(",")]
    except Exception as e:
        st.error("Error en la interpretación de los niveles de Fibonacci. Asegúrese de introducir valores numéricos separados por comas.")
        levels = [0.0, 0.236, 0.382, 0.5, 0.618, 1.0]

    return {
        "manual": manual,
        "high_price": high_price,
        "low_price": low_price,
        "color": color,
        "line_width": line_width,
        "opacity": opacity,
        "levels": levels,
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    if "Fecha" not in data.columns:
        st.warning("No se encontró la columna 'Fecha' en los datos. No se dibujarán los retrocesos de Fibonacci.")
        return

    # Determinar los extremos
    if user_params.get("manual"):
        high = user_params.get("high_price")
        low = user_params.get("low_price")
    else:
        if "High" in data.columns and "Low" in data.columns:
            high = data["High"].max()
            low = data["Low"].min()
        elif "Close" in data.columns:
            high = data["Close"].max()
            low = data["Close"].min()
        else:
            st.warning("No se encontraron columnas adecuadas para determinar los extremos. Se requieren 'High' y 'Low' o 'Close'.")
            return

    if high == low:
        st.warning("El precio alto y bajo son iguales. No se pueden calcular retrocesos de Fibonacci.")
        return

    diff = high - low
    levels = user_params.get("levels", [0.0, 0.236, 0.382, 0.5, 0.618, 1.0])
    color_hex = user_params.get("color")
    line_width = user_params.get("line_width")
    opacity = user_params.get("opacity")

    # Convertir el color hexadecimal a formato RGBA combinándolo con la opacidad
    r, g, b = hex_to_rgb(color_hex)
    rgba_color = f"rgba({r}, {g}, {b}, {opacity})"

    # Para cada nivel de Fibonacci se calcula el precio correspondiente y se traza una línea horizontal
    for lvl in levels:
        price = high - diff * lvl
        fib_data = []
        for _, row in data.iterrows():
            if pd.notna(row["Fecha"]):
                time_val = int(row["Fecha"].timestamp())
                fib_data.append({
                    "time": time_val,
                    "value": price
                })
        charts_config[0]["series"].append({
            "type": "Line",
            "data": fib_data,
            "options": {
                "lineWidth": line_width,
                "color": rgba_color,
                "title": f"Fib {int(lvl*100)}%"
            }
        })

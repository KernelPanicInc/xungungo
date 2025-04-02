import streamlit as st
import pandas as pd
import numpy as np

"""
Plugin que calcula una regresión lineal a partir de una fecha de inicio 
y traza la línea de regresión junto a sus canales superior e inferior.
El canal se define como la línea de regresión ± un múltiplo de 
la desviación estándar de los residuos.
"""

name = "Regresión Lineal con Canales"
description = "Calcula y traza una regresión lineal desde una fecha de inicio y muestra sus canales superior e inferior basados en un multiplicador de la desviación estándar."

def get_user_params(data: pd.DataFrame) -> dict:
    with st.sidebar.expander("Configuración de Regresión Lineal y Canales"):
        # Parámetro: Fecha de inicio para el cálculo de la regresión.
        start_date = st.date_input(
            "Fecha de inicio para la regresión",
            value=pd.to_datetime("2020-01-01").date(),
            help="Selecciona la fecha desde la cual se calculará la regresión lineal."
        )
    
        # Parámetro: Multiplicador para la desviación estándar (definirá la distancia de los canales respecto a la línea de regresión)
        multiplier = st.slider(
            "Multiplicador de desviación para canales",
            min_value=0.5, max_value=3.0, value=1.0, step=0.1,
            help="Multiplicador de la desviación estándar para calcular los canales superior e inferior."
        )
    
        # Parámetros para la línea de regresión
        reg_color = st.color_picker(
            "Color de la línea de regresión",
            value="#000000",
            help="Color de la línea de regresión."
        )
        reg_line_width = st.number_input(
            "Ancho de línea de regresión",
            min_value=1, max_value=10, value=2, step=1,
            help="Ancho de la línea de regresión."
        )
        reg_opacity = st.slider(
            "Opacidad de la línea de regresión",
            min_value=0.0, max_value=1.0, value=1.0, step=0.1,
            help="Opacidad de la línea de regresión."
        )
        reg_name = st.text_input(
            "Nombre de la línea de regresión",
            value="Regresión Lineal",
            help="Nombre o etiqueta para la línea de regresión."
        )
    
        # Parámetros para el canal superior
        upper_color = st.color_picker(
            "Color del canal superior",
            value="#008000",
            help="Color de la línea del canal superior."
        )
        upper_line_width = st.number_input(
            "Ancho de línea del canal superior",
            min_value=1, max_value=10, value=2, step=1,
            help="Ancho de la línea del canal superior."
        )
        upper_opacity = st.slider(
            "Opacidad del canal superior",
            min_value=0.0, max_value=1.0, value=1.0, step=0.1,
            help="Opacidad de la línea del canal superior."
        )
        upper_name = st.text_input(
            "Nombre del canal superior",
            value="Canal Superior",
            help="Nombre o etiqueta para el canal superior."
        )
    
        # Parámetros para el canal inferior
        lower_color = st.color_picker(
            "Color del canal inferior",
            value="#FF0000",
            help="Color de la línea del canal inferior."
        )
        lower_line_width = st.number_input(
            "Ancho de línea del canal inferior",
            min_value=1, max_value=10, value=2, step=1,
            help="Ancho de la línea del canal inferior."
        )
        lower_opacity = st.slider(
            "Opacidad del canal inferior",
            min_value=0.0, max_value=1.0, value=1.0, step=0.1,
            help="Opacidad de la línea del canal inferior."
        )
        lower_name = st.text_input(
            "Nombre del canal inferior",
            value="Canal Inferior",
            help="Nombre o etiqueta para el canal inferior."
        )
    
    return {
        "start_date": start_date,
        "multiplier": multiplier,
        "reg_color": reg_color,
        "reg_line_width": reg_line_width,
        "reg_opacity": reg_opacity,
        "reg_name": reg_name,
        "upper_color": upper_color,
        "upper_line_width": upper_line_width,
        "upper_opacity": upper_opacity,
        "upper_name": upper_name,
        "lower_color": lower_color,
        "lower_line_width": lower_line_width,
        "lower_opacity": lower_opacity,
        "lower_name": lower_name
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    if "Close" not in data.columns or "Fecha" not in data.columns:
        st.warning("No se encontró la columna 'Close' o 'Fecha' en los datos. No se calculará la regresión.")
        return

    # Asegurarse de que la columna 'Fecha' esté en formato datetime
    data["Fecha"] = pd.to_datetime(data["Fecha"])
    
    # Filtrar datos a partir de la fecha de inicio proporcionada
    start_date = pd.to_datetime(user_params.get("start_date"))
    filtered_data = data[data["Fecha"] >= start_date]
    
    if filtered_data.empty:
        st.warning("No hay datos a partir de la fecha de inicio seleccionada.")
        return
    
    # Convertir las fechas a valores numéricos (timestamp) para la regresión
    x = filtered_data["Fecha"].apply(lambda dt: dt.timestamp()).values
    y = filtered_data["Close"].values
    
    # Calcular la regresión lineal (pendiente y ordenada al origen)
    slope, intercept = np.polyfit(x, y, 1)
    
    # Calcular los valores de la línea de regresión
    y_reg = slope * x + intercept
    
    # Calcular la desviación estándar de los residuos
    residuals = y - y_reg
    std_residual = np.std(residuals)
    
    # Obtener el multiplicador para los canales
    multiplier = user_params.get("multiplier")
    
    # Calcular los valores de los canales superior e inferior
    y_upper = y_reg + multiplier * std_residual
    y_lower = y_reg - multiplier * std_residual
    
    # Construir las series para graficar
    reg_series = []
    upper_series = []
    lower_series = []
    for _, row in filtered_data.iterrows():
        time_val = int(row["Fecha"].timestamp())
        reg_series.append({
            "time": time_val,
            "value": float(slope * time_val + intercept)
        })
        upper_series.append({
            "time": time_val,
            "value": float(slope * time_val + intercept + multiplier * std_residual)
        })
        lower_series.append({
            "time": time_val,
            "value": float(slope * time_val + intercept - multiplier * std_residual)
        })
    
    # Añadir las series calculadas al charts_config
    charts_config[0]["series"].append({
        "type": "Line",
        "data": reg_series,
        "options": {
            "lineWidth": user_params.get("reg_line_width"),
            "color": user_params.get("reg_color"),
            "opacity": user_params.get("reg_opacity"),
            "title": user_params.get("reg_name")
        }
    })
    
    charts_config[0]["series"].append({
        "type": "Line",
        "data": upper_series,
        "options": {
            "lineWidth": user_params.get("upper_line_width"),
            "color": user_params.get("upper_color"),
            "opacity": user_params.get("upper_opacity"),
            "title": user_params.get("upper_name")
        }
    })
    
    charts_config[0]["series"].append({
        "type": "Line",
        "data": lower_series,
        "options": {
            "lineWidth": user_params.get("lower_line_width"),
            "color": user_params.get("lower_color"),
            "opacity": user_params.get("lower_opacity"),
            "title": user_params.get("lower_name")
        }
    })

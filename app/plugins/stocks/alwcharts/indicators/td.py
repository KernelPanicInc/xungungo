import streamlit as st
import pandas as pd
from plugins.stocks.alwcharts.indicators.td.td_setup import calculate_td_setup
from plugins.stocks.alwcharts.indicators.td.td_countdown import calculate_td_countdown

name = "TD Sequential - Setup + Countdown"
description = "Detecta el TD Setup y Countdown en módulos separados para mayor organización."

def get_user_params(data: pd.DataFrame) -> dict:
    st.sidebar.markdown("**Configuración del TD Sequential**")
    
    # Configurar los colores en dos columnas
    col1, col2 = st.sidebar.columns(2)
    with col1:
        buy_setup_color = st.color_picker("Color para Buy Setup (①-⑨)", value="#00FF00")
        sell_setup_color = st.color_picker("Color para Sell Setup (①-⑨)", value="#AA0000")
    with col2:
        buy_countdown_color = st.color_picker("Color para Buy Countdown (㏠-㏬)", value="#008000")
        sell_countdown_color = st.color_picker("Color para Sell Countdown (㏠-㏬)", value="#800000")
    
    show_only_full_setups = st.sidebar.checkbox(
        "Mostrar solo Setups completos (9)", value=False,
        help="Si se activa, solo se mostrarán los Setups que llegan a 9."
    )
    
    show_only_complete_countdown = st.sidebar.checkbox(
        "Mostrar solo Countdown completos", value=False,
        help="Si se activa, se muestran solo los countdowns completos (hasta 13) y, en caso de estar en curso, solo el último marcador."
    )
    
    return {
        "buy_setup_color": buy_setup_color,
        "sell_setup_color": sell_setup_color,
        "buy_countdown_color": buy_countdown_color,
        "sell_countdown_color": sell_countdown_color,
        "show_only_full_setups": show_only_full_setups,
        "show_only_complete_countdown": show_only_complete_countdown
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    if "Close" not in data.columns or "Fecha" not in data.columns:
        st.warning("Los datos deben contener las columnas 'Close' y 'Fecha'.")
        return

    markers = []
    data = data.reset_index(drop=True)

    # Obtener los setups y los índices de setups completos
    setup_markers, completed_buy_setups, completed_sell_setups = calculate_td_setup(
        data, 
        user_params["show_only_full_setups"], 
        user_params["buy_setup_color"], 
        user_params["sell_setup_color"]
    )

    # Obtener los countdowns basados en los setups completados
    buy_countdown_markers = calculate_td_countdown(
        data, 
        completed_buy_setups, 
        "buy", 
        user_params["buy_countdown_color"],
        only_complete_countdown=user_params["show_only_complete_countdown"],
        contrary_setups=completed_sell_setups 
    )
    sell_countdown_markers = calculate_td_countdown(
        data, 
        completed_sell_setups, 
        "sell", 
        user_params["sell_countdown_color"],
        only_complete_countdown=user_params["show_only_complete_countdown"],
        contrary_setups=completed_buy_setups 
    )

    # Agregar todos los marcadores y ordenarlos por tiempo
    markers.extend(setup_markers)
    markers.extend(buy_countdown_markers)
    markers.extend(sell_countdown_markers)
    markers = sorted(markers, key=lambda x: x["time"])

    # Agregar los markers al gráfico principal
    if markers:
        if "markers" in charts_config[0]["series"][0]:
            charts_config[0]["series"][0]["markers"].extend(markers)
        else:
            charts_config[0]["series"][0]["markers"] = markers

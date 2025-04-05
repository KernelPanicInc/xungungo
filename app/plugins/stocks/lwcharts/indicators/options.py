import streamlit as st
import requests
import datetime
import pandas as pd

@st.cache_data(ttl=600)
def fetch_options_data(ticker="NVDA", fromdate="all", todate="undefined"):
    url = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain"
    params = {
        "assetclass": "stocks",
        "limit": 5000,
        "fromdate": fromdate,
        "todate": todate,
        "excode": "oprac",
        "callput": "callput",
        "money": "all",
        "type": "all",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code != 200:
        st.warning(f"No se pudo obtener data. HTTP: {resp.status_code}")
        return {}
    return resp.json()

name = "Key Option Levels"
description = "Obtiene y dibuja líneas horizontales para niveles clave de Open Interest y Max Pain de opciones, usando la API de Nasdaq."

def obtener_lista_meses():
    inicio = datetime.date(2025, 3, 1)
    fin = datetime.date(2025, 12, 1)
    meses = []
    actual = inicio
    while actual <= fin:
        meses.append(actual.strftime("%B %Y"))
        if actual.month == 12:
            actual = datetime.date(actual.year + 1, 1, 1)
        else:
            actual = datetime.date(actual.year, actual.month + 1, 1)
    # Agregamos "All" al inicio
    meses = ["All"] + meses
    return meses

def hex_to_rgba(hex_color: str, opacity: float):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {opacity})"

def calculate_max_pain(strikes, call_oi, put_oi):
    """
    Calcula el valor de max pain: para cada posible strike (en la lista de strikes),
    se calcula la suma de las pérdidas teóricas de los calls y puts.
    Se considera para cada strike candidato X:
        pérdida_call = sum( max(0, X - strike_i) * call_oi_i )
        pérdida_put  = sum( max(0, strike_i - X) * put_oi_i )
    El strike con la suma mínima es el max pain.
    """
    pain_dict = {}
    for x in strikes:
        total_pain = 0
        for strike, c, p in zip(strikes, call_oi, put_oi):
            call_loss = max(0, x - strike) * c
            put_loss = max(0, strike - x) * p
            total_pain += call_loss + put_loss
        pain_dict[x] = total_pain
    # Retornamos el strike con menor dolor
    max_pain_strike = min(pain_dict, key=pain_dict.get)
    return max_pain_strike

def get_user_params(data: pd.DataFrame) -> dict:
    with st.sidebar.expander("Parámetros - Key Option Levels", expanded=False):
        lista_meses = obtener_lista_meses()
        mes_seleccionado = st.selectbox("Selecciona el mes de expiración", lista_meses)
        if mes_seleccionado == "All":
            fromdate = "all"
            todate = "undefined"
        else:
            date_obj = datetime.datetime.strptime(mes_seleccionado, "%B %Y")
            primer_dia = date_obj.replace(day=1)
            ultimo_dia = (primer_dia.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
            fromdate = primer_dia.strftime("%Y-%m-%d")
            todate = ultimo_dia.strftime("%Y-%m-%d")
        st.write(f"Parámetros de búsqueda: fromdate={fromdate}, todate={todate}")

        show_call_oi = st.checkbox("Mostrar Máximo Call OI", value=True)
        color_call_oi = "#FF0000"
        if show_call_oi:
            color_call_oi = st.color_picker("Color línea Max Call OI", "#FF0000")

        show_put_oi = st.checkbox("Mostrar Máximo Put OI", value=True)
        color_put_oi = "#0000FF"
        if show_put_oi:
            color_put_oi = st.color_picker("Color línea Max Put OI", "#0000FF")

        show_total_oi = st.checkbox("Mostrar Máximo OI Total (Calls+Puts)", value=False)
        color_total_oi = "#008000"
        if show_total_oi:
            color_total_oi = st.color_picker("Color línea Max OI Total", "#008000")

        show_max_pain = st.checkbox("Mostrar Max Pain", value=True)
        color_max_pain = "#FFA500"
        if show_max_pain:
            color_max_pain = st.color_picker("Color línea Max Pain", "#FFA500")

        line_width = st.slider("Ancho de Líneas", min_value=1, max_value=5, value=2)
    return {
        "fromdate": fromdate,
        "todate": todate,
        "show_call_oi": show_call_oi,
        "color_call_oi": color_call_oi,
        "show_put_oi": show_put_oi,
        "color_put_oi": color_put_oi,
        "show_total_oi": show_total_oi,
        "color_total_oi": color_total_oi,
        "show_max_pain": show_max_pain,
        "color_max_pain": color_max_pain,
        "line_width": line_width
    }

def apply(charts_config: list, data: pd.DataFrame, user_params: dict):
    # Verificar que la columna 'Fecha' exista en los datos
    if "Fecha" not in data.columns:
        st.warning("No se encontró la columna 'Fecha' en los datos. No se dibujarán los niveles de opciones.")
        return

    ticker = user_params.get("ticker", "NVDA")
    fromdate = user_params.get("fromdate")
    todate = user_params.get("todate")
    # Obtener datos de opciones de la API
    options_json = fetch_options_data(ticker, fromdate, todate)
    if not options_json:
        return

    rows = options_json.get("data", {}).get("table", {}).get("rows", [])
    option_rows = [r for r in rows if r.get("strike")]

    strike_list = []
    call_oi_list = []
    put_oi_list = []

    for row in option_rows:
        strike_str = row.get("strike", "").replace("--", "0")
        try:
            strike_val = float(strike_str)
        except:
            continue
        c_oi_str = row.get("c_Openinterest", "0").replace("--", "0")
        p_oi_str = row.get("p_Openinterest", "0").replace("--", "0")
        try:
            c_oi = float(c_oi_str)
        except:
            c_oi = 0.0
        try:
            p_oi = float(p_oi_str)
        except:
            p_oi = 0.0
        strike_list.append(strike_val)
        call_oi_list.append(c_oi)
        put_oi_list.append(p_oi)

    if not strike_list:
        st.warning("No se encontraron datos de opciones para el ticker seleccionado.")
        return

    # Calcular niveles de Open Interest
    max_call_oi_strike = None
    second_call_oi_strike = None
    if user_params["show_call_oi"] and any(call_oi_list):
        sorted_call_indices = sorted(range(len(call_oi_list)), key=lambda i: call_oi_list[i], reverse=True)
        max_call_oi_strike = strike_list[sorted_call_indices[0]]
        if len(sorted_call_indices) > 1:
            second_call_oi_strike = strike_list[sorted_call_indices[1]]

    max_put_oi_strike = None
    second_put_oi_strike = None
    if user_params["show_put_oi"] and any(put_oi_list):
        sorted_put_indices = sorted(range(len(put_oi_list)), key=lambda i: put_oi_list[i], reverse=True)
        max_put_oi_strike = strike_list[sorted_put_indices[0]]
        if len(sorted_put_indices) > 1:
            second_put_oi_strike = strike_list[sorted_put_indices[1]]

    max_total_oi_strike = None
    if user_params["show_total_oi"]:
        total_oi_list = [c + p for c, p in zip(call_oi_list, put_oi_list)]
        if any(total_oi_list):
            idx_total = max(range(len(total_oi_list)), key=lambda i: total_oi_list[i])
            max_total_oi_strike = strike_list[idx_total]

    # Calcular el max pain si se desea
    max_pain_strike = None
    if user_params.get("show_max_pain"):
        max_pain_strike = calculate_max_pain(strike_list, call_oi_list, put_oi_list)

    # Extraer los timestamps de los datos para generar las líneas horizontales
    timestamps = []
    for _, row in data.iterrows():
        if pd.notna(row["Fecha"]):
            timestamps.append(int(row["Fecha"].timestamp()))
    if not timestamps:
        st.warning("No se pudieron extraer timestamps de los datos.")
        return

    line_width = user_params.get("line_width", 2)

    # Función auxiliar para añadir una línea horizontal en charts_config
    def add_horizontal_line(y_value, label, color, base_opacity=1.0):
        if y_value is None:
            return
        rgba_color = hex_to_rgba(color, base_opacity)
        line_data = [{"time": ts, "value": y_value} for ts in timestamps]
        charts_config[0]["series"].append({
            "type": "Line",
            "data": line_data,
            "options": {
                "lineWidth": line_width,
                "color": rgba_color,
                "title": label
            }
        })

    # Agregar las líneas horizontales para cada indicador
    add_horizontal_line(max_call_oi_strike, "Max Call OI", user_params["color_call_oi"], base_opacity=1.0)
    add_horizontal_line(second_call_oi_strike, "2nd Max Call OI", user_params["color_call_oi"], base_opacity=0.3)
    add_horizontal_line(max_put_oi_strike, "Max Put OI", user_params["color_put_oi"], base_opacity=1.0)
    add_horizontal_line(second_put_oi_strike, "2nd Max Put OI", user_params["color_put_oi"], base_opacity=0.3)
    add_horizontal_line(max_total_oi_strike, "Max OI Total", user_params["color_total_oi"], base_opacity=1.0)
    add_horizontal_line(max_pain_strike, "Max Pain", user_params["color_max_pain"], base_opacity=1.0)

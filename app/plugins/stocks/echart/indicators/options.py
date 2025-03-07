import streamlit as st
import requests
import re
import datetime

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
plugin_type = "overlay"

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

def get_user_params(df=None):
    with st.sidebar.expander("Parámetros - Key Option Levels", expanded=False):
        # Selectbox para filtrar expiraciones
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

        # Parámetros generales
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

        line_width = st.slider("Ancho de Líneas", min_value=1, max_value=5, value=2)

    return {
        "show_call_oi": show_call_oi,
        "color_call_oi": color_call_oi,
        "show_put_oi": show_put_oi,
        "color_put_oi": color_put_oi,
        "show_total_oi": show_total_oi,
        "color_total_oi": color_total_oi,
        "line_width": line_width,
        "fromdate": fromdate,
        "todate": todate
    }

def apply_overlay(kline_obj, data, dates, user_params, params):
    print("Aplicando líneas de Open Interest...")
    from pyecharts.charts import Line
    from pyecharts import options as opts

    ticker = params.get("ticker", "NVDA")

    show_call_oi    = user_params["show_call_oi"]
    color_call_oi   = user_params["color_call_oi"]
    show_put_oi     = user_params["show_put_oi"]
    color_put_oi    = user_params["color_put_oi"]
    show_total_oi   = user_params["show_total_oi"]
    color_total_oi  = user_params["color_total_oi"]
    line_width      = user_params["line_width"]

    fromdate        = user_params["fromdate"]
    todate          = user_params["todate"]

    # Obtener datos de la API
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
        return

    # Ordenamos y encontramos los máximos (y segundos máximos)
    max_call_oi_strike = None
    second_call_oi_strike = None
    if show_call_oi and any(call_oi_list):
        # Ordenamos de mayor a menor
        sorted_call_indices = sorted(range(len(call_oi_list)), key=lambda i: call_oi_list[i], reverse=True)
        # Primer mayor
        idx_call = sorted_call_indices[0]
        max_call_oi_strike = strike_list[idx_call]
        # Segundo mayor (solo si hay al menos 2 strikes)
        if len(sorted_call_indices) > 1:
            second_call_oi_strike = strike_list[sorted_call_indices[1]]

    max_put_oi_strike = None
    second_put_oi_strike = None
    if show_put_oi and any(put_oi_list):
        # Ordenamos de mayor a menor
        sorted_put_indices = sorted(range(len(put_oi_list)), key=lambda i: put_oi_list[i], reverse=True)
        idx_put = sorted_put_indices[0]
        max_put_oi_strike = strike_list[idx_put]
        if len(sorted_put_indices) > 1:
            second_put_oi_strike = strike_list[sorted_put_indices[1]]

    max_total_oi_strike = None
    if show_total_oi:
        total_oi_list = [c + p for c, p in zip(call_oi_list, put_oi_list)]
        if any(total_oi_list):
            idx_total = max(range(len(total_oi_list)), key=lambda i: total_oi_list[i])
            max_total_oi_strike = strike_list[idx_total]

    # Función para añadir líneas horizontales
    def add_horizontal_line(y_value, label, color, opacity=1.0):
        if y_value is None:
            return
        line = (
            Line()
            .add_xaxis(dates)
            .add_yaxis(
                series_name=label,
                y_axis=[y_value] * len(dates),  # Línea horizontal
                symbol="none",
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=color),
                linestyle_opts=opts.LineStyleOpts(
                    width=line_width,
                    color=color,
                    type_="dashed",
                    opacity=opacity  # Ajusta la transparencia
                ),
                # Para mostrar el nombre en la marca del tooltip
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(y=y_value, name=label)],
                    # Color de la etiqueta:
                    label_opts=opts.LabelOpts(color=color)
                ),
                yaxis_index=0,
                z=5,
            )
        )
        kline_obj.overlap(line)

    # Agregamos la línea principal y la segunda línea con opacidad menor
    add_horizontal_line(max_call_oi_strike, "Max Call OI", color_call_oi, opacity=1.0)
    add_horizontal_line(second_call_oi_strike, "2nd Max Call OI", color_call_oi, opacity=0.3)

    add_horizontal_line(max_put_oi_strike, "Max Put OI", color_put_oi, opacity=1.0)
    add_horizontal_line(second_put_oi_strike, "2nd Max Put OI", color_put_oi, opacity=0.3)

    # Para total OI no estamos mostrando un segundo máximo,
    # pero podrías implementarlo de forma análoga si quieres.
    add_horizontal_line(max_total_oi_strike, "Max OI Total", color_total_oi, opacity=1.0)

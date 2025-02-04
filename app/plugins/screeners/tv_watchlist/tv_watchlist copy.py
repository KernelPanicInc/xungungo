import requests
import json
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

# Información básica del plugin
nombre = "TradingView Watchlist Plugin"
descripcion = "Plugin que obtiene una lista de símbolos desde una watchlist de TradingView."
tipo = "tv_watchlist"

def get_parametros_config():
    """
    Retorna los parámetros configurables específicos del plugin.
    """
    return {
        "url": {
            "label": "URL de la Watchlist de TradingView",
            "default": "https://www.tradingview.com/watchlist/public/example",
        },
        "columns": {
            "label": "Columnas para mostrar (separadas por comas)",
            "default": "Perf.W, Perf.1M, Perf.3M, Perf.YTD, Perf.Y, Perf.5Y, Recommend.All",
        },
    }

def render_parametros_config(parametros):
    """
    Renderiza los parámetros configurables en la interfaz de Streamlit.
    """
    url = st.text_input(parametros["url"]["label"], value=parametros["url"]["default"])
    columns = st.text_input(parametros["columns"]["label"], value=parametros["columns"]["default"])
    return {"url": url, "columns": columns}

def obtener_watchlist_symbols(url):
    """
    Extrae los símbolos de una watchlist pública de TradingView desde la URL proporcionada.
    """
    #st.write("URL solicitada:", url)  # Debug
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"No se pudo obtener la watchlist. Código de estado: {response.status_code}")
        return []

    # Parsear el contenido HTML con Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscar el bloque JSON dentro del <script>
    script_tag = soup.find('script', {'type': 'application/prs.init-data+json'})
    if not script_tag:
        st.error("No se encontró el bloque JSON en la página proporcionada. Verifica si la estructura de la página cambió.")
        return []

    try:
        # Extraer el contenido del <script> y cargar el JSON
        raw_json = script_tag.string
        #st.write("JSON capturado:", raw_json[:500])  # Mostrar los primeros 500 caracteres del JSON

        # Convertir el string JSON en un diccionario
        json_data = json.loads(raw_json)
        symbols = json_data.get("sharedWatchlist", {}).get("list", {}).get("symbols", [])
        if symbols:
            st.success(f"Se encontraron {len(symbols)} símbolos.")
        else:
            st.warning("No se encontraron símbolos en la watchlist.")
        return symbols
    except json.JSONDecodeError as e:
        st.error(f"Error al procesar el JSON de la watchlist: {e}")
        return []
    except Exception as e:
        st.error(f"Error inesperado al procesar la watchlist: {e}")
        return []

def obtener_datos_tradingview(symbols, columns):
    """
    Consulta la API de TradingView con los símbolos obtenidos.
    """
    url = "https://scanner.tradingview.com/global/scan?label-product=popup-watchlists"
    payload = {
        "columns": columns,
        "symbols": {"tickers": symbols},
    }

    headers = {
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/",
        "User-Agent": "Mozilla/5.0",
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error("No se pudo obtener la información de TradingView.")
        st.error(f"Código de estado: {response.text}")
        return pd.DataFrame()

    data = response.json().get("data", [])
    if not data:
        st.warning("No se encontraron datos para los símbolos proporcionados.")
        return pd.DataFrame()

    df = pd.DataFrame([{"Símbolo": entry["s"], **dict(zip(payload["columns"], entry["d"]))} for entry in data])
    return df

def style_dataframe(df):
    """
    Aplica estilos al DataFrame para resaltar valores positivos y negativos.
    """
    def highlight_values(val):
        if isinstance(val, (int, float)):
            color = 'green' if val > 0 else 'red' if val < 0 else 'black'
            return f'color: {color}'
        return None

    return df.style.applymap(highlight_values)

def render(config):
    """
    Renderiza el plugin en Streamlit.
    """
    url = config.get("url", "")
    columns = config.get("columns", "Perf.W, Perf.1M, Perf.3M, Perf.YTD, Perf.Y, Perf.5Y, Recommend.All")

    if not url:
        st.error("No se proporcionó una URL válida.")
        return

    symbols = obtener_watchlist_symbols(url)

    if symbols:
        st.write(f"Se encontraron {len(symbols)} símbolos en la watchlist.")
        df = obtener_datos_tradingview(symbols, columns)

        if not df.empty:
            styled_df = style_dataframe(df)
            numRows = len(df)
            calculated_height = (numRows + 1) * 35 + 3
            st.dataframe(styled_df, height=calculated_height)
        else:
            st.warning("El DataFrame está vacío.")
    else:
        st.warning("No se encontraron símbolos en la watchlist proporcionada.")

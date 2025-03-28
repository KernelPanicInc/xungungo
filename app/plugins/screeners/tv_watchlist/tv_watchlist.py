import requests
import json
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode
from io import BytesIO

# Información básica del plugin
nombre = "TradingView Watchlist Plugin"
descripcion = "Plugin que obtiene una lista de símbolos desde una watchlist de TradingView."
tipo = "tv_watchlist"

def render_config(screener_config):
    """
    Renderiza los campos de configuración para el plugin usando un text_input para la URL
    y un multiselect para las columnas.
    Actualiza el diccionario 'screener_config' con los valores ingresados.
    """
    # Configurar el parámetro URL
    default_url = "https://www.tradingview.com/watchlist/public/example"
    url_value = screener_config.get("url", default_url)
    nuevo_url = st.text_input(
        "URL de la Watchlist de TradingView",
        value=url_value,
        key="url_config"
    )
    screener_config["url"] = nuevo_url

    # Configurar el parámetro columns usando un multiselect
    # Definir las opciones disponibles (puedes modificar o ampliar esta lista según tus necesidades)
    opciones_columns = [
        "close", "open", "high", "low", "volume",
        "Perf.W", "Perf.1M", "Perf.3M", "Perf.YTD",
        "Perf.Y", "Perf.5Y", "Perf.All", "Recommend.All", "beta_1_year",
        "beta_3_year", "beta_5_year", "Volatility.D",
        "Volatility.W", "Volatility.M", "Recommend.MA",
        "Recommend.Other", "RSI", "Mom", "AO", "CCI20"
    ]
    # Obtener el valor actual; si no existe, usar una lista por defecto
    default_columns = ["close","Perf.W", "Perf.1M", "Perf.3M", "Perf.YTD", "Perf.Y", "Perf.5Y", "Recommend.All"]
    current_columns = screener_config.get("columns", default_columns)
    # Si current_columns viene en forma de cadena, convertirla a lista
    if isinstance(current_columns, str):
        current_columns = [col.strip() for col in current_columns.split(",") if col.strip()]
    # Mostrar el multiselect para elegir las columnas
    selected_columns = st.multiselect(
        "Columnas para mostrar",
        options=opciones_columns,
        default=current_columns,
        key="columns_config"
    )
    screener_config["columns"] = selected_columns


def obtener_watchlist_symbols(url):
    """
    Extrae los símbolos de una watchlist pública de TradingView desde la URL proporcionada.
    """
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

def to_excel(df):
    """
    Convierte un DataFrame de pandas a un archivo Excel en memoria.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Watchlist')
    processed_data = output.getvalue()
    return processed_data

def render(config):
    """
    Renderiza el plugin en Streamlit.
    """
    url = config.get("url", "")
    columns = [col.strip() for col in config.get("columns", [])]  # Maneja 'columns' como lista

    if not url:
        st.error("No se proporcionó una URL válida.")
        return

    symbols = obtener_watchlist_symbols(url)

    if symbols:
        st.write(f"Se encontraron {len(symbols)} símbolos en la watchlist.")
        df = obtener_datos_tradingview(symbols, columns)

        if not df.empty:
            # Definir código JS para estilizar celdas
            cell_style_jscode = JsCode("""
                function(params) {
                    if (typeof params.value === 'number') {
                        if (params.value > 0) {
                            return { 'color': 'green' };
                        } else if (params.value < 0) {
                            return { 'color': 'red' };
                        }
                    }
                    return null;
                }
            """)

            # Configurar AgGrid sin filtros en la barra lateral
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(enabled=True, paginationAutoPageSize=True)  # Paginación con 100 filas por página
            gb.configure_side_bar()  # Barra lateral para filtros adicionales de AgGrid
            gb.configure_default_column(filter=True, sortable=True, resizable=True)  # Columnas filtrables, ordenables y resizables

            # Aplicar estilos condicionales a columnas numéricas
            numeric_columns = df.select_dtypes(include=['float', 'int']).columns.tolist()
            for col in numeric_columns:
                gb.configure_column(col, cellStyle=cell_style_jscode)

            gridOptions = gb.build()

            # Establecer una altura fija con scroll vertical
            grid_height = 750  # Puedes ajustar este valor según tus necesidades

            # Renderizar AgGrid
            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                height=grid_height,  # Altura fija para manejar scroll
                width='100%',
                update_mode=GridUpdateMode.NO_UPDATE,  # Ajusta según necesites
                allow_unsafe_jscode=True,  # Permitir código JS personalizado si es necesario
            )

            # Agregar un botón de descarga para exportar a Excel
            st.markdown("### Exportar Datos")
            excel_data = to_excel(df)
            st.download_button(
                label="Descargar como Excel",
                data=excel_data,
                file_name='watchlist.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("El DataFrame está vacío.")
    else:
        st.warning("No se encontraron símbolos en la watchlist proporcionada.")

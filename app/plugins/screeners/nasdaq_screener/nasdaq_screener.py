import requests
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode
from io import BytesIO

# Información básica del plugin
nombre = "NASDAQ Stocks Plugin"
descripcion = "Plugin que obtiene una lista de acciones desde la API de NASDAQ."
tipo = "nasdaq_screener"

def get_parametros_config():
    """
    Retorna los parámetros configurables específicos del plugin.
    """
    return {
        "limit": {
            "label": "Número de acciones a obtener",
            "default": 25,
        },
        "columns": {
            "label": "Columnas para mostrar (lista)",
            "default": [
                "symbol", 
                "name", 
                "lastsale", 
                "netchange", 
                "pctchange", 
                "marketCap", 
                "country", 
                "ipoyear", 
                "volume", 
                "sector", 
                "industry"
            ],
        },
    }

def obtener_datos_nasdaq(limit):
    """
    Obtiene datos de la API de NASDAQ.
    """
    url = f"https://api.nasdaq.com/api/screener/stocks?tableonly=false&limit={limit}&download=true"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'es-ES,es;q=0.9',
        'origin': 'https://www.nasdaq.com',
        'priority': 'u=1, i',
        'referer': 'https://www.nasdaq.com/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"No se pudo obtener la información de NASDAQ. Código de estado: {response.status_code}")
        return pd.DataFrame()

    data = response.json().get("data", {})
    rows = data.get("rows", [])
    if not rows:
        st.warning("No se encontraron datos en la API de NASDAQ.")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    return df

def to_excel(df):
    """
    Convierte un DataFrame de pandas a un archivo Excel en memoria.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='NASDAQ Stocks')
    processed_data = output.getvalue()
    return processed_data

def render(config):
    """
    Renderiza el plugin en Streamlit.
    """
    limit = config.get("limit", 25)

    st.subheader("NASDAQ Stocks")
    df = obtener_datos_nasdaq(limit)

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
            file_name='nasdaq_stocks.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning("No se encontraron datos en la API de NASDAQ.")

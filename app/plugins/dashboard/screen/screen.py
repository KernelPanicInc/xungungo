import json
import pandas as pd
import streamlit as st
import yfinance as yf

nombre = "Stock Screener"
descripcion = "Plugin que ejecuta un screening usando yfinance.screen y muestra solo Symbol y regularMarketChangePercent formateado."
tipo = "screen"

default_config = {
    "query_mode": "most_actives",
    "custom_query": "",
    "offset": 0,
    "size": 10,
    "sortField": "ticker",
    "sortAsc": False,
    "height": 400  # Altura por defecto del widget (en píxeles)
}

def config(current_config: dict) -> dict:
    st.write("### Configuración del Stock Screener")
    query_mode_default = current_config.get("query_mode", default_config["query_mode"])
    custom_query_default = current_config.get("custom_query", default_config["custom_query"])
    offset_default = current_config.get("offset", default_config["offset"])
    size_default = current_config.get("size", default_config["size"])
    sortField_default = current_config.get("sortField", default_config["sortField"])
    sortAsc_default = current_config.get("sortAsc", default_config["sortAsc"])
    height_default = current_config.get("height", default_config["height"])

    try:
        predefined_queries = list(yf.PREDEFINED_SCREENER_QUERIES.keys())
    except Exception:
        predefined_queries = ["most_actives", "day_gainers", "day_losers"]

    query_options = predefined_queries + ["custom"]
    if query_mode_default not in query_options:
        query_mode_default = query_options[0]
    
    selected_mode = st.selectbox(
        "Consulta predefinida",
        options=query_options,
        index=query_options.index(query_mode_default),
        help="Selecciona una consulta predefinida o 'custom' para ingresar una consulta manual."
    )
    
    if selected_mode == "custom":
        st.write("#### Consulta Personalizada")
        st.caption("Ejemplo: and(region=us, intradaymarketcap>2000000000)")
        custom_query_val = st.text_area("Ingresa la consulta (cadena)", value=custom_query_default)
    else:
        custom_query_val = ""

    offset_val = st.number_input("Offset", min_value=0, value=offset_default, step=1)
    size_val = st.number_input("Tamaño de resultados (size)", min_value=1, max_value=250, value=size_default, step=1)
    sortField_val = st.text_input("Campo para ordenar (sortField)", value=sortField_default)
    sortAsc_val = st.checkbox("Orden ascendente (sortAsc)", value=sortAsc_default)
    height_val = st.slider("Altura del widget (px)", min_value=200, max_value=800, value=height_default, step=50)

    return {
        "query_mode": selected_mode,
        "custom_query": custom_query_val,
        "offset": offset_val,
        "size": size_val,
        "sortField": sortField_val,
        "sortAsc": sortAsc_val,
        "height": height_val
    }

def render(config: dict):
    st.write(f"Screener: {config.get('query_mode', 'most_actives')}")
    
    query_mode = config.get("query_mode", default_config["query_mode"])
    custom_query = config.get("custom_query", default_config["custom_query"])
    offset_val = config.get("offset", default_config["offset"])
    size_val = config.get("size", default_config["size"])
    sortField_val = config.get("sortField", default_config["sortField"])
    sortAsc_val = config.get("sortAsc", default_config["sortAsc"])
    height_val = int(config.get("height", default_config["height"]))-81  # Ajustar altura para evitar scroll

    try:
        if query_mode == "custom":
            response = yf.screen(
                query=custom_query,
                offset=offset_val,
                size=size_val,
                sortField=sortField_val if sortField_val else None,
                sortAsc=sortAsc_val
            )
        else:
            response = yf.screen(query_mode)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        return

    # Convertir la respuesta a DataFrame
    if isinstance(response, pd.DataFrame):
        df = response
    elif isinstance(response, dict):
        quotes = response.get("quotes", None)
        if quotes is None or not isinstance(quotes, list):
            st.error("La respuesta no contiene datos en 'quotes'.")
            st.json(response)
            return
        df = pd.DataFrame(quotes)
    else:
        st.error(f"Tipo de respuesta no esperado: {type(response)}")
        st.write(response)
        return

    # Filtrar solo las columnas mínimas importantes
    columns_to_show = ["symbol", "regularMarketChangePercent"]
    missing_cols = [col for col in columns_to_show if col not in df.columns]
    if missing_cols:
        st.error(f"Las siguientes columnas no están presentes en los resultados: {missing_cols}")
        st.dataframe(df, use_container_width=True)
        return

    df_filtered = df[columns_to_show].copy()

    # Formatear 'regularMarketChangePercent': agregar "%" y aplicar estilo en verde si es positivo
    def format_change(val):
        try:
            num = float(val)
            return f"{num:.2f}%"
        except Exception:
            return val

    df_filtered["regularMarketChangePercent"] = df_filtered["regularMarketChangePercent"].apply(format_change)
    
    # Aplicar estilo: color verde a valores positivos
    def color_positive(val):
        try:
            num = float(val.replace("%", ""))
            if num > 0:
                return "color: green"
        except Exception:
            pass
        return ""

    styled_df = df_filtered.style.applymap(color_positive, subset=["regularMarketChangePercent"])
    
    st.dataframe(styled_df, use_container_width=True, height=height_val)

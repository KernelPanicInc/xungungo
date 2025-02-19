import streamlit as st
import requests
import pandas as pd
import altair as alt
from pages.darkpools.dialog_issue_info import render_issue_info
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode


st.title("Resumen de Dark Pools - FINRA")

st.markdown('''<style>
div[data-testid="stModal"] div[role="dialog"] {
    width: 80%;
}
</style>''', unsafe_allow_html=True)

# Definir headers comunes para las peticiones
headers = {
    "accept": "application/json",
    "accept-language": "es-ES,es;q=0.9",
    "content-type": "application/json",
    "origin": "https://otctransparency.finra.org",
    "referer": "https://otctransparency.finra.org/"
}

# --- Obtener fechas disponibles desde weeklyDownloadDetails ---
with st.spinner("Obteniendo fechas disponibles..."):
    dates_url = "https://api.finra.org/data/group/otcMarket/name/weeklyDownloadDetails"
    dates_payload = {
        "quoteValues": False,
        "delimiter": "|",
        "limit": 27,
        "fields": ["weekStartDate"],
        "sortFields": ["-weekStartDate"],
        "compareFilters": [
            {"fieldName": "summaryTypeCode", "fieldValue": "ATS_W_SMBL", "compareType": "EQUAL"},
            {"fieldName": "tierIdentifier", "fieldValue": "T1", "compareType": "EQUAL"}
        ]
    }
    
    dates_response = requests.post(dates_url, headers=headers, json=dates_payload)
    if dates_response.status_code == 200:
        dates_data = dates_response.json()
        # Extraer las fechas disponibles
        available_dates = [item["weekStartDate"] for item in dates_data if "weekStartDate" in item]
        # Ordenar de forma descendente (la fecha más reciente primero)
        available_dates = sorted(available_dates, reverse=True)
    else:
        st.error("Error al obtener las fechas disponibles.")
        available_dates = []

if available_dates:
    # --- Filtros en la barra lateral ---
    st.sidebar.header("Filtros de Búsqueda")
    selected_date = st.sidebar.selectbox(
        "Seleccione la fecha de inicio de la semana",
        options=available_dates,
        index=0  # Por defecto, la fecha más reciente (última fecha)
    )
    limit = st.sidebar.number_input("Límite de registros", value=5000, min_value=1)
    
    # --- Consultar datos desde weeklySummary usando la fecha seleccionada ---
    with st.spinner("Cargando datos..."):
        summary_url = "https://api.finra.org/data/group/otcMarket/name/weeklySummary"
        summary_payload = {
            "quoteValues": False,
            "delimiter": "|",
            "limit": limit,
            "fields": [
                "productTypeCode",
                "issueSymbolIdentifier",
                "issueName",
                "totalWeeklyShareQuantity",
                "totalWeeklyTradeCount",
                "lastUpdateDate"
            ],
            "compareFilters": [
                {
                    "fieldName": "weekStartDate",
                    "fieldValue": selected_date,
                    "compareType": "EQUAL"
                },
                {
                    "fieldName": "tierIdentifier",
                    "fieldValue": "T1",
                    "compareType": "EQUAL"
                },
                {
                    "fieldName": "summaryTypeCode",
                    "fieldValue": "ATS_W_SMBL",
                    "compareType": "EQUAL"
                }
            ]
        }
        
        summary_response = requests.post(summary_url, headers=headers, json=summary_payload)
    
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        if isinstance(summary_data, list) and len(summary_data) > 0:
            df = pd.DataFrame(summary_data)
            st.success(f"Datos cargados exitosamente: {len(df)} registros")
            
            # --- Mostrar métricas resumidas ---
            total_shares = df["totalWeeklyShareQuantity"].sum()
            total_trades = df["totalWeeklyTradeCount"].sum()
            col1, col2 = st.columns(2)
            col1.metric("Total Acciones Negociadas", f"{total_shares:,}")
            col2.metric("Total Operaciones", f"{total_trades:,}")
            
            # --- Gráfico: Top 10 Acciones Más Operadas ---
            st.subheader("Top 10 Acciones Más Operadas")
            df_shares = df.sort_values("totalWeeklyShareQuantity", ascending=False).head(10)
            chart_shares = alt.Chart(df_shares).mark_bar().encode(
                x=alt.X('issueSymbolIdentifier:N', sort='-y', title="Símbolo del Issue"),
                y=alt.Y('totalWeeklyShareQuantity:Q', title="Total Acciones Negociadas"),
                tooltip=["issueName", "totalWeeklyShareQuantity"]
            ).properties(width=700, height=400)
            st.altair_chart(chart_shares, use_container_width=True)
            
            # --- Tabla interactiva usando st_aggrid ---
            st.subheader("Datos Detallados")
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_selection(selection_mode="single")
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=False)
            gb.configure_grid_options()
            gridOptions = gb.build()
            grid_response = AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=False, theme="streamlit",data_return_mode=DataReturnMode.AS_INPUT,update_mode=GridUpdateMode.SELECTION_CHANGED)
            selected_rows = grid_response["selected_rows"]

            if selected_rows is not None and not selected_rows.empty:
                primer_fila = selected_rows.iloc[0]
                st.write("Fila(s) seleccionada(s):", primer_fila['issueSymbolIdentifier'])
                render_issue_info(primer_fila['issueSymbolIdentifier'], selected_date)
            
        else:
            st.warning("No se encontraron datos para la fecha seleccionada.")
    else:
        st.error(f"Error al cargar datos. Código de estado: {summary_response.status_code}")
else:
    st.error("No hay fechas disponibles para seleccionar.")

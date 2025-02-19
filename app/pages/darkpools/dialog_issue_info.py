import streamlit as st
import requests
import pandas as pd

@st.dialog("Info")
def render_issue_info(issueSymbolIdentifier, date):
    st.write(f"Info de {issueSymbolIdentifier} en semana {date}")

    url = "https://api.finra.org/data/group/otcMarket/name/weeklySummary"
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    payload = {
        "quoteValues": False,
        "delimiter": "|",
        "limit": 5000,
        "sortFields": ["-totalWeeklyShareQuantity"],
        "compareFilters": [
            {"fieldName": "summaryTypeCode", "fieldValue": "ATS_W_SMBL_FIRM", "compareType": "EQUAL"},
            {"fieldName": "issueSymbolIdentifier", "fieldValue": issueSymbolIdentifier, "compareType": "EQUAL"},
            {"fieldName": "weekStartDate", "fieldValue": date, "compareType": "EQUAL"},
            {"fieldName": "tierIdentifier", "fieldValue": "T1", "compareType": "EQUAL"}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        if data:
            df = pd.DataFrame(data)
            columnas_relevantes = ["marketParticipantName", "totalWeeklyShareQuantity", "totalWeeklyTradeCount"]
            columnas_a_mostrar = [col for col in columnas_relevantes if col in df.columns]
            df = df[columnas_a_mostrar]
            
            # Renombramos las columnas por algo más descriptivo
            df = df.rename(columns={
                "marketParticipantName": "ATS",
                "totalWeeklyShareQuantity": "Week Shares",
                "totalWeeklyTradeCount": "Trades"
            })
            
            st.table(df)
        else:
            st.write("No se encontraron datos para los parámetros indicados.")
    else:
        st.error(f"Error en la consulta: {response.status_code}")

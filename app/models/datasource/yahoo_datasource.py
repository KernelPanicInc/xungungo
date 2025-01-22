import requests
import streamlit as st
# Define la función para consultar el servicio
def search_service(searchterm: str) -> list:
    if not searchterm:
        return []
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": searchterm}
    try:
        
        response = requests.get(
                    url, 
                    params=params, 
                    timeout=60, 
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit"
                        "/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
                    },
                    )
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP no exitosos
        data = response.json()
        # Devuelve los resultados en formato de tuplas
        return [(f"{item['longname']} ({item['symbol']})", item["symbol"]) for item in data.get("quotes", []) if "longname" in item and "symbol" in item]
    except requests.exceptions.RequestException as e:
        # Maneja la excepción y devuelve una lista vacía o un mensaje de error
        st.error("Error al consultar el servicio. Por favor, intenta de nuevo.")
        st.error(e)
        return e
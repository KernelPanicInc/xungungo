import requests
import streamlit as st

# 1️⃣  Separamos la configuración común para poder re-usarla en varios calls si lo necesitas.
SESSION = requests.Session()
SESSION.headers.update({
    # Pedimos JSON (o cualquier cosa) explícitamente
    "Accept": "*/*",
    "Accept-Language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-CL;q=0.5",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
    ),
    # Encabezados CORS que Yahoo espera aunque tu llamada no sea desde un navegador
    "Origin": "https://finance.yahoo.com",
    "Referer": "https://finance.yahoo.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
})

def search_service(searchterm: str) -> list[tuple[str, str]]:
    """Devuelve una lista de (nombre largo, símbolo) para el término buscado."""
    if not searchterm:
        return []

    url = "https://query2.finance.yahoo.com/v1/finance/search"

    # 2️⃣  Replicamos el bloque de parámetros del *curl*,
    #     con el término de búsqueda en `q`.
    params = {
        "q": searchterm,
        "lang": "en-US",
        "region": "US",
        "quotesCount": 7,
        "quotesQueryId": "tss_match_phrase_query",
        "multiQuoteQueryId": "multi_quote_single_token_query",
        "enableCb": "false",
        "enableNavLinks": "true",
        "enableCulturalAssets": "true",
        "enableNews": "false",
        "enableResearchReports": "false",
        "enableLists": "false",
        "listsCount": 2,
        "recommendCount": 6,
        "enablePrivateCompany": "true",
    }

    try:
        resp = SESSION.get(url, params=params, timeout=15)
        resp.raise_for_status()                 # 3️⃣  Errores HTTP
        data = resp.json()                      # 4️⃣  Errores de parseo → except JSONDecodeError

        return [
            (f"{item['longname']} ({item['symbol']})", item["symbol"])
            for item in data.get("quotes", [])
            if item.get("longname") and item.get("symbol")
        ]

    except requests.exceptions.JSONDecodeError:
        st.error("La respuesta no estaba en formato JSON (Yahoo pudo redirigir o devolver HTML).")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error al consultar Yahoo Finance: {e}")
        return []

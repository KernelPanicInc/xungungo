import requests
import streamlit as st

nombre = "Stocks Fundamentals"
descripcion = "Este plugin muestra los fundamentales de una acción utilizando yfinance."
tipo = "stock"

def render(ticker):
    import yfinance as yf

    # Descargar datos del ticker
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Título principal
        st.markdown(f"# {info.get('longName', ticker)} ({ticker})")
        st.markdown(
            f"### ${info.get('currentPrice', 'N/A')} "
            f"({info.get('regularMarketChangePercent', 0) * 100:+.2f}%)"
        )

        # Subtítulos de cotización actual
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Precio Anterior", info.get("regularMarketPreviousClose", "N/A"))
        col2.metric("Rango Diario", f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}")
        col3.metric("Rango 52 Semanas", f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}")
        col4.metric("Capitalización de Mercado", f"{info.get('marketCap', 'N/A'):,}")

        # Sección con detalles financieros
        st.markdown("## Detalles Financieros")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                - **Sector:** {info.get('sector', 'N/A')}
                - **Industria:** {info.get('industry', 'N/A')}
                - **PE Ratio (TTM):** {info.get('trailingPE', 'N/A')}
                - **EPS (TTM):** {info.get('trailingEps', 'N/A')}
                """
            )
        with col2:
            st.markdown(
                f"""
                - **Beta:** {info.get('beta', 'N/A')}
                - **Dividendos:** {info.get('dividendYield', 'N/A') * 100:.2f}%
                - **Volumen Promedio:** {info.get('averageVolume', 'N/A'):,}
                - **Empleados:** {info.get('fullTimeEmployees', 'N/A')}
                """
            )

        # Sección con descripción de la empresa
        st.markdown("---")
        st.markdown("### Sobre la Empresa")
        st.markdown(info.get("longBusinessSummary", "Descripción no disponible."))
        website = info.get("website", "N/A")
        if website != "N/A":
            st.markdown(f"[Visitar Sitio Web]({website})")

        # Línea de separación
        st.markdown("---")

    except Exception as e:
        st.error(f"Ocurrió un error al obtener los datos del ticker '{ticker}': {e}")

nombre = "Chart Plugin"
descripcion = "Este plugin grafica los datos históricos de un ticker utilizando Yahoo Finance y Plotly, con opción de elegir el tipo de gráfico."
tipo = "stock"

def render(ticker):
    import streamlit as st
    import yfinance as yf
    import datetime as dt
    import plotly.graph_objects as go
    from utils.flatten_columns import flatten_columns

    # Título del plugin
    st.title(":chart_with_upwards_trend: Stock Price Chart with Plotly")
    st.write(f"Mostrando datos históricos para el ticker: **{ticker}**")

    # Selección del rango de fechas
    st.sidebar.subheader("Parámetros de Gráfica")
    start_date = st.sidebar.date_input("Fecha de inicio", dt.date(2020, 1, 1))
    end_date = st.sidebar.date_input("Fecha de fin", dt.date.today())

    if start_date > end_date:
        st.error("La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    # Selección del tipo de gráfico
    chart_type = st.sidebar.selectbox("Selecciona el tipo de gráfico", ["Candlestick", "Línea"])

    # Selección del intervalo
    interval = st.sidebar.selectbox(
        "Selecciona el intervalo de datos",
        ["1m", "5m", "15m", "1h", "1d", "1wk", "1mo"],
        index=4  # Selecciona "1d" como predeterminado
    )

    # Descargar datos históricos y mostrar spinner
    with st.spinner("Cargando datos y generando gráfico..."):
        try:
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            data = flatten_columns(data)
            
            # Filtrar días sin datos
            data.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
            
            if data.empty:
                st.warning(f"No se encontraron datos para el ticker {ticker} en el rango de fechas e intervalo seleccionados.")
                return

            # Crear el gráfico
            fig = go.Figure()

            if chart_type == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Candlestick'
                ))
            elif chart_type == "Línea":
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name='Precio de Cierre',
                    line=dict(color='blue', width=2)
                ))

            # Configurar el diseño del gráfico
            fig.update_layout(
                title=f"Evolución del Precio de {ticker}",
                xaxis_tickformat = '%d-%m-%Y',  # Formato de fecha más legible
                xaxis=dict(
                    title="Fecha",
                    type='category',  # Evitar días sin datos
                    #tickformat='%d-%m-%Y',  # Formato de fecha más legible
                    tickangle=-45,  # Inclinar etiquetas de fechas
                    tickmode='auto',  # Mostrar etiquetas en intervalos regulares
                ),
                yaxis=dict(title="Precio (USD)", showgrid=True),
                template="plotly_white",
                legend_title="Leyenda",
                hovermode="x unified",
                dragmode="pan",  # Configura el modo inicial en "pan"
                width=1000,
                height=600
            )

            # Mostrar la gráfica en Streamlit con scrollzoom habilitado
            st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
        except Exception as e:
            st.error(f"Ocurrió un error al obtener los datos del ticker '{ticker}' con el intervalo '{interval}': {e}")

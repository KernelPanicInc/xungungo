nombre = "LWCharts Plugin"
descripcion = "Plugin con panel de velas arriba y volumen abajo sin solaparse."
tipo = "stock"

def render(ticker):
    import streamlit as st
    import yfinance as yf
    import pandas as pd
    import datetime as dt
    from streamlit_lightweight_charts import renderLightweightCharts
    from utils.flatten_columns import flatten_columns
    from plugins.stocks.lwcharts.indicators.load_indicators import load_indicators

    st.write(f"Gráfico Candlestick para el ticker: **{ticker}**")
    
    # Parámetros de entrada: rango de fechas e intervalo de tiempo
    default_start = dt.date.today() - dt.timedelta(days=730)
    start_date = st.sidebar.date_input("Fecha de inicio", default_start)
    end_date = st.sidebar.date_input("Fecha de fin", dt.date.today())

    interval_options = [
        "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
        "1d", "5d", "1wk", "1mo", "3mo"
    ]
    interval = st.sidebar.selectbox(
        "Intervalo de Tiempo",
        options=interval_options,
        index=8,  # '1d' por defecto
        help="Selecciona el intervalo de tiempo para los datos históricos."
    )
    
    # Descargar los datos históricos usando yfinance
    with st.spinner("Cargando datos históricos..."):
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        data = flatten_columns(data)
    
    if data.empty:
        st.warning(f"No se encontraron datos para el ticker {ticker} en el rango de fechas seleccionado.")
        return

    data = data.reset_index()
    # Determinar el nombre de la columna de fecha según el intervalo
    time_column = "Datetime" if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"] else "Date"
    data.rename(columns={time_column: "Fecha"}, inplace=True)
    
    # Preparar los datos en el formato candlestick:
    # Cada vela incluye: tiempo (en formato UNIX epoch), apertura, máximo, mínimo y cierre
    candles = []
    for _, row in data.iterrows():
        time_val = int(row["Fecha"].timestamp())
        candles.append({
            "time": time_val,
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"])
        })
    
    # Configuración del gráfico con lightweightcharts
    charts_config = [
        {
            "chart": {
                "height": 600,
                "layout": {
                    "background": {"type": "solid", "color": "#FFFFFF"},
                    "textColor": "black"
                },
                "timeScale": {
                    "timeVisible": True,
                    "secondsVisible": False
                },
                "watermark": {
                    "visible": True,
                    "text": f'{ticker} Candlestick chart from {start_date} to {end_date}',
                    "fontSize": 12,
                    "lineHeight": 50,
                    "color": "rgba(0, 0, 0, 0.5)",
                    "horzAlign": "left",
                    "vertAlign": "top"
                }
            },
            "series": [
                {
                    "type": "Candlestick",
                    "data": candles
                }
            ]
        }
    ]


        # ====== Cargar plugins
    plugins = load_indicators()
    plugin_names = [p.name for p in plugins]

    st.sidebar.subheader("Indicadores Disponibles")
    selected_plugins = st.sidebar.multiselect("Indicadores", plugin_names, default=[])


        # ====== Aplicar plugins
    for plug in plugins:
        if plug.name in selected_plugins:
            user_params = {}
            if hasattr(plug, "get_user_params"):
                user_params = plug.get_user_params(data)

            plug.apply(charts_config, data, user_params)

    
    st.subheader("Gráfico Candlestick")
    renderLightweightCharts(charts_config, key="myCandlestickChart")

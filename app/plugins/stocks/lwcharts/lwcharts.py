nombre = "Charts"
descripcion = "Plugin con panel de velas arriba y volumen abajo sin solaparse."
tipo = "stock"

def render(ticker):
    import streamlit as st
    import yfinance as yf
    import pandas as pd
    import datetime as dt
    from streamlit_lightweight_charts import renderLightweightCharts
    from streamlit_theme import st_theme
    from utils.flatten_columns import flatten_columns
    from plugins.stocks.lwcharts.indicators.load_indicators import load_indicators

    theme = st_theme()
    is_dark = theme.get("base") == "dark"

    bg_color = "#1E1E1E" if is_dark else "#CCCCCC"
    text_color = "white" if is_dark else "black"
    watermark_color = "rgba(255, 255, 255, 0.3)" if is_dark else "rgba(0, 0, 0, 0.5)"
    grid = {
                    "vertLines": { "color": '#444' },
                    "horzLines": { "color": '#444' },
                } if is_dark else {}

    

    st.write(f"Gráfico Candlestick para el ticker: **{ticker}**")
    
    default_start = dt.date.today() - dt.timedelta(days=730)
    start_date = st.sidebar.date_input("Fecha de inicio", default_start)
    end_date = st.sidebar.date_input("Fecha de fin", dt.date.today())
    # Convertir la fecha final a datetime hasta las 23:59 para incluir todo el día
    end_datetime = dt.datetime.combine(end_date, dt.time(23, 59))


    interval_options = [
        "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
        "1d", "5d", "1wk", "1mo", "3mo"
    ]
    interval = st.sidebar.selectbox(
        "Intervalo de Tiempo",
        options=interval_options,
        index=8,
        help="Selecciona el intervalo de tiempo para los datos históricos."
    )

    with st.spinner("Cargando datos históricos..."):
        data = yf.download(ticker, start=start_date, end=end_datetime, interval=interval)
        data = flatten_columns(data)

    if data.empty:
        st.warning(f"No se encontraron datos para el ticker {ticker} en el rango de fechas seleccionado.")
        return

    data = data.reset_index()
    time_column = "Datetime" if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"] else "Date"
    data.rename(columns={time_column: "Fecha"}, inplace=True)

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

    charts_config = [
        {
            "chart": {
                "height": 600,
                "grid" : grid,
                "layout": {
                    "background": {"type": "solid", "color": bg_color},
                    "textColor": text_color
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
                    "color": watermark_color,
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
    plugins = load_indicators()
    plugin_names = [p.name for p in plugins]

    st.sidebar.subheader("Indicadores Disponibles")
    selected_plugins = st.sidebar.multiselect("Indicadores", plugin_names, default=[])

    for plug in plugins:
        if plug.name in selected_plugins:
            user_params = {}
            if hasattr(plug, "get_user_params"):
                user_params = plug.get_user_params(data)
                user_params["is_dark"] = is_dark
            plug.apply(charts_config, data, user_params)

    st.subheader("Gráfico Candlestick")
    renderLightweightCharts(charts_config, key="myCandlestickChart")

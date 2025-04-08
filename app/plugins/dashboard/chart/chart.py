import datetime as dt
import streamlit as st
import yfinance as yf
from utils.flatten_columns import flatten_columns

nombre = "Charts"
descripcion = "Plugin con panel de velas arriba y volumen abajo (opcional) sin solaparse."
tipo = "chart"

# Configuración por defecto del plugin
default_config = {
    "ticker": "AAPL",
    "start_date": (dt.date.today() - dt.timedelta(days=730)).isoformat(),
    "end_date": dt.date.today().isoformat(),
    "interval": "1d",
    "show_volume": True,
    "height": 400  # Altura por defecto del gráfico de velas
}

def config(current_config: dict) -> dict:
    """
    Muestra inputs para configurar el plugin y retorna un diccionario con los valores
    que el usuario haya seleccionado o ingresado.
    """
    # Recuperar valores anteriores o usar los valores por defecto
    ticker_value = current_config.get("ticker", default_config["ticker"])
    period_value = current_config.get("period", "")
    start_value = current_config.get("start_date", default_config["start_date"])
    end_value = current_config.get("end_date", default_config["end_date"])
    interval_value = current_config.get("interval", default_config["interval"])
    show_volume_value = current_config.get("show_volume", default_config["show_volume"])
    height_value = current_config.get("height", default_config["height"])

    st.write("### Configuración Principal")
    ticker = st.text_input("Ticker", value=ticker_value)
    period = st.text_input("Period (opcional)", value=period_value)

    if not period:
        try:
            start_date = st.date_input(
                "Fecha de inicio",
                value=dt.datetime.strptime(start_value, "%Y-%m-%d").date()
            )
        except Exception:
            start_date = st.date_input("Fecha de inicio", value=dt.date.today() - dt.timedelta(days=730))
        
        try:
            end_date = st.date_input(
                "Fecha de fin",
                value=dt.datetime.strptime(end_value, "%Y-%m-%d").date()
            )
        except Exception:
            end_date = st.date_input("Fecha de fin", value=dt.date.today())
    else:
        # Si se define 'period', no se usan start_date y end_date
        start_date = dt.datetime.strptime(start_value, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end_value, "%Y-%m-%d").date()

    interval_options = [
        "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
        "1d", "5d", "1wk", "1mo", "3mo"
    ]
    try:
        index_interval = interval_options.index(interval_value)
    except ValueError:
        index_interval = 8  # "1d"

    interval = st.selectbox(
        "Intervalo",
        options=interval_options,
        index=index_interval,
        help="Selecciona el intervalo de tiempo para los datos históricos."
    )

    st.write("### Opciones de Gráfico")
    show_volume = st.checkbox("Mostrar Volumen", value=show_volume_value, help="Activa o desactiva el gráfico de volumen debajo de las velas.")

    height = st.slider(
        "Altura del gráfico de velas (px)",
        min_value=200,
        max_value=1000,
        value=height_value,
        step=50,
        help="Controla la altura en píxeles del panel de velas."
    )

    # Construir el diccionario final
    new_config = {
        "ticker": ticker,
        "interval": interval,
        "show_volume": show_volume,
        "height": height
    }

    if period:
        new_config["period"] = period
    else:
        new_config["start_date"] = start_date.isoformat()
        new_config["end_date"] = end_date.isoformat()

    return new_config

def render(config: dict):
    """
    Renderiza el gráfico de velas y, opcionalmente, el volumen, usando lightweight-charts.
    Lee la configuración y descarga datos con yfinance.
    """
    from streamlit_lightweight_charts import renderLightweightCharts

    # Extraer parámetros
    ticker = config.get("ticker", default_config["ticker"])
    interval = config.get("interval", default_config["interval"])
    show_volume = config.get("show_volume", default_config["show_volume"])
    height = int(config.get("height", default_config["height"]))-39  # Ajustar altura para evitar scroll

    period_config = config.get("period", None)
    if not period_config:
        try:
            start_date = dt.datetime.strptime(config.get("start_date", default_config["start_date"]), "%Y-%m-%d").date()
        except Exception:
            start_date = dt.date.today() - dt.timedelta(days=730)
        try:
            end_date = dt.datetime.strptime(config.get("end_date", default_config["end_date"]), "%Y-%m-%d").date()
        except Exception:
            end_date = dt.date.today()
        end_datetime = dt.datetime.combine(end_date, dt.time(23, 59))
    
    # Se asume que hay una prop "is_dark" para ajuste de colores (si no existe, se usa False)
    is_dark = config.get("is_dark", False)
    bg_color = "#1E1E1E" if is_dark else "#CCCCCC"
    text_color = "white" if is_dark else "black"
    watermark_color = "rgba(255, 255, 255, 0.3)" if is_dark else "rgba(0, 0, 0, 0.5)"
    grid = {
        "vertLines": {"color": '#444'},
        "horzLines": {"color": '#444'},
    } if is_dark else {}

    with st.spinner("Cargando datos históricos..."):
        if period_config:
            data = yf.download(ticker, period=period_config, interval=interval)
        else:
            data = yf.download(ticker, start=start_date, end=end_datetime, interval=interval)
        data = flatten_columns(data)

    if data.empty:
        st.warning(f"No se encontraron datos para el ticker {ticker} en el rango seleccionado.")
        return

    data = data.reset_index()
    # Determinar la columna de tiempo: "Datetime" o "Date"
    time_column = "Datetime" if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"] else "Date"
    data.rename(columns={time_column: "Fecha"}, inplace=True)

    # Velas
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

    # Volumen
    volumes = []
    for _, row in data.iterrows():
        time_val = int(row["Fecha"].timestamp())
        volumes.append({
            "time": time_val,
            "value": int(row["Volume"])
        })

    # Panel superior: gráfico de velas
    chart_candles = {
        "chart": {
            "height": height,  # Usar "height" de la configuración
            "grid": grid,
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
                "text": (f'{ticker} Candlestick '
                         f'{"from " + str(start_date) + " to " + str(end_date) if not period_config else "period " + period_config}'),
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

    charts_config = [chart_candles]

    # Panel inferior: gráfico de volumen (opcional)
    if show_volume:
        chart_volume = {
            "chart": {
                "height": 200,
                "grid": grid,
                "layout": {
                    "background": {"type": "solid", "color": bg_color},
                    "textColor": text_color
                },
                "timeScale": {
                    "timeVisible": True,
                    "secondsVisible": False
                },
                "watermark": {
                    "visible": False
                }
            },
            "series": [
                {
                    "type": "Histogram",
                    "data": volumes,
                    "color": "#26a69a"
                }
            ]
        }
        charts_config.append(chart_volume)

    from streamlit_lightweight_charts import renderLightweightCharts
    renderLightweightCharts(charts_config)

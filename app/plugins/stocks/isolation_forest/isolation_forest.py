nombre = "Isolation Forest Plugin"
descripcion = "Este plugin utiliza Isolation Forest para detectar anomalías en los datos históricos de un ticker."
tipo = "stock"

def render(ticker):
    import streamlit as st
    import yfinance as yf
    import pandas as pd
    import datetime as dt
    from sklearn.ensemble import IsolationForest
    from streamlit_theme import st_theme


    from utils.flatten_columns import flatten_columns
    from streamlit_lightweight_charts import renderLightweightCharts

    # Título del plugin
    st.write(f"Detectando anomalías en los datos históricos del ticker: **{ticker}**")

    theme = st_theme()
    
    # Lista completa de intervalos
    interval_options = [
        "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
        "1d", "5d", "1wk", "1mo", "3mo"
    ]

    st.sidebar.subheader("Parámetros de Análisis")
    
        # Fecha de inicio por defecto = 60 días antes (para no chocar con intradía por defecto)
    default_start = dt.date.today() - dt.timedelta(days=60)
    start_date = st.sidebar.date_input("Fecha de inicio", default_start)
    # Fecha de fin por defecto = hoy
    end_date = st.sidebar.date_input("Fecha de fin", dt.date.today())


    # Selección del intervalo
    interval = st.sidebar.selectbox(
        "Intervalo de Tiempo",
        options=interval_options,
        index=7,  # Por ejemplo, "1h" como predeterminado
        help="Selecciona el intervalo de tiempo para los datos históricos."
    )

    # Ajuste del rango de fechas para intervalos intradía
    today = dt.date.today()
    if interval == "1m":
        max_days = 7
    elif interval in ["2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
        max_days = 59
    else:
        max_days = 36500  # Sin límite práctico para >= 1d

    min_allowed_date = today - dt.timedelta(days=max_days)
    if start_date < min_allowed_date:
        st.warning(
            f"Para el intervalo '{interval}', solo se permiten como máximo {max_days} días hacia atrás. "
            f"Ajustando fecha de inicio a {min_allowed_date}."
        )
        start_date = min_allowed_date

    # Convertir las fechas a datetime
    start_datetime = dt.datetime.combine(start_date, dt.time.min)
    end_datetime = dt.datetime.combine(end_date, dt.time(23, 59))

    # Parámetros de Isolation Forest
    contamination = st.sidebar.slider(
        "Nivel de Contaminación (proporción de anomalías)",
        min_value=0.01, max_value=0.5, value=0.05, step=0.01
    )
    n_estimators = st.sidebar.slider(
        "Número de Estimadores",
        min_value=50, max_value=500, value=100, step=50
    )

    if start_datetime > end_datetime:
        st.error("La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    # Descargar datos y procesar anomalías
    with st.spinner("Cargando datos históricos y detectando anomalías..."):
        try:
            data = yf.download(ticker, start=start_datetime, end=end_datetime, interval=interval)
            data = flatten_columns(data)
            if data.empty:
                st.warning(f"No se encontraron datos para el ticker {ticker} en el rango de fechas seleccionado.")
                return

            # Dado que para intervalos < 1d, la columna de tiempo se llama "Datetime" en yfinance
            time_column = "Datetime" if interval in ["1m","2m","5m","15m","30m","60m","90m","1h"] else "Date"
            data = data.reset_index()
            data.rename(columns={time_column: "Fecha"}, inplace=True)

            # Seleccionamos solo la columna 'Close'
            df = data[['Fecha', 'Close']].copy()

            # Normalización para Isolation Forest
            df['Close_Normalized'] = (df['Close'] - df['Close'].mean()) / df['Close'].std()

            # Entrenar el modelo
            model = IsolationForest(
                n_estimators=n_estimators,
                contamination=contamination,
                random_state=42
            )
            df['Anomaly_Score'] = model.fit_predict(df[['Close_Normalized']])
            df['Anomaly'] = df['Anomaly_Score'].apply(lambda x: 'Normal' if x == 1 else 'Anomalía')

            # Preparamos los datos de la serie (Line) para streamlit-lightweight-charts
            # Usamos 'time' en formato UNIX epoch o "YYYY-MM-DD HH:MM"
            line_series_data = []
            for _, row in df.iterrows():
                # Para intradía -> mejor "YYYY-MM-DD HH:MM"
                time_str = int(row["Fecha"].timestamp())
                line_series_data.append({
                    "time": time_str,
                    "value": float(row["Close"]),
                })

            # Preparamos los marcadores para las anomalías
            markers_data = []
            anomaly_rows = df[df['Anomaly'] == 'Anomalía']
            for _, row in anomaly_rows.iterrows():
                time_str = int(row["Fecha"].timestamp())
                markers_data.append({
                    "time": time_str,
                    "position": "inBar",
                    "color": "rgba(255, 0, 0, 0.6)",
                    "shape": "circle"
                })

            # Configuración general del gráfico y la serie (un solo "chart")
            charts_config = [
                {
                    "chart": {
#                        "width": 800,
                        "height": 500,
                        "layout": {
                            "background": {
                                "type": "solid",
                                "color": "#FFFFFF",
                            },
                            "textColor": "black",
                        },
                        "timeScale": {
                            "timeVisible": True,
                            "secondsVisible": False
                        },
                        "watermark": {
                            "visible": True,
                            "text": f'{ticker} Isolation Forest {interval} from {start_datetime} to {end_datetime}',        # Texto del título estático
                            "fontSize": 12,                     # Tamaño de fuente del título
                            "lineHeight" : 50,                  # Altura de la línea del título
                            "color": "rgba(0, 0, 0, 0.5)",       # Color negro semitransparente (50% opacidad)
                            "horzAlign": "left",              # Centrado horizontal
                            "vertAlign": "top"                  # Alineado a la parte superior
                        }
                    },
                    "series": [
                        {
                            "type": "Line",
                            "data": line_series_data,
                            "markers": markers_data,  # anotaciones de anomalías
                            "options": {
                                "lineWidth": 2,
                                "color": "blue"
                            }
                        }
                    ]
                }
            ]

            if theme["base"] == "dark":
                charts_config[0]["chart"]["layout"]["background"]["color"] = "#1c1c1c"
                charts_config[0]["chart"]["layout"]["textColor"] = "white"
                charts_config[0]["chart"]["watermark"]["color"] = "#CCC"
                charts_config[0]["chart"]["grid"] = {
                    "vertLines": { "color": '#444' },
                    "horzLines": { "color": '#444' },
                }
                charts_config[0]["series"][0]["options"]["color"] = "#2962FF"

            st.subheader("Gráfico de Precios y Anomalías")
            renderLightweightCharts(charts_config, key="myAnomalyChart")

            # ----- TABLA DE ANOMALÍAS -----
            st.subheader("Anomalías Detectadas")
            anomalies = df[df['Anomaly'] == 'Anomalía']
            st.write(f"Se detectaron **{len(anomalies)} anomalías** en los datos históricos.")
            st.dataframe(anomalies[['Fecha', 'Close']])

        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos para el ticker '{ticker}': {e}")

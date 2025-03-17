nombre = "Isolation Forest Plugin"
descripcion = "Este plugin utiliza Isolation Forest para detectar anomalías en los datos históricos de un ticker, permitiendo analizar Cierre, Cierre y Volumen, OHLCV, o Volatilidad y Volumen."
tipo = "stock"

def render(ticker):
    import streamlit as st
    import yfinance as yf
    import pandas as pd
    import datetime as dt
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from streamlit_theme import st_theme
    from utils.flatten_columns import flatten_columns
    from streamlit_lightweight_charts import renderLightweightCharts

    st.write(f"Detectando anomalías en los datos históricos del ticker: **{ticker}**")
    theme = st_theme()

    # Lista de intervalos disponibles
    interval_options = [
        "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
        "1d", "5d", "1wk", "1mo", "3mo"
    ]

    st.sidebar.subheader("Parámetros de Análisis")
    default_start = dt.date.today() - dt.timedelta(days=60)
    start_date = st.sidebar.date_input("Fecha de inicio", default_start)
    end_date = st.sidebar.date_input("Fecha de fin", dt.date.today())

    interval = st.sidebar.selectbox(
        "Intervalo de Tiempo",
        options=interval_options,
        index=7,
        help="Selecciona el intervalo de tiempo para los datos históricos."
    )

    # Selección de métrico de análisis
    analysis_metric = st.sidebar.selectbox(
        "Métrico de análisis",
        options=["Cierre", "Cierre y Volumen", "OHLCV", "Volatilidad y Volumen"],
        help="Selecciona el tipo de análisis a realizar."
    )

    # Opción para visualizar gradiente de anomalía en todos los puntos
    show_gradient = st.sidebar.checkbox("Mostrar gradiente en todos los puntos", value=False)

    # Manejo del slider de contaminación: si el gradiente está activo se bloquea en 0.05
    if not show_gradient:
        contamination = st.sidebar.slider(
            "Nivel de Contaminación (proporción de anomalías)",
            min_value=0.01, max_value=0.5, value=0.05, step=0.01
        )
    else:
        st.sidebar.write("Nivel de Contaminación: Bloqueado en 0.05")
        contamination = 0.05

    n_estimators = st.sidebar.slider(
        "Número de Estimadores",
        min_value=50, max_value=500, value=100, step=50
    )

    # Ajuste del rango de fechas para intervalos intradía
    today = dt.date.today()
    if interval == "1m":
        max_days = 7
    elif interval in ["2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
        max_days = 59
    else:
        max_days = 36500

    min_allowed_date = today - dt.timedelta(days=max_days)
    if start_date < min_allowed_date:
        st.warning(
            f"Para el intervalo '{interval}', solo se permiten como máximo {max_days} días hacia atrás. "
            f"Ajustando fecha de inicio a {min_allowed_date}."
        )
        start_date = min_allowed_date

    start_datetime = dt.datetime.combine(start_date, dt.time.min)
    end_datetime = dt.datetime.combine(end_date, dt.time(23, 59))

    def download_data(ticker, start_dt, end_dt, interval):
        data = yf.download(ticker, start=start_dt, end=end_dt, interval=interval)
        data = flatten_columns(data)
        if data.empty:
            st.warning(f"No se encontraron datos para el ticker {ticker} en el rango de fechas seleccionado.")
            return None
        # Para intervalos intradía, la columna se llama "Datetime", de lo contrario "Date"
        time_column = "Datetime" if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"] else "Date"
        data = data.reset_index()
        data.rename(columns={time_column: "Fecha"}, inplace=True)
        return data

    def detect_anomalies(df, metric, n_estimators, contamination):
        df_processed = df.copy()
        if metric == "Cierre":
            df_processed['Close_Normalized'] = (df_processed['Close'] - df_processed['Close'].mean()) / df_processed['Close'].std()
            features = df_processed[['Close_Normalized']]
        elif metric == "Cierre y Volumen":
            df_processed['Close_Normalized'] = (df_processed['Close'] - df_processed['Close'].mean()) / df_processed['Close'].std()
            if "Volume" in df_processed.columns:
                df_processed['Volume_Normalized'] = (df_processed['Volume'] - df_processed['Volume'].mean()) / df_processed['Volume'].std()
                features = df_processed[['Close_Normalized', 'Volume_Normalized']]
            else:
                st.error("Datos de volumen no disponibles para el análisis combinado. Se procederá solo con el precio.")
                features = df_processed[['Close_Normalized']]
        elif metric == "OHLCV":
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                if col in df_processed.columns:
                    df_processed[f"{col}_Normalized"] = (df_processed[col] - df_processed[col].mean()) / df_processed[col].std()
                else:
                    st.error(f"Datos de {col} no disponibles y se omitirán en el análisis.")
            feature_columns = [f"{col}_Normalized" for col in ["Open", "High", "Low", "Close", "Volume"] if f"{col}_Normalized" in df_processed.columns]
            if len(feature_columns) == 0:
                st.error("No se encontraron columnas suficientes para el análisis OHLCV. Se procederá con 'Cierre'.")
                features = df_processed[['Close_Normalized']]
            else:
                features = df_processed[feature_columns]
        elif metric == "Volatilidad y Volumen":
            if all(col in df_processed.columns for col in ["High", "Low", "Volume"]):
                df_processed["Volatilidad"] = df_processed["High"] - df_processed["Low"]
                df_processed["Volume_Log"] = np.log(df_processed["Volume"] + 1)
                # Normalización z-score para volatilidad y volumen
                vol_mean = df_processed["Volatilidad"].mean()
                vol_std = df_processed["Volatilidad"].std()
                vol_norm = (df_processed["Volatilidad"] - vol_mean) / vol_std if vol_std != 0 else 0
                vol_log_mean = df_processed["Volume_Log"].mean()
                vol_log_std = df_processed["Volume_Log"].std()
                vol_log_norm = (df_processed["Volume_Log"] - vol_log_mean) / vol_log_std if vol_log_std != 0 else 0
                df_processed["Volatilidad_Normalized"] = vol_norm
                df_processed["Volume_Normalized"] = vol_log_norm
                features = df_processed[["Volatilidad_Normalized", "Volume_Normalized"]]
            else:
                st.error("Datos de High, Low o Volume no disponibles para el análisis de Volatilidad y Volumen. Se procederá con 'Cierre'.")
                df_processed['Close_Normalized'] = (df_processed['Close'] - df_processed['Close'].mean()) / df_processed['Close'].std()
                features = df_processed[['Close_Normalized']]
        else:
            features = df_processed[['Close']]

        model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42
        )
        model.fit(features)
        df_processed['Prediccion'] = model.predict(features)
        df_processed['Anomaly'] = df_processed['Prediccion'].apply(lambda x: 'Normal' if x == 1 else 'Anomalía')
        raw_scores = model.decision_function(features)
        anomaly_scores = -raw_scores  # Mayor valor indica mayor anomalía
        min_score = anomaly_scores.min()
        max_score = anomaly_scores.max()
        norm_scores = (anomaly_scores - min_score) / (max_score - min_score) if max_score != min_score else anomaly_scores * 0
        df_processed['norm_score'] = norm_scores
        return df_processed

    with st.spinner("Cargando datos históricos y detectando anomalías..."):
        try:
            data = download_data(ticker, start_datetime, end_datetime, interval)
            if data is None:
                return

            # Seleccionar columnas según la métrica elegida
            if analysis_metric == "OHLCV":
                columns_to_select = ['Fecha', 'Open', 'High', 'Low', 'Close', 'Volume']
            elif analysis_metric == "Cierre y Volumen":
                columns_to_select = ['Fecha', 'Close', 'Volume']
            elif analysis_metric == "Volatilidad y Volumen":
                # Se requieren High, Low y Volume; se incluye Close para el gráfico
                columns_to_select = ['Fecha', 'High', 'Low', 'Close', 'Volume']
            else:  # "Cierre"
                columns_to_select = ['Fecha', 'Close']

            df = data[columns_to_select].copy()

            # Filtrar filas con Volume igual a 0 si el análisis incluye volumen
            if analysis_metric in ["Cierre y Volumen", "OHLCV", "Volatilidad y Volumen"]:
                df = df[df["Volume"] != 0]

            df = detect_anomalies(df, analysis_metric, n_estimators, contamination)

            # Configurar datos para el gráfico según la métrica:
            if analysis_metric == "OHLCV":
                ohlc_data = []
                for _, row in df.iterrows():
                    ohlc_data.append({
                        "time": int(row["Fecha"].timestamp()),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"])
                    })
                series_type = "Candlestick"
            else:
                ohlc_data = []
                for _, row in df.iterrows():
                    ohlc_data.append({
                        "time": int(row["Fecha"].timestamp()),
                        "value": float(row["Close"])
                    })
                series_type = "Line"

            # Definir la posición de los marcadores:
            marker_position = "aboveBar" if analysis_metric == "OHLCV" else "inBar"

            # Configurar marcadores
            markers_data = []
            if show_gradient:
                for _, row in df.iterrows():
                    s = row["norm_score"]  # Valor entre 0 y 1
                    red = int(255 * s)
                    blue = int(255 * (1 - s))
                    alpha = 0.2 + 0.8 * s  # Menos transparencia para valores anómalos
                    color = f"rgba({red}, 0, {blue}, {alpha:.2f})"
                    markers_data.append({
                        "time": int(row["Fecha"].timestamp()),
                        "position": marker_position,
                        "color": color,
                        "shape": "circle"
                    })
            else:
                anomaly_rows = df[df['Anomaly'] == 'Anomalía']
                for _, row in anomaly_rows.iterrows():
                    markers_data.append({
                        "time": int(row["Fecha"].timestamp()),
                        "position": marker_position,
                        "color": "rgba(255, 0, 0, 0.6)",
                        "shape": "circle"
                    })

            charts_config = [{
                "chart": {
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
                        "text": f'{ticker} Isolation Forest ({analysis_metric}) {interval} from {start_datetime} to {end_datetime}',
                        "fontSize": 12,
                        "lineHeight": 50,
                        "color": "rgba(0, 0, 0, 0.5)",
                        "horzAlign": "left",
                        "vertAlign": "top"
                    }
                },
                "series": [{
                    "type": series_type,
                    "data": ohlc_data,
                    "markers": markers_data,
                    "options": {
                        "lineWidth": 2,
                        "color": "blue"
                    }
                }]
            }]

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

            st.subheader("Análisis de Anomalías")
            if analysis_metric == "OHLCV":
                st.dataframe(df[['Fecha', 'Open', 'High', 'Low', 'Close', 'Volume', 'norm_score']])
            elif analysis_metric == "Cierre y Volumen":
                st.dataframe(df[['Fecha', 'Close', 'Volume', 'norm_score']])
            elif analysis_metric == "Volatilidad y Volumen":
                st.dataframe(df[['Fecha', 'High', 'Low', 'Close', 'Volume', 'Volatilidad', 'Volatilidad_Normalized', 'Volume_Normalized', 'norm_score']])
            else:
                st.dataframe(df[['Fecha', 'Close', 'norm_score']])
        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos para el ticker '{ticker}': {e}")

nombre = "Isolation Forest Plugin"
descripcion = "Este plugin utiliza Isolation Forest para detectar anomalías en los datos históricos de un ticker."
tipo = "stock"

def render(ticker):
    import streamlit as st
    import yfinance as yf
    import pandas as pd
    import datetime as dt
    import plotly.express as px
    from sklearn.ensemble import IsolationForest
    from utils.flatten_columns import flatten_columns

    # Título del plugin
    st.title(":mag: Anomaly Detection with Isolation Forest")
    st.write(f"Detectando anomalías en los datos históricos del ticker: **{ticker}**")

    # Selección del rango de fechas
    st.sidebar.subheader("Parámetros de Análisis")
    start_date = st.sidebar.date_input("Fecha de inicio", dt.date(2020, 1, 1))
    end_date = st.sidebar.date_input("Fecha de fin", dt.date.today())

    # Convertir las fechas seleccionadas a datetime: inicio a las 00:00 y fin a las 23:59
    start_datetime = dt.datetime.combine(start_date, dt.time.min)
    end_datetime = dt.datetime.combine(end_date, dt.time(23, 59))

    interval = st.sidebar.selectbox(
        "Intervalo de Tiempo",
        options=["1d", "1wk", "1mo", "15m"],
        index=0,
        help="Selecciona el intervalo de tiempo para los datos históricos (diario, semanal, mensual o intradía)."
    )

    # Parámetros de Isolation Forest
    contamination = st.sidebar.slider("Nivel de Contaminación (proporción de anomalías)", min_value=0.01, max_value=0.5, value=0.05, step=0.01)
    n_estimators = st.sidebar.slider("Número de Estimadores", min_value=50, max_value=500, value=100, step=50)

    if start_datetime > end_datetime:
        st.error("La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    # Descargar datos históricos y procesar anomalías
    with st.spinner("Cargando datos históricos y detectando anomalías..."):
        try:
            # Descargar datos con el intervalo seleccionado usando los datetime convertidos
            data = yf.download(ticker, start=start_datetime, end=end_datetime, interval=interval)
            data = flatten_columns(data)
            if data.empty:
                st.warning(f"No se encontraron datos para el ticker {ticker} en el rango de fechas seleccionado.")
                return

            # Manejo dinámico de la columna de tiempo
            time_column = "Datetime" if interval in ["15m"] else "Date"
            data = data.reset_index()  # Asegurarnos de que la columna de tiempo sea accesible
            data.rename(columns={time_column: "Fecha"}, inplace=True)

            # Seleccionar solo la columna de precios de cierre y crear una copia
            df = data[['Fecha', 'Close']].copy()
            df.loc[:, 'Close_Normalized'] = (df['Close'] - df['Close'].mean()) / df['Close'].std()

            # Aplicar Isolation Forest y asignar la predicción
            model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=42)
            df.loc[:, 'Anomaly_Score'] = model.fit_predict(df[['Close_Normalized']])

            # Etiquetar anomalías usando .loc
            df.loc[:, 'Anomaly'] = df['Anomaly_Score'].apply(lambda x: 'Normal' if x == 1 else 'Anomalía')

            # Graficar resultados
            st.subheader("Gráfico de Precios y Anomalías")
            fig = px.scatter(
                df,
                x='Fecha',
                y='Close',
                color='Anomaly',
                color_discrete_map={'Normal': 'blue', 'Anomalía': 'red'},
                title=f"Detección de Anomalías para {ticker}",
                labels={'Close': 'Precio (USD)', 'Fecha': 'Fecha'},
                template="plotly_white",
                height=600,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Mostrar tabla con anomalías detectadas
            st.subheader("Anomalías Detectadas")
            anomalies = df[df['Anomaly'] == 'Anomalía']
            st.write(f"Se detectaron **{len(anomalies)} anomalías** en los datos históricos.")
            st.dataframe(anomalies[['Fecha', 'Close']])

        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos para el ticker '{ticker}': {e}")

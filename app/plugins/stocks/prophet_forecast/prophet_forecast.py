nombre = "Forecast Plugin"
descripcion = "Este plugin genera un pronóstico utilizando Prophet y muestra gráficos de estacionalidad."
tipo = "stock"

def render(ticker):
    import streamlit as st
    import yfinance as yf
    from prophet import Prophet
    from prophet.plot import plot_components_plotly
    import pandas as pd
    import datetime as dt
    import plotly.graph_objects as go
    from utils.flatten_columns import flatten_columns

    # Título del plugin
    st.title(":crystal_ball: Stock Price Forecast with Prophet")
    st.write(f"Generando un pronóstico para el ticker: **{ticker}**")

    # Selección del rango de fechas para datos históricos
    st.sidebar.subheader("Parámetros de Forecast")
    start_date = st.sidebar.date_input("Fecha de inicio", dt.date(2020, 1, 1))
    end_date = st.sidebar.date_input("Fecha de fin", dt.date.today())
    forecast_period = st.sidebar.number_input("Horizonte de pronóstico (días)", min_value=1, max_value=365, value=30)

    if start_date > end_date:
        st.error("La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    # Descargar datos históricos
    with st.spinner("Cargando datos históricos y generando pronóstico..."):
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            data = flatten_columns(data)
            if data.empty:
                st.warning(f"No se encontraron datos para el ticker {ticker} en el rango de fechas seleccionado.")
                return

            # Preparar datos para Prophet
            df = data[['Close']].reset_index()
            df = df.rename(columns={'Date': 'ds', 'Close': 'y'})

            # Configurar y entrenar el modelo de Prophet
            model = Prophet(daily_seasonality=True)
            model.fit(df)

            # Generar el futuro horizonte
            future = model.make_future_dataframe(periods=forecast_period)
            forecast = model.predict(future)

            # Crear gráfico interactivo con datos históricos y pronóstico
            fig = go.Figure()

            # Datos históricos
            fig.add_trace(go.Scatter(
                x=df['ds'], y=df['y'], mode='lines', name='Datos Históricos',
                line=dict(color='blue', width=2)
            ))

            # Pronóstico
            fig.add_trace(go.Scatter(
                x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Pronóstico',
                line=dict(color='green', width=2)
            ))

            # Bandas de incertidumbre
            fig.add_trace(go.Scatter(
                x=forecast['ds'], y=forecast['yhat_upper'], mode='lines',
                name='Banda Superior', line=dict(width=0), showlegend=False,
                fillcolor='rgba(0, 255, 0, 0.2)', fill='tonexty'
            ))
            fig.add_trace(go.Scatter(
                x=forecast['ds'], y=forecast['yhat_lower'], mode='lines',
                name='Banda Inferior', line=dict(width=0), showlegend=False,
                fillcolor='rgba(0, 255, 0, 0.2)', fill='tonexty'
            ))

            # Configurar el diseño del gráfico
            fig.update_layout(
                title=f"Pronóstico de Precios para {ticker}",
                xaxis_title="Fecha",
                yaxis_title="Precio (USD)",
                template="plotly_white",
                hovermode="x unified",
                width=1000,
                height=600
            )

            # Mostrar la gráfica en Streamlit
            st.plotly_chart(fig, use_container_width=True)

            # Mostrar tabla de pronóstico
            st.subheader("Datos del Pronóstico")
            st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(10))

            # Gráficos de estacionalidad
            st.subheader("Gráficos de Estacionalidad")
            seasonality_fig = plot_components_plotly(model, forecast)
            st.plotly_chart(seasonality_fig, use_container_width=True)

        except Exception as e:
            st.error(f"Ocurrió un error al generar el pronóstico para el ticker '{ticker}': {e}")

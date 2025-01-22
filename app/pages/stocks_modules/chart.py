import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from utils.flatten_columns import flatten_columns
import pandas as pd

def calculate_td_sequential(data):
    """
    Calcula el indicador TD Sequential para un DataFrame.
    
    Args:
        data (pd.DataFrame): DataFrame con datos históricos que contienen la columna 'Close'.
    
    Returns:
        pd.DataFrame: DataFrame con columnas adicionales 'TD_Buy_Setup', 'TD_Sell_Setup', 'TD_Buy_Countdown', 'TD_Sell_Countdown'.
    """
    # Inicializar columnas para el TD Sequential
    data['TD_Buy_Setup'] = 0
    data['TD_Sell_Setup'] = 0
    data['TD_Buy_Countdown'] = 0
    data['TD_Sell_Countdown'] = 0

    # Iterar sobre los datos para calcular el TD Sequential
    for i in range(4, len(data)):
        # TD Buy Setup: Close[i] < Close[i-4]
        if data.loc[data.index[i], 'Close'] < data.loc[data.index[i-4], 'Close']:
            data.loc[data.index[i], 'TD_Buy_Setup'] = data.loc[data.index[i-1], 'TD_Buy_Setup'] + 1 if data.loc[data.index[i-1], 'TD_Buy_Setup'] >= 0 else 1
            if data.loc[data.index[i], 'TD_Buy_Setup'] > 9:
                data.loc[data.index[i], 'TD_Buy_Setup'] = 9
        else:
            data.loc[data.index[i], 'TD_Buy_Setup'] = 0

        # TD Sell Setup: Close[i] > Close[i-4]
        if data.loc[data.index[i], 'Close'] > data.loc[data.index[i-4], 'Close']:
            data.loc[data.index[i], 'TD_Sell_Setup'] = data.loc[data.index[i-1], 'TD_Sell_Setup'] + 1 if data.loc[data.index[i-1], 'TD_Sell_Setup'] >= 0 else 1
            if data.loc[data.index[i], 'TD_Sell_Setup'] > 9:
                data.loc[data.index[i], 'TD_Sell_Setup'] = 9
        else:
            data.loc[data.index[i], 'TD_Sell_Setup'] = 0

    # Calcular TD Countdown
    for i in range(1, len(data)):
        # TD Buy Countdown: Close[i] < Low[i-2] y Buy Setup en progreso
        if data.loc[data.index[i], 'TD_Buy_Setup'] == 9:
            countdown = 0
            for j in range(i + 1, len(data)):
                if data.loc[data.index[j], 'Close'] < data.loc[data.index[j-2], 'Low']:
                    countdown += 1
                    data.loc[data.index[j], 'TD_Buy_Countdown'] = countdown
                    if countdown == 13:
                        break
                else:
                    countdown = 0

        # TD Sell Countdown: Close[i] > High[i-2] y Sell Setup en progreso
        if data.loc[data.index[i], 'TD_Sell_Setup'] == 9:
            countdown = 0
            for j in range(i + 1, len(data)):
                if data.loc[data.index[j], 'Close'] > data.loc[data.index[j-2], 'High']:
                    countdown += 1
                    data.loc[data.index[j], 'TD_Sell_Countdown'] = countdown
                    if countdown == 13:
                        break
                else:
                    countdown = 0

    return data

def render(ticker):
    """Renderiza un gráfico de velas para el ticker seleccionado utilizando datos reales de yfinance."""

    # Selección de rango de fechas
    st.sidebar.write("### Selección de rango de fechas")
    start_date = st.sidebar.date_input("Fecha de inicio", value=pd.Timestamp.now() - pd.Timedelta(days=200))
    end_date = st.sidebar.date_input("Fecha de fin", value=pd.Timestamp.now())
    
    # Validación de rango de fechas
    if start_date > end_date:
        st.error("La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    # Checkbox para mostrar/ocultar EMA 200
    show_ema_200 = st.sidebar.checkbox("Mostrar EMA 200", value=True)
    show_td_sequential = st.sidebar.checkbox("Mostrar TD Sequential", value=True)

    try:
        # Descargar datos históricos del ticker para el rango seleccionado
        data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
        data = flatten_columns(data)

        if data.empty:
            st.warning(f"No se encontraron datos para el ticker: {ticker} en el rango seleccionado.")
            return

        # Calcular EMA 200
        data['EMA_200'] = data['Close'].ewm(span=200, adjust=False).mean()

        # Calcular TD Sequential y Countdown
        data = calculate_td_sequential(data)

        # Crear el gráfico de velas
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker
        ))

        # Agregar la EMA 200 al gráfico si el usuario la habilita
        if show_ema_200:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['EMA_200'],
                mode="lines",
                line=dict(color="orange", width=2),
                name="EMA 200"
            ))

        # Agregar TD Sequential y Countdown al gráfico si el usuario lo habilita
        if show_td_sequential:
            for i in range(len(data)):
                # Mostrar números del TD Buy Setup
                if data.loc[data.index[i], 'TD_Buy_Setup'] == 9:
                    fig.add_annotation(
                        x=data.index[i],
                        y=data.loc[data.index[i], 'Low'],
                        text="9",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowcolor="darkgreen",
                        font=dict(color="green", size=14, weight="bold"),
                        align="center"
                    )
                # Mostrar números del TD Sell Setup
                if data.loc[data.index[i], 'TD_Sell_Setup'] == 9:
                    fig.add_annotation(
                        x=data.index[i],
                        y=data.loc[data.index[i], 'High'],
                        text="9",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowcolor="darkred",
                        font=dict(color="red", size=14, weight="bold"),
                        align="center"
                    )
                # Mostrar números del TD Buy Countdown
                if data.loc[data.index[i], 'TD_Buy_Countdown'] == 13:
                    fig.add_annotation(
                        x=data.index[i],
                        y=data.loc[data.index[i], 'Low'] - (data.loc[data.index[i], 'Low'] * 0.01),
                        text="13",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowcolor="green",
                        font=dict(color="darkgreen", size=14, weight="bold"),
                        align="center"
                    )
                # Mostrar números del TD Sell Countdown
                if data.loc[data.index[i], 'TD_Sell_Countdown'] == 13:
                    fig.add_annotation(
                        x=data.index[i],
                        y=data.loc[data.index[i], 'High'] + (data.loc[data.index[i], 'High'] * 0.01),
                        text="13",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowcolor="red",
                        font=dict(color="darkred", size=14, weight="bold"),
                        align="center"
                    )

        fig.update_layout(
            title=f"Gráfico de velas - {ticker}",
            xaxis_title="Fecha",
            yaxis_title="Precio",
            xaxis_rangeslider_visible=False
        )
        # Mostrar el gráfico
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error al cargar o procesar datos para {ticker}: {str(e)}")

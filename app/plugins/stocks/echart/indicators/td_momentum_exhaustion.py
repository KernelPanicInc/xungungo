name = "TD Momentum Exhaustion"
plugin_type = "overlay"

def get_user_params(df=None):
    import streamlit as st

    with st.sidebar.expander("Parámetros TDMX (Simplificado)", expanded=False):
        
        # -- Parámetros para el conteo DeMark (Setup)
        st.write("### Configuración de TD Setup")
        setup_lookback = st.number_input("Lookback para TD Setup (N-4)", 1, 10, 4)
        consecutive_needed = st.number_input("Consecutivas para 'Setup' (ej. 9)", 2, 15, 9)

        st.write("---")
        st.write("### Configuración de RSI")
        rsi_period = st.number_input("Periodo RSI", 2, 50, 14)
        rsi_overbought = st.number_input("Umbral Sobrecompra (RSI)", 50, 99, 70)
        rsi_oversold = st.number_input("Umbral Sobreventa (RSI)", 1, 50, 30)

        st.write("---")
        st.write("### Configuración de Volumen")
        vol_ma_period = st.number_input("Periodo Media Volumen", 2, 100, 20)
        vol_spike_factor = st.number_input("Factor de pico de Volumen", 1.0, 5.0, 1.5)

        st.write("---")
        st.write("### Opciones de visualización")
        signal_color_buy = st.color_picker("Color señal de Compra", "#00FF00")
        signal_color_sell = st.color_picker("Color señal de Venta", "#FF0000")
        alpha_signals = st.slider("Opacidad para Señales", 0.0, 1.0, 1.0)

    return {
        "setup_lookback": setup_lookback,
        "consecutive_needed": consecutive_needed,
        "rsi_period": rsi_period,
        "rsi_overbought": rsi_overbought,
        "rsi_oversold": rsi_oversold,
        "vol_ma_period": vol_ma_period,
        "vol_spike_factor": vol_spike_factor,
        "signal_color_buy": signal_color_buy,
        "signal_color_sell": signal_color_sell,
        "alpha_signals": alpha_signals
    }


def apply_overlay(kline_obj, data, dates, user_params):
    """
    Indicador 'TDMX' (versión muy simplificada) que:
      1) Identifica un 'Setup' estilo DeMark al llegar a X velas consecutivas alcistas/bajistas.
      2) Chequea RSI para ver si está en sobrecompra/sobreventa.
      3) Verifica si hay un pico de volumen en esa vela.
      4) Dibuja una marca (scatter) encima de la vela cuando hay posible señal de agotamiento.
    """

    print("Aplicando TDMX overlay...")

    import pandas as pd
    from pyecharts.charts import Scatter
    from pyecharts import options as opts
    import numpy as np

    # ---------------------------
    # 1. Extraer parámetros
    # ---------------------------
    setup_lookback = user_params["setup_lookback"]
    consecutive_needed = user_params["consecutive_needed"]

    rsi_period = user_params["rsi_period"]
    rsi_overbought = user_params["rsi_overbought"]
    rsi_oversold = user_params["rsi_oversold"]

    vol_ma_period = user_params["vol_ma_period"]
    vol_spike_factor = user_params["vol_spike_factor"]

    color_buy = user_params["signal_color_buy"]
    color_sell = user_params["signal_color_sell"]
    alpha_signals = user_params["alpha_signals"]

    # ---------------------------
    # 2. Calcular RSI
    # ---------------------------
    # Para un RSI básico:
    # 1) Calcular cambios de precio (up, down)
    # 2) Media de subidas y bajadas (EMA)
    # 3) RSI = 100 - [100 / (1 + RS)].
    # Aquí usamos un enfoque rápido.

    # Asegurar que tengamos column 'Close'
    closes = data["Close"].values
    
    def compute_rsi(prices, period=14):
        """Devuelve un array con el RSI calculado."""
        deltas = np.diff(prices)
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period if len(seed[seed < 0]) > 0 else 0
        
        rs = up / down if down != 0 else 0
        rsi_array = [0]*(period)  # primeros 'period' sin RSI (o NaN)
        rsi_array.append(100 - 100/(1+rs))

        for i in range(period+1, len(prices)):
            delta = deltas[i-1]
            gain = max(delta, 0)
            loss = max(-delta, 0)

            up = (up*(period-1) + gain) / period
            down = (down*(period-1) + loss) / period
            rs = up / down if down != 0 else 0
            rsi_array.append(100 - 100/(1+rs))
        return rsi_array

    rsi_vals = compute_rsi(closes, rsi_period)
    # Para alinear mejor, podemos utilizar pd.Series(rsi_vals).shift(...) si fuera necesario.

    # ---------------------------
    # 3. Calcular media de volumen y pico
    # ---------------------------
    volumes = data["Volume"].values
    vol_series = pd.Series(volumes)
    vol_ma = vol_series.rolling(vol_ma_period).mean().fillna(method="bfill")

    # ---------------------------
    # 4. Conteo TD Setup simple
    #    - Contamos velas consecutivas vs. (N - setup_lookback)
    # ---------------------------
    bullish_count = 0
    bearish_count = 0

    # Listas para recolectar señales
    buy_signals_x = []
    buy_signals_y = []
    sell_signals_x = []
    sell_signals_y = []

    for i in range(setup_lookback, len(data)):
        current_close = data["Close"].iloc[i]
        prev_close = data["Close"].iloc[i - setup_lookback]

        # Chequeamos si vela alcista/bajista vs. (N - lookback)
        if current_close > prev_close:
            bullish_count += 1
            bearish_count = 0  # reseteamos el bajista
        elif current_close < prev_close:
            bearish_count += 1
            bullish_count = 0  # reseteamos el alcista
        else:
            # Si es igual, no sumamos ni a uno ni a otro
            pass

        # Si llegamos al conteo X (ej. 9) en alcista, evaluamos RSI/Volumen
        if bullish_count == consecutive_needed:
            # RSI alto = sobrecompra?
            if rsi_vals[i] >= rsi_overbought:
                # Volumen pico?
                if vol_ma[i] > 0 and (volumes[i] >= vol_spike_factor * vol_ma[i]):
                    # Señal de venta (posible agotamiento alcista)
                    sell_signals_x.append(dates[i])
                    # La posición "y" será el High o Close para dibujar el punto
                    precio_senal = data["High"].iloc[i]
                    sell_signals_y.append(precio_senal)

            # Reseteamos el conteo alcista para no tener señales repetidas
            bullish_count = 0

        # Si llegamos al conteo X (ej. 9) en bajista, evaluamos RSI/Volumen
        if bearish_count == consecutive_needed:
            # RSI bajo = sobreventa?
            if rsi_vals[i] <= rsi_oversold:
                # Volumen pico?
                if vol_ma[i] > 0 and (volumes[i] >= vol_spike_factor * vol_ma[i]):
                    # Señal de compra (posible agotamiento bajista)
                    buy_signals_x.append(dates[i])
                    precio_senal = data["Low"].iloc[i]
                    buy_signals_y.append(precio_senal)

            # Reseteamos el conteo bajista
            bearish_count = 0

    # ---------------------------
    # 5. Graficar señales en el Kline (Scatter)
    # ---------------------------
    # Scatter para señales de compra
    scatter_buy = (
        Scatter()
        .add_xaxis(buy_signals_x)
        .add_yaxis(
            series_name="TDMX Buy",
            y_axis=buy_signals_y,
            symbol="triangle",
            symbol_size=12,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=color_buy,
                opacity=alpha_signals
            ),
            yaxis_index=0,
        )
    )

    # Scatter para señales de venta
    scatter_sell = (
        Scatter()
        .add_xaxis(sell_signals_x)
        .add_yaxis(
            series_name="TDMX Sell",
            y_axis=sell_signals_y,
            symbol="pin",
            symbol_size=12,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=color_sell,
                opacity=alpha_signals
            ),
            yaxis_index=0,
        )
    )

    # Se superponen las señales en el chart principal (kline_obj)
    kline_obj.overlap(scatter_buy)
    kline_obj.overlap(scatter_sell)

    print("Overlay TDMX aplicado con señales:", 
          f"Buy={len(buy_signals_x)}, Sell={len(sell_signals_x)}")

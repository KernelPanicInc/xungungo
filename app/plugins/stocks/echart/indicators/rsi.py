# indicators/rsi.py

name = "RSI"
description = "Indicador RSI (Relative Strength Index)."
plugin_type = "overlay"  # o "grid", si quisieras su propio panel

def get_user_params():
    import streamlit as st

    st.sidebar.subheader("Configuración RSI")
    period = st.sidebar.number_input("Periodo RSI", 2, 100, 14)
    color = st.sidebar.color_picker("Color de RSI", "#2f4554")
    return {"period": period, "color": color}

def apply_to_chart(grid, data, dates, user_params):
    from pyecharts.charts import Line
    from pyecharts import options as opts
    import pandas as pd

    period = user_params.get("period", 14)
    color = user_params.get("color", "#2f4554")

    # Calcular RSI
    close_diff = data['Close'].diff()
    gain = close_diff.clip(lower=0).fillna(0)
    loss = -1 * close_diff.clip(upper=0).fillna(0)

    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))

    rsi_values = rsi.fillna(method="bfill").tolist()

    line_rsi = (
        Line()
        .add_xaxis(dates)
        .add_yaxis(
            series_name=f"RSI({period})",
            y_axis=rsi_values,
            is_smooth=True,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2, color=color),
        )
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=True))
    )

    # Igual que con el SMA, superponemos con el primer chart (Kline).
    if len(grid.chart_components) > 0:
        grid.chart_components[0].overlap(line_rsi)

    return grid

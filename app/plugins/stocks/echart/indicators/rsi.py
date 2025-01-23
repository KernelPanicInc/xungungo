# indicators/rsi.py

name = "RSI"
description = "Indicador RSI (Relative Strength Index)."
plugin_type = "grid"  # Va sobre el mismo panel (grid_index=1) del Volumen

def get_user_params(df = None):
    import streamlit as st
    st.sidebar.subheader("Configuración RSI")
    period = st.sidebar.number_input("Periodo RSI", 2, 100, 14)
    color = st.sidebar.color_picker("Color de RSI", "#2f4554")
    return {"period": period, "color": color}

def apply_grid(volume_chart, data, dates, user_params):
    from pyecharts.charts import Line
    from pyecharts import options as opts
    import pandas as pd

    period = user_params.get("period", 14)
    color = user_params.get("color", "#2f4554")

    # --- Cálculo RSI ---
    close_diff = data["Close"].diff()
    gain = close_diff.clip(lower=0).fillna(0)
    loss = -close_diff.clip(upper=0).fillna(0)

    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    rsi_values = rsi.fillna(method="bfill").tolist()

    # 1) Asegurarte de que "volume_chart" use xaxis_index=1, yaxis_index=0 en su Bar().
    #    Algo así en tu código principal, por ejemplo:
    #
    #    Bar()
    #    .add_xaxis(dates)
    #    .add_yaxis("Volumen", volume_list, yaxis_index=0, ...)
    #    .set_global_opts(
    #         xaxis_opts=opts.AxisOpts(grid_index=1),
    #         yaxis_opts=opts.AxisOpts(is_scale=True, grid_index=1),
    #    )
    #
    # 2) EXTENDER el chart para agregar un segundo eje Y (index=1):
    volume_chart.extend_axis(
        yaxis=opts.AxisOpts(
            type_="value",
            position="right",  # Eje a la derecha
            min_=0,           # Forzamos RSI entre 0 y 100
            max_=100,
            is_scale=False,   # No se reescala automáticamente
            grid_index=1,     # Mismo grid de volumen
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color=color)  # Color del eje
            ),
            # Opcional: nombre del eje
            name=f"RSI({period})",
        )
    )

    # 3) Crear la línea RSI que apunte a xaxis_index=1, yaxis_index=1
    line_rsi = (
        Line()
        .add_xaxis(dates)
        .add_yaxis(
            series_name=f"RSI({period})",
            y_axis=rsi_values,
            is_symbol_show=False,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=2, color=color),
            xaxis_index=1,  # Mismo x-axis del volumen
            yaxis_index=1,  # Eje Y extendido
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True),
            # Mantén las references a grid_index=1 para el panel inferior
            xaxis_opts=opts.AxisOpts(grid_index=1),
            # No modificar yaxis_opts aquí, ya lo hicimos en extend_axis
        )
    )

    # 4) "overlap" la línea RSI sobre el chart de volumen
    volume_chart.overlap(line_rsi)

name = "SMA"
plugin_type = "overlay"

def get_user_params():
    import streamlit as st

    with st.sidebar.expander("Parámetros SMA (3 líneas)", expanded=False):

        # SMA 1
        period1 = st.number_input("Periodo SMA #1", 2, 200, 20)
        color1 = st.color_picker("Color SMA #1", "#c23531")
        opacity1 = st.slider("Opacidad SMA #1", 0.0, 1.0, 1.0)
        st.write("---")

        # SMA 2
        period2 = st.number_input("Periodo SMA #2", 2, 200, 50)
        color2 = st.color_picker("Color SMA #2", "#00FF00")
        opacity2 = st.slider("Opacidad SMA #2", 0.0, 1.0, 1.0)
        st.write("---")

        # SMA 3
        period3 = st.number_input("Periodo SMA #3", 2, 200, 100)
        color3 = st.color_picker("Color SMA #3", "#0000FF")
        opacity3 = st.slider("Opacidad SMA #3", 0.0, 1.0, 1.0)

    return {
        "periods": [period1, period2, period3],
        "colors": [color1, color2, color3],
        "opacities": [opacity1, opacity2, opacity3]
    }

def apply_overlay(kline_obj, data, dates, user_params):
    print("Aplicando triple SMA overlay...")
    from pyecharts.charts import Line
    from pyecharts import options as opts

    periods = user_params["periods"]
    colors = user_params["colors"]
    opacities = user_params["opacities"]

    # Dibujamos cada SMA
    for p, c, alpha in zip(periods, colors, opacities):
        sma_vals = (
            data["Close"]
            .rolling(p)
            .mean()
            .fillna(method="bfill")
            .tolist()
        )

        line = (
            Line()
            .add_xaxis(dates)
            .add_yaxis(
                series_name=f"SMA({p})",
                y_axis=sma_vals,
                symbol="none",  # no dibujar puntos
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=3, color=c, opacity=alpha),
                yaxis_index=0,
                z=10,
            )
        )
        kline_obj.overlap(line)

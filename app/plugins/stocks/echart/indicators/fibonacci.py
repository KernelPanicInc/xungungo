name = "Fibonacci Retracements"
plugin_type = "overlay"

def get_user_params(data):
    import streamlit as st

    # Obtener valores predeterminados de high y low de los datos
    default_high = max(data["High"]) if "High" in data else 100.0
    default_low = min(data["Low"]) if "Low" in data else 50.0

    with st.sidebar.expander("Parámetros Fibonacci", expanded=False):
        high_price = st.number_input(
            "Precio Alto", 
            min_value=0.0, 
            value=default_high, 
            step=0.1
        )
        low_price = st.number_input(
            "Precio Bajo", 
            min_value=0.0, 
            value=default_low, 
            step=0.1
        )
        line_color = st.color_picker("Color de Líneas", "#FF5733")
        line_width = st.slider("Ancho de Líneas", min_value=1, max_value=5, value=2)

    return {
        "high_price": high_price,
        "low_price": low_price,
        "line_color": line_color,
        "line_width": line_width,
    }

def apply_overlay(kline_obj, data, dates, user_params):
    print("Aplicando Retrocesos de Fibonacci...")
    from pyecharts.charts import Line
    from pyecharts import options as opts

    high = user_params["high_price"]
    low = user_params["low_price"]
    line_color = user_params["line_color"]
    line_width = user_params["line_width"]

    # Niveles de retroceso estándar de Fibonacci
    fib_levels = [0.0, 0.236, 0.382, 0.5, 0.618, 1.0]
    levels = [(high - (high - low) * level) for level in fib_levels]

    # Agregar líneas horizontales para cada nivel
    for level, fib_value in zip(levels, fib_levels):
        line = (
            Line()
            .add_xaxis(dates)
            .add_yaxis(
                series_name=f"Fib {fib_value:.3f}",
                y_axis=[level] * len(dates),  # Línea horizontal en el nivel
                symbol="none",
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(
                    width=line_width,
                    color=line_color,
                    type_="dashed",  # Líneas discontinuas (opcional)
                ),
                yaxis_index=0,
                z=5,  # Dibujo por debajo de otros overlays
            )
        )
        kline_obj.overlap(line)

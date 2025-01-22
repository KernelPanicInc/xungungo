nombre = "EChart Plugin"
descripcion = "Plugin con panel de velas arriba y volumen abajo sin solaparse."
tipo = "stock"

def render(ticker):
    import streamlit as st
    from streamlit_echarts import st_pyecharts
    import yfinance as yf
    import datetime as dt

    from pyecharts.charts import Grid, Kline, Bar
    from pyecharts import options as opts
    from pyecharts.globals import ThemeType

    # Ajusta la ruta a tus archivos
    from plugins.stocks.echart.indicators.load_indicators import load_indicators
    from utils.flatten_columns import flatten_columns
    # ====== Parámetros de fecha
    st.sidebar.subheader("Rango de Fechas")
    start_date = st.sidebar.date_input("Fecha inicio", dt.date.today() - dt.timedelta(days=365))
    end_date = st.sidebar.date_input("Fecha fin", dt.datetime.combine(dt.date.today(), dt.time(11, 59)))
    if start_date > end_date:
        st.error("Fecha inicio > Fecha fin.")
        return

    # ====== Descarga de datos
    with st.spinner("Descargando datos..."):
        df = yf.download(ticker, start=start_date, end=end_date)
        df = flatten_columns(df)

    if df.empty:
        st.warning("No se encontraron datos en ese rango.")
        return

    # Preparar datos Kline
    dates = df.index.strftime("%Y-%m-%d").tolist()
    kline_data = []
    for o, c, l, h in zip(df["Open"], df["Close"], df["Low"], df["High"]):
        kline_data.append([o, c, l, h])

    # ====== Crear Grid
    grid = Grid(
        init_opts=opts.InitOpts(width="100%", height="800px", theme=ThemeType.LIGHT)
    )

    # ====== Panel de velas (arriba)
    kline_main = (
        Kline()
        .add_xaxis(dates)
        .add_yaxis(
            series_name="Precio",
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#14b143", border_color="#14b143", 
                color0="#ef232a", border_color0="#ef232a"
            ),
            yaxis_index=0,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"Gráfico {ticker}"),
            xaxis_opts=opts.AxisOpts(
                type_="category", 
                is_scale=True, 
                #boundary_gap=True,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False)
                ),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            datazoom_opts=[
                opts.DataZoomOpts(
                    type_="slider", 
                    xaxis_index=[0,1],
                    range_start=80,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    type_="inside", 
                    xaxis_index=[0,1],
                    pos_left="10%",
                    range_start=80,
                    range_end=100,      
                ),
            ],
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(
                pos_top="5%",
                pos_left="center",
                textstyle_opts=opts.TextStyleOpts(font_size=10),
            ),
        )
    )


    # ====== Panel de volumen (abajo)
    volume_list = df["Volume"].tolist()
    volume_chart = (
        Bar()
        .add_xaxis(dates)
        .add_yaxis(
            "Volumen",
            volume_list,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color="#5470C6"),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category", is_scale=True,
                # Ocultamos label X aquí, pues ya se ve arriba (opcional)
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            datazoom_opts=[
                # Los xaxis_index deben coincidir con [0,1] para compartir zoom
                opts.DataZoomOpts(
                    type_="slider", 
                    xaxis_index=[0,1],
                    range_start=80,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    type_="inside", 
                    xaxis_index=[0,1],
                    range_start=80,
                    range_end=100,
                ),
            ],
            legend_opts=opts.LegendOpts(is_show=True),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        )
    )


    # ====== Cargar plugins
    plugins = load_indicators()
    plugin_names = [p.name for p in plugins]

    st.sidebar.subheader("Indicadores Disponibles")
    selected_plugins = st.sidebar.multiselect("Indicadores", plugin_names, default=[])

    # ====== Aplicar plugins
    for plug in plugins:
        if plug.name in selected_plugins:
            user_params = {}
            if hasattr(plug, "get_user_params"):
                user_params = plug.get_user_params()

            plugin_type = getattr(plug, "plugin_type", "overlay")
            if plugin_type == "overlay" and hasattr(plug, "apply_overlay"):
                # Se solapa en el chart superior (velas)
                try:
                    plug.apply_overlay(kline_main, df, dates, user_params)
                except Exception as e:
                    st.error(f"Error en plugin {plug.name}: {e}")
                    continue
            elif plugin_type == "grid" and hasattr(plug, "apply_grid"):
                # Se solapa sobre el chart de volumen
                plug.apply_grid(volume_chart, df, dates, user_params)
            else:
                st.warning(f"Plugin {plug.name} sin función esperada.")


    # Lo ubicamos en la parte superior del grid (ej. 50% de altura)
    grid.add(
        kline_main,
        grid_opts=opts.GridOpts(
            height="70%"
        )
    )

    # Ubicamos el volumen en la mitad inferior (ej. 25% de altura)
    grid.add(
        volume_chart,
        grid_opts=opts.GridOpts(
            pos_top="80%",
            height="10%"
        ),
    )
    # ====== Render final
    st_pyecharts(grid, height="800px")

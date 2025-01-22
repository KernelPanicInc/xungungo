name = "TD Sequential"
plugin_type = "overlay"

def get_user_params():
    import streamlit as st

    st.sidebar.subheader("Parámetros TD Sequential")

    show_mode = st.sidebar.selectbox(
        "Mostrar conteo:",
        ["1 to 9", "solo 9", "ninguno"],
        index=0
    )

    # Elegir símbolo para “compra” y “venta”
    symbol_buy = st.sidebar.selectbox(
        "Símbolo compra:",
        ["circle", "triangle", "arrow", "pin", "diamond", "arrow"],
        index=3
    )
    symbol_sell = st.sidebar.selectbox(
        "Símbolo venta:",
        ["circle", "triangle", "arrow", "pin", "diamond", "arrow"],
        index=3
    )

    # Colores
    color_buy = st.sidebar.color_picker("Color BUY", "#00B050")
    color_sell = st.sidebar.color_picker("Color SELL", "#FF0000")

    return {
        "show_mode": show_mode,
        "symbol_buy": symbol_buy,
        "symbol_sell": symbol_sell,
        "color_buy": color_buy,
        "color_sell": color_sell,
    }

def apply_overlay(kline_obj, data, dates, user_params):
    import numpy as np
    from pyecharts.charts import Scatter
    from pyecharts import options as opts
    from pyecharts.commons.utils import JsCode

    show_mode  = user_params["show_mode"]
    symbol_buy = user_params["symbol_buy"]
    symbol_sell= user_params["symbol_sell"]
    color_buy  = user_params["color_buy"]
    color_sell = user_params["color_sell"]

    if not all(col in data.columns for col in ["Close", "High", "Low"]):
        print("[TD Sequential] ERROR: Falta columna (Close, High, Low) en el DataFrame.")
        return

    df = data.reset_index(drop=True)
    n = len(df)
    if n < 5:
        print("[TD Sequential] No hay datos suficientes (necesitamos al menos 5).")
        return

    # Cálculo buySet / sellSet
    buySet  = np.zeros(n, dtype=int)
    sellSet = np.zeros(n, dtype=int)

    for i in range(n):
        if i < 4:
            continue
        # Lógica DeMark (básica)
        if df["Close"][i] < df["Close"][i-4]:
            buySet[i] = 1 if buySet[i-1] == 9 else buySet[i-1] + 1
        else:
            buySet[i] = 0

        if df["Close"][i] > df["Close"][i-4]:
            sellSet[i] = 1 if sellSet[i-1] == 9 else sellSet[i-1] + 1
        else:
            sellSet[i] = 0

    # Generamos los puntos a dibujar
    buy_x, buy_y, buy_label = [], [], []
    sell_x, sell_y, sell_label = [], [], []

    for i in range(n):
        # Decide si dibujar 1..9 o solo 9 (o nada)
        if show_mode == "1 to 9" and buySet[i] > 0:
            buy_x.append(dates[i])
            buy_y.append(df["Low"][i] * 0.99)
            buy_label.append(str(buySet[i]))
        elif show_mode == "solo 9" and buySet[i] == 9:
            buy_x.append(dates[i])
            buy_y.append(df["Low"][i] * 0.99)
            buy_label.append("9")

        if show_mode == "1 to 9" and sellSet[i] > 0:
            sell_x.append(dates[i])
            sell_y.append(df["High"][i] * 1.005)
            sell_label.append(str(sellSet[i]))
        elif show_mode == "solo 9" and sellSet[i] == 9:
            sell_x.append(dates[i])
            sell_y.append(df["High"][i] * 1.005)
            sell_label.append("9")

    # Scatter para BUY
    scatter_buy = (
        Scatter()
        .add_xaxis(buy_x)
        .add_yaxis(
            series_name="TD Buy",
            y_axis=buy_y,
            symbol=symbol_buy,
            symbol_size=8,
            label_opts=opts.LabelOpts(
                is_show=True,
                position="bottom",
                color="#00B050",
                rich={
                        "big": {
                            "fontSize": 16,
                            "fontWeight": "bold",
                            "color": "#00B050"
                        }
                    },
                formatter=JsCode(
                                """
                                function (params) {
                                    var val = params.value[2];
                                    if (val === "9") {
                                        return '{big|' + val + '}';
                                    }
                                    return val;
                                }
                                """
                            )
            ),
            itemstyle_opts=opts.ItemStyleOpts(color=color_buy),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode("""
                    function(params) {
                        return 'BuySet: ' + params.value[2];
                    }
                """)
            ),
        )
    )
    buy_data_with_label = []
    for x, y, lbl in zip(buy_x, buy_y, buy_label):
        buy_data_with_label.append([x, y, lbl])
    scatter_buy.options["series"][0]["data"] = buy_data_with_label

    # Scatter para SELL
    scatter_sell = (
        Scatter()
        .add_xaxis(sell_x)
        .add_yaxis(
            series_name="TD Sell",
            y_axis=sell_y,
            symbol=symbol_sell,
            symbol_size=12,
            label_opts=opts.LabelOpts(
                            is_show=True,
                            position="top",
                            color="#FF0000",
                            rich={
                                    "big": {
                                        "fontSize": 16,
                                        "fontWeight": "bold",
                                        "color": "#FF0000",
                                        "borderRadius": 4,
                                        "borderColor" : "#FF0000",
                                        "borderWidth" : 1,
                                        "padding" : [2, 4]
                                    }
                            },
                            formatter=JsCode(
                                """
                                function (params) {
                                    var val = params.value[2];
                                    if (val === "9") {
                                        return '{big|' + val + '}';
                                    }
                                    return val;
                                }
                                """
                            )
                        ),
            itemstyle_opts=opts.ItemStyleOpts(color=color_sell),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode("""
                    function(params) {
                        return 'SellSet: ' + params.value[2];
                    }
                """)
            ),
        )
    )
    sell_data_with_label = []
    for x, y, lbl in zip(sell_x, sell_y, sell_label):
        sell_data_with_label.append([x, y, lbl])
    scatter_sell.options["series"][0]["data"] = sell_data_with_label

    # Montamos en el gráfico principal
    kline_obj.overlap(scatter_buy)
    kline_obj.overlap(scatter_sell)

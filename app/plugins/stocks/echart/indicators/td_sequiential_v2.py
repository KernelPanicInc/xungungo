name = "TD Sequential (Avanzado)"
plugin_type = "overlay"

def get_user_params(data = None):
    import streamlit as st

    st.sidebar.subheader("Parámetros TD Sequential (Avanzado)")

    # Modo de Setup (1..9, solo 9, ninguno)
    show_mode = st.sidebar.selectbox(
        "Mostrar conteo Setup:",
        ["1 to 9", "solo 9", "ninguno"],
        index=0
    )

    # Modo de Countdown (1..13, solo 13, ninguno)
    show_countdown = st.sidebar.selectbox(
        "Mostrar TD Countdown:",
        ["1 to 13", "solo 13", "ninguno"],
        index=0
    )

    # Elegir símbolos y colores
    symbol_buy     = st.sidebar.selectbox("Símbolo Setup BUY",  ["circle","triangle","pin","arrow"],  index=1)
    symbol_sell    = st.sidebar.selectbox("Símbolo Setup SELL", ["circle","triangle","pin","arrow"],  index=1)
    symbol_cdbuy   = st.sidebar.selectbox("Símbolo Countdown BUY",  ["circle","triangle","rect","diamond"], index=1)
    symbol_cdsell  = st.sidebar.selectbox("Símbolo Countdown SELL", ["circle","triangle","rect","diamond"], index=1)

    color_buy     = st.sidebar.color_picker("Color Setup BUY", "#00B050")
    color_sell    = st.sidebar.color_picker("Color Setup SELL", "#FF0000")
    color_cdbuy   = st.sidebar.color_picker("Color Countdown BUY", "#0080FF")
    color_cdsell  = st.sidebar.color_picker("Color Countdown SELL", "#FFC000")

    return {
        "show_mode": show_mode,
        "show_countdown": show_countdown,
        "symbol_buy": symbol_buy,
        "symbol_sell": symbol_sell,
        "symbol_cdbuy": symbol_cdbuy,
        "symbol_cdsell": symbol_cdsell,
        "color_buy": color_buy,
        "color_sell": color_sell,
        "color_cdbuy": color_cdbuy,
        "color_cdsell": color_cdsell,
    }


def apply_overlay(kline_obj, data, dates, user_params):
    import numpy as np
    from pyecharts.charts import Scatter
    from pyecharts import options as opts
    from pyecharts.commons.utils import JsCode

    # ---------------------------------------------------------------------
    # 1. Validar columnas y extraer parámetros
    # ---------------------------------------------------------------------
    required_cols = ["Close", "High", "Low"]
    if not all(col in data.columns for col in required_cols):
        print(f"[TD Sequential] ERROR: Falta alguna de las columnas requeridas: {required_cols}")
        return

    df = data.reset_index(drop=True)
    n  = len(df)
    if n < 20:
        print("[TD Sequential] No hay datos suficientes (mínimo ~20 para un ejemplo con Countdown).")
        return

    show_mode      = user_params["show_mode"]        # Setup (1..9, solo 9, ninguno)
    show_countdown = user_params["show_countdown"]   # Countdown (1..13, solo 13, ninguno)

    symbol_buy    = user_params["symbol_buy"]
    symbol_sell   = user_params["symbol_sell"]
    symbol_cdbuy  = user_params["symbol_cdbuy"]
    symbol_cdsell = user_params["symbol_cdsell"]

    color_buy     = user_params["color_buy"]
    color_sell    = user_params["color_sell"]
    color_cdbuy   = user_params["color_cdbuy"]
    color_cdsell  = user_params["color_cdsell"]

    # ---------------------------------------------------------------------
    # 2. Cálculo de TD Setup + "Setup Perfection"
    # ---------------------------------------------------------------------
    # Manejaremos el setup con un estado para BUY y otro para SELL.  
    # Guardaremos en arrays: buySetup[i], sellSetup[i] con la cuenta de Setup (1..9),  
    # o 0 si no hay setup. Cuando un setup está "extendido" mientras busca perfección,
    # seguiremos marcando 9 en los siguientes bares, pero sin "confirmar" la perfección
    # hasta que se cumpla la condición.
    buySetup  = np.zeros(n, dtype=int)
    sellSetup = np.zeros(n, dtype=int)

    # Para saber si ya se "perfeccionó" un setup:
    buyPerfectedAt  = -1  # índice donde el setup BUY quedó perfeccionado
    sellPerfectedAt = -1  # índice donde el setup SELL quedó perfeccionado

    # Estados de si estamos construyendo un setup (BUY o SELL).
    buyCount  = 0
    sellCount = 0

    # Índice donde empezó el setup actual (BUY/SELL). Lo necesitamos
    # para verificar perfecciones con alguna referencia, si se desea.
    buySetupStartIndex  = -1
    sellSetupStartIndex = -1

    # Reglas de reset: si un setup de BUY está en curso y se cumple la condición
    # contraria para SELL, a veces se resetea. Aquí haremos un approach simple:
    # Si un setup opuesto se inicia (count=1) mientras uno no ha sido perfeccionado,
    # reiniciamos el anterior. (Regla abreviada, no oficial)

    for i in range(n):
        if i < 4:
            continue

        close_now  = df["Close"][i]
        close_prev = df["Close"][i-4]

        # ----------------------------
        # 2.1. Chequeo setup BUY
        # ----------------------------
        if buyCount == 0:
            # si no hay BUY en curso, ¿se inicia uno?
            if close_now < close_prev:
                buyCount = 1
                buySetup[i] = 1
                buySetupStartIndex = i
        else:
            # ya estamos en un setup buy
            if close_now < close_prev:
                if buyCount < 9:
                    buyCount += 1
                    buySetup[i] = buyCount
                else:
                    # Ya llegamos a 9 en algún bar anterior,
                    # seguimos "extendiéndolo" con 9 mientras no se perfeccione
                    buySetup[i] = 9
                # Nota: no reseteamos buyCount aquí
            else:
                # Se rompe la secuencia
                buyCount = 0
                # buySetup[i] = 0  # (por defecto ya es 0)

        # ----------------------------
        # 2.2. Chequeo setup SELL
        # ----------------------------
        if sellCount == 0:
            if close_now > close_prev:
                sellCount = 1
                sellSetup[i] = 1
                sellSetupStartIndex = i
        else:
            if close_now > close_prev:
                if sellCount < 9:
                    sellCount += 1
                    sellSetup[i] = sellCount
                else:
                    # Extendido con 9
                    sellSetup[i] = 9
            else:
                sellCount = 0

        # ----------------------------
        # 2.3. Regla simple de reset opuesto (opcional)
        #     Si se inicia un setup SELL y hay un BUY sin perfeccionar, lo reseteamos.
        #     Y viceversa.
        # ----------------------------
        # Ejemplo: si sellCount == 1 y buyPerfectedAt < 0 (no se perfeccionó)
        # y buyCount > 0, podemos resetear buyCount = 0.  
        # Esto es extremadamente simplificado; muchas variantes no resetean así.
        if sellCount == 1 and buyCount > 0 and (buyPerfectedAt < 0):
            buyCount = 0  # anular buy
        if buyCount == 1 and sellCount > 0 and (sellPerfectedAt < 0):
            sellCount = 0

        # -----------------------------------------------------------------
        # 2.4. "Setup Perfection"
        #
        #  - Una versión simplificada: si ya tenemos un "9" (o extendido)
        #    miramos si el low (para BUY) o high (para SELL) del bar actual
        #    cumple cierta condición (p.ej. "low[i] <= min( low[i-2], low[i-3] )").
        #    Cuando se cumpla, marcamos que el Setup se perfecciona en i.
        #
        #  - La realidad: hay reglas más elaboradas: se compara la close de
        #    bar 8 o 9 con la low de ciertos bares previos, etc.
        # -----------------------------------------------------------------

        # BUY perfection
        if buyCount >= 9 and buyPerfectedAt < 0:
            # Condición muy simplificada: low actual <= low de hace 2 barras
            # (en la práctica, la referencia varía). Ajusta a tu gusto.
            if i >= 2:
                if df["Low"][i] <= df["Low"][i-2]:
                    buyPerfectedAt = i  # se perfeccionó
                    # (Podríamos dejar un "banderazo" en buySetup[i] = 99, p.ej.:
                    #  para mostrar un 9 con un indicador "P". Lo veremos al graficar)
                    # buySetup[i] = 9  # ya lo está
                # Si no se perfecciona, seguimos con 9 en cada bar hasta que se cumpla.

        # SELL perfection
        if sellCount >= 9 and sellPerfectedAt < 0:
            if i >= 2:
                if df["High"][i] >= df["High"][i-2]:
                    sellPerfectedAt = i
                    # sellSetup[i] = 9  # ya está en 9

    # ---------------------------------------------------------------------
    # 3. TD Countdown (con reinicio si aparece un Setup 9 opuesto perfecto)
    # ---------------------------------------------------------------------
    # - Empezamos el countdown de BUY sólo si buyPerfectedAt >= 0
    #   (es decir, ya se encontró un 9 de BUY y se "perfeccionó").  
    # - Se inicia a partir del **bar siguiente** a la perfección.
    # - Regla de conteo (simplificada): sumamos 1..13 cuando close[i] < close[i-2].
    # - Si durante el conteo BUY aparece un SELL 9 perfeccionado, se cancela el BUY countdown.
    #   (y viceversa)
    #
    buyCountdown  = np.zeros(n, dtype=int)
    sellCountdown = np.zeros(n, dtype=int)

    # Si no se perfeccionó, no hay countdown.
    if buyPerfectedAt >= 0:
        in_buy_countdown = True
        count_b = 0
        for i in range(buyPerfectedAt + 1, n):
            # Si vemos un SELL 9 perfeccionado, cancelamos
            if sellPerfectedAt >= 0 and i >= sellPerfectedAt:
                in_buy_countdown = False
                break

            if i >= 2 and in_buy_countdown:
                # Condición simplificada: close[i] < close[i-2]
                if df["Close"][i] < df["Close"][i-2]:
                    count_b += 1
                    buyCountdown[i] = count_b
                    if count_b == 13:
                        # Una vez llegamos a 13, paramos
                        in_buy_countdown = False
                        break

    if sellPerfectedAt >= 0:
        in_sell_countdown = True
        count_s = 0
        for i in range(sellPerfectedAt + 1, n):
            # Si aparece un BUY 9 perfeccionado en el camino, cancelamos
            if buyPerfectedAt >= 0 and i >= buyPerfectedAt:
                in_sell_countdown = False
                break

            if i >= 2 and in_sell_countdown:
                if df["Close"][i] > df["Close"][i-2]:
                    count_s += 1
                    sellCountdown[i] = count_s
                    if count_s == 13:
                        in_sell_countdown = False
                        break

    # ---------------------------------------------------------------------
    # 4. Preparar datos para graficar Setup (Scatter)
    # ---------------------------------------------------------------------
    buy_x, buy_y, buy_label = [], [], []
    sell_x, sell_y, sell_label = [], [], []

    for i in range(n):
        bval = buySetup[i]
        sval = sellSetup[i]
        if bval > 0:
            # Opción: si show_mode="solo 9" y bval<9 => no mostramos
            if (show_mode == "1 to 9") or (show_mode == "solo 9" and bval == 9):
                buy_x.append(dates[i])
                # Bajarlo un poco del Low
                buy_y.append(df["Low"][i] * 0.99)
                # Marcamos "9P" si se perfeccionó justo en este bar
                # (o bval=9 y i>=buyPerfectedAt)
                if bval == 9 and i == buyPerfectedAt:
                    buy_label.append("9P")  # 9 Perfected
                else:
                    buy_label.append(str(bval))

        if sval > 0:
            if (show_mode == "1 to 9") or (show_mode == "solo 9" and sval == 9):
                sell_x.append(dates[i])
                sell_y.append(df["High"][i] * 1.005)
                if sval == 9 and i == sellPerfectedAt:
                    sell_label.append("9P")
                else:
                    sell_label.append(str(sval))

    scatter_buy = (
        Scatter()
        .add_xaxis(buy_x)
        .add_yaxis(
            series_name="TD Setup BUY",
            y_axis=buy_y,
            symbol=symbol_buy,
            symbol_size=8,
            label_opts=opts.LabelOpts(
                is_show=True,
                position="bottom",
                color=color_buy,
                rich={
                    "big": {
                        "fontSize": 16,
                        "fontWeight": "bold",
                        "color": color_buy
                    }
                },
                formatter=JsCode(
                    """
                    function (params) {
                        var val = params.value[2];
                        if (val === "9" || val==="9P") {
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
                        return 'Setup BUY: ' + params.value[2];
                    }
                """)
            ),
        )
    )
    buy_data_with_label = []
    for x, y, lbl in zip(buy_x, buy_y, buy_label):
        buy_data_with_label.append([x, y, lbl])
    scatter_buy.options["series"][0]["data"] = buy_data_with_label

    scatter_sell = (
        Scatter()
        .add_xaxis(sell_x)
        .add_yaxis(
            series_name="TD Setup SELL",
            y_axis=sell_y,
            symbol=symbol_sell,
            symbol_size=8,
            label_opts=opts.LabelOpts(
                is_show=True,
                position="top",
                color=color_sell,
                rich={
                    "big": {
                        "fontSize": 16,
                        "fontWeight": "bold",
                        "color": color_sell
                    }
                },
                formatter=JsCode(
                    """
                    function (params) {
                        var val = params.value[2];
                        if (val === "9" || val==="9P") {
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
                        return 'Setup SELL: ' + params.value[2];
                    }
                """)
            ),
        )
    )
    sell_data_with_label = []
    for x, y, lbl in zip(sell_x, sell_y, sell_label):
        sell_data_with_label.append([x, y, lbl])
    scatter_sell.options["series"][0]["data"] = sell_data_with_label

    # ---------------------------------------------------------------------
    # 5. Preparar datos para graficar Countdown (Scatter)
    # ---------------------------------------------------------------------
    cdbuy_x,  cdbuy_y,  cdbuy_label   = [], [], []
    cdsell_x, cdsell_y, cdsell_label = [], [], []

    for i in range(n):
        bcd = buyCountdown[i]
        scd = sellCountdown[i]

        if bcd > 0:
            # "solo 13" o "1 to 13"
            if show_countdown == "1 to 13" or (show_countdown == "solo 13" and bcd == 13):
                cdbuy_x.append(dates[i])
                # Un poco más abajo que el setup
                cdbuy_y.append(df["Low"][i] * 0.97)
                cdbuy_label.append(str(bcd))

        if scd > 0:
            if show_countdown == "1 to 13" or (show_countdown == "solo 13" and scd == 13):
                cdsell_x.append(dates[i])
                cdsell_y.append(df["High"][i] * 1.01)
                cdsell_label.append(str(scd))

    scatter_cdbuy = (
        Scatter()
        .add_xaxis(cdbuy_x)
        .add_yaxis(
            series_name="TD CD BUY",
            y_axis=cdbuy_y,
            symbol=symbol_cdbuy,
            symbol_size=10,
            label_opts=opts.LabelOpts(
                is_show=True,
                position="bottom",
                color=color_cdbuy,
                rich={
                    "big": {
                        "fontSize": 14,
                        "fontWeight": "bold",
                        "color": color_cdbuy
                    }
                },
                formatter=JsCode(
                    """
                    function (params) {
                        var val = params.value[2];
                        if (val === "13") {
                            return '{big|' + val + '}';
                        }
                        return val;
                    }
                    """
                )
            ),
            itemstyle_opts=opts.ItemStyleOpts(color=color_cdbuy),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode("""
                    function(params) {
                        return 'Countdown BUY: ' + params.value[2];
                    }
                """)
            ),
        )
    )
    cdbuy_data_with_label = []
    for x, y, lbl in zip(cdbuy_x, cdbuy_y, cdbuy_label):
        cdbuy_data_with_label.append([x, y, lbl])
    scatter_cdbuy.options["series"][0]["data"] = cdbuy_data_with_label

    scatter_cdsell = (
        Scatter()
        .add_xaxis(cdsell_x)
        .add_yaxis(
            series_name="TD CD SELL",
            y_axis=cdsell_y,
            symbol=symbol_cdsell,
            symbol_size=10,
            label_opts=opts.LabelOpts(
                is_show=True,
                position="top",
                color=color_cdsell,
                rich={
                    "big": {
                        "fontSize": 14,
                        "fontWeight": "bold",
                        "color": color_cdsell
                    }
                },
                formatter=JsCode(
                    """
                    function (params) {
                        var val = params.value[2];
                        if (val === "13") {
                            return '{big|' + val + '}';
                        }
                        return val;
                    }
                    """
                )
            ),
            itemstyle_opts=opts.ItemStyleOpts(color=color_cdsell),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode("""
                    function(params) {
                        return 'Countdown SELL: ' + params.value[2];
                    }
                """)
            ),
        )
    )
    cdsell_data_with_label = []
    for x, y, lbl in zip(cdsell_x, cdsell_y, cdsell_label):
        cdsell_data_with_label.append([x, y, lbl])
    scatter_cdsell.options["series"][0]["data"] = cdsell_data_with_label

    # ---------------------------------------------------------------------
    # 6. Añadir los scatters al Kline
    # ---------------------------------------------------------------------
    # Setup
    if show_mode != "ninguno":
        kline_obj.overlap(scatter_buy)
        kline_obj.overlap(scatter_sell)

    # Countdown
    if show_countdown != "ninguno":
        kline_obj.overlap(scatter_cdbuy)
        kline_obj.overlap(scatter_cdsell)

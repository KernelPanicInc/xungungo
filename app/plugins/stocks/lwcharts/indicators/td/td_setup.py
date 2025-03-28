import pandas as pd

def calculate_td_setup(
    data: pd.DataFrame, 
    show_only_full_setups: bool, 
    buy_setup_color: str, 
    sell_setup_color: str
):
    """
    Calcula el TD Setup y retorna:
      - setup_markers: lista de marcadores (diccionarios) para el gráfico
      - completed_buy_setups: índices donde se completó el Buy Setup
      - completed_sell_setups: índices donde se completó el Sell Setup

    Lógica:
      - Si show_only_full_setups=False => se agregan todos los números (1..9) a medida que se forman.
      - Si show_only_full_setups=True  => se agregan solo los que llegan a 9, pero 
        al final se muestra también la última serie activa (si no se rompió).
    """

    setup_markers = []
    completed_buy_setups = []
    completed_sell_setups = []

    # Estados de conteo
    buy_setup_count = 0
    sell_setup_count = 0

    # Almacenamos marcadores parciales en cada Setup
    buy_partials = []
    sell_partials = []

    def format_setup_text(count):
        mapping = {
            1: "①", 2: "②", 3: "③", 4: "④",
            5: "⑤", 6: "⑥", 7: "⑦", 8: "⑧", 9: "⑨"
        }
        return mapping.get(count, str(count))

    for i in range(5, len(data)):
        # -- Detección Bearish Flip (Inicio Buy Setup) --
        if (data.loc[i, "Close"] < data.loc[i-4, "Close"]
            and data.loc[i-1, "Close"] > data.loc[i-5, "Close"]):
            # Romper el Sell Setup en curso
            if not show_only_full_setups and sell_partials:
                # Los marcadores parciales de sell ya están en el setup_markers (si existían)
                pass
            sell_setup_count = 0
            sell_partials = []

            # Iniciar Buy Setup
            buy_setup_count = 1
            buy_partials = [{
                "time": int(data.loc[i, "Fecha"].timestamp()),
                "position": "belowBar",
                "color": buy_setup_color,
                "text": format_setup_text(buy_setup_count)
            }]

            if not show_only_full_setups:
                # Agregar el "①" inmediatamente
                setup_markers.append(buy_partials[-1])
            continue

        # -- Detección Bullish Flip (Inicio Sell Setup) --
        if (data.loc[i, "Close"] > data.loc[i-4, "Close"]
            and data.loc[i-1, "Close"] < data.loc[i-5, "Close"]):
            # Romper el Buy Setup en curso
            if not show_only_full_setups and buy_partials:
                pass
            buy_setup_count = 0
            buy_partials = []

            # Iniciar Sell Setup
            sell_setup_count = 1
            sell_partials = [{
                "time": int(data.loc[i, "Fecha"].timestamp()),
                "position": "aboveBar",
                "color": sell_setup_color,
                "text": format_setup_text(sell_setup_count)
            }]

            if not show_only_full_setups:
                setup_markers.append(sell_partials[-1])
            continue

        # -- Continuar Buy Setup --
        if buy_setup_count > 0:
            if data.loc[i, "Close"] < data.loc[i-4, "Close"]:
                buy_setup_count += 1
                marker = {
                    "time": int(data.loc[i, "Fecha"].timestamp()),
                    "position": "belowBar",
                    "color": buy_setup_color,
                    "text": format_setup_text(buy_setup_count)
                }

                if buy_setup_count == 9:
                    marker["shape"] = "circle"

                buy_partials.append(marker)

                if not show_only_full_setups:
                    # Se muestran parciales en tiempo real
                    setup_markers.append(marker)

                if buy_setup_count == 9:
                    completed_buy_setups.append(i)
                    if show_only_full_setups:
                        # Si solo mostramos completos, ahora sí añadimos toda la secuencia
                        setup_markers.extend(buy_partials)
                    # Reset
                    buy_setup_count = 0
                    buy_partials = []
            else:
                # Se rompe antes de 9
                if not show_only_full_setups:
                    # Los parciales ya se mostraron en tiempo real, no hacemos nada
                    pass
                buy_setup_count = 0
                buy_partials = []

        # -- Continuar Sell Setup --
        if sell_setup_count > 0:
            if data.loc[i, "Close"] > data.loc[i-4, "Close"]:
                sell_setup_count += 1
                marker = {
                    "time": int(data.loc[i, "Fecha"].timestamp()),
                    "position": "aboveBar",
                    "color": sell_setup_color,
                    "text": format_setup_text(sell_setup_count)
                }

                if sell_setup_count == 9:
                    marker["shape"] = "circle"

                sell_partials.append(marker)

                if not show_only_full_setups:
                    setup_markers.append(marker)

                if sell_setup_count == 9:
                    completed_sell_setups.append(i)
                    if show_only_full_setups:
                        setup_markers.extend(sell_partials)
                    sell_setup_count = 0
                    sell_partials = []
            else:
                # Se rompe antes de 9
                if not show_only_full_setups:
                    pass
                sell_setup_count = 0
                sell_partials = []

    # ✅ Mostrar la última serie activa si no se completó ni se rompió
    # Esto solo aplica cuando show_only_full_setups=True y hay un Setup en curso
    if show_only_full_setups:
        # Buy Setup activo
        if buy_setup_count > 0 and len(buy_partials) > 0:
            # Agregamos el último marcador (barra actual)
            setup_markers.append(buy_partials[-1])

        # Sell Setup activo
        if sell_setup_count > 0 and len(sell_partials) > 0:
            setup_markers.append(sell_partials[-1])

    return setup_markers, completed_buy_setups, completed_sell_setups

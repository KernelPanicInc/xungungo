import pandas as pd

def calculate_td_countdown(
    data: pd.DataFrame, 
    completed_setups: list, 
    countdown_type: str, 
    countdown_marker_color: str, 
    only_complete_countdown: bool = False, 
    contrary_setups: list = None
) -> list:
    """
    Calcula el TD Countdown a partir de los índices donde se completó el TD Setup.
    
    Parámetros:
      - data: DataFrame que debe contener las columnas "Close", "Low", "High" y "Fecha".
      - completed_setups: Lista de índices donde se completó el TD Setup (índices del 9).
      - countdown_type: "buy" o "sell".
      - countdown_marker_color: Color para los markers del countdown.
      - only_complete_countdown: Si True, solo muestra countdowns completos (hasta 13)
          y, en caso de que una secuencia activa no se complete, muestra la secuencia completa.
      - contrary_setups: Lista de índices donde se completó el Setup contrario. Si se encuentra uno, se cancela el countdown.
      
    Retorna:
      - countdown_markers: Lista de diccionarios, cada uno representando un marker del countdown.
    """
    if contrary_setups is None:
        contrary_setups = []

    countdown_markers = []

    for setup_index in completed_setups:
        count = 0
        sequence_markers = []
        broke = False  # Flag que indica si se canceló el countdown por un Setup contrario

        # Iniciar el Countdown en la misma barra donde está el 9 del Setup
        for i in range(setup_index, len(data)):
            # Si se detecta un Setup contrario, se cancela el countdown actual
            if i in contrary_setups:
                broke = True
                break

            if i < 2:
                continue

            if countdown_type.lower() == "buy":
                # Condición para TD Buy Countdown: cierre actual <= mínimo de 2 barras atrás
                if data.loc[i, "Close"] <= data.loc[i-2, "Low"]:
                    count += 1
                    marker = {
                        "time": int(data.loc[i, "Fecha"].timestamp()),
                        "position": "belowBar",  # Para Buy Countdown se dibuja en la parte superior
                        "color": countdown_marker_color,
                        "text": f"{count}"
                    }
                    if count == 13:
                        marker["shape"] = "arrowUp"
                        marker["size"] = 1
                        sequence_markers.append(marker)
                        break
                    sequence_markers.append(marker)

            elif countdown_type.lower() == "sell":
                # Condición para TD Sell Countdown: cierre actual >= máximo de 2 barras atrás
                if data.loc[i, "Close"] >= data.loc[i-2, "High"]:
                    count += 1
                    marker = {
                        "time": int(data.loc[i, "Fecha"].timestamp()),
                        "position": "aboveBar",  # Para Sell Countdown se dibuja en la parte inferior
                        "color": countdown_marker_color,
                        "text": f"{count}"
                    }
                    if count == 13:
                        marker["shape"] = "arrowDown"
                        marker["size"] = 1
                        sequence_markers.append(marker)
                        break
                    sequence_markers.append(marker)

        # Según la opción, agregamos la secuencia completa
        if only_complete_countdown:
            # Si la secuencia se completó (llegó a 13), o si no se rompió, mostramos toda la secuencia acumulada
            if (count == 13) or (not broke and sequence_markers):
                countdown_markers.extend(sequence_markers)
        else:
            countdown_markers.extend(sequence_markers)

    # Ordenar los markers por "time"
    countdown_markers = sorted(countdown_markers, key=lambda x: x["time"])
    return countdown_markers

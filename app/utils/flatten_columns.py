import pandas as pd

def flatten_columns(df):
    """
    Aplana las columnas de un DataFrame si tienen un índice jerárquico (MultiIndex)
    y conserva solo los nombres principales (Close, High, Low, Open, Volume), eliminando el ticker.

    Args:
        df (pd.DataFrame): DataFrame con columnas potencialmente jerárquicas.

    Returns:
        pd.DataFrame: DataFrame con columnas aplanadas (nombres simples).
    """
    if isinstance(df.columns, pd.MultiIndex):
        # Tomar solo el primer nivel del MultiIndex para eliminar el ticker
        df.columns = [col[0] for col in df.columns]
    return df

# widgets/widget_chart.py
import streamlit as st
import pandas as pd
from plugins.dashboard.widgets.widget_base import WidgetBase

class ChartWidget(WidgetBase):
    def __init__(self, widget_id: str, params: dict):
        self.widget_id = widget_id
        self.title = params.get('title', 'Título por defecto')
        self.data_source = params.get('data_source', None)

    def render(self):
        st.write(f"**ChartWidget (ID: {self.widget_id})**")
        st.write(f"Título: {self.title}")

        if self.data_source:
            try:
                df = pd.read_csv(self.data_source)
                st.line_chart(df)
            except Exception as e:
                st.error(f"No se pudo cargar el archivo: {e}")
        else:
            st.warning("No se especificó data_source.")

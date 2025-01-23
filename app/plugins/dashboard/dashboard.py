import json
import streamlit as st
from plugins.dashboard.widgets import get_widget_class
from plugins.dashboard.add_widgets import add_widget
import os
from plugins.dashboard.widgets import load_widgets

class DashboardManager:
    """
    Clase principal para gestionar la configuración y renderización del dashboard.
    """
    def __init__(self, config_path="dashboard_config.json", widget_folder="widgets"):
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self.widget_folder = widget_folder
        self.config = self.load_config()
        self.widgets = self.load_widgets()

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_widgets(self):
        st.write("Cargando widgets...")
        return load_widgets(self.widget_folder)

    def add_widget_dialog(self):
        add_widget(self.widgets)

    def render(self):
        topcol1, topcol2, topcol3 = st.columns((2, 8, 2))
        with topcol3:
            st.button(icon=":material/add_box:", on_click=self.add_widget_dialog, label="Añadir Widget")

        # Extraemos cuántas columnas se requieren (por defecto 2)
        num_columns = self.config.get("layout", {}).get("columns", 2)
        columns = st.columns(num_columns)

        # Recorremos la lista de widgets
        for widget_info in self.config.get("widgets", []):
            wtype = widget_info["type"]
            wid = widget_info["id"]
            params = widget_info.get("params", {})
            col_index = widget_info.get("column", 0)

            # Obtenemos la clase del widget
            WidgetClass = get_widget_class(wtype)

            # Instanciamos el widget
            widget_obj = WidgetClass(wid, params)

            # Renderizamos el widget en la columna correspondiente
            with columns[col_index]:
                widget_obj.render()


dashboard = DashboardManager()
dashboard.render()
import json
import streamlit as st
from plugins.dashboard.widgets import get_widget_class
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "dashboard_config.json")

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def config_page():
    st.title("Configuración de Widgets")

    config = load_config()

    # 1. Mostrar y editar widgets existentes
    st.subheader("Widgets existentes")

    # Iteramos sobre cada widget en la configuración
    for i, widget_info in enumerate(config.get("widgets", [])):
        widget_id = widget_info.get("id", f"widget_{i}")
        widget_type = widget_info.get("type", "Unknown")
        widget_params = widget_info.get("params", {})
        widget_column = widget_info.get("column", 0)

        with st.expander(f"Widget: {widget_id} ({widget_type})", expanded=False):
            st.write(f"**ID**: `{widget_id}` | **Columna**: `{widget_column}`")

            # Creamos un formulario para editar parámetros
            form_key = f"form_{widget_id}"
            with st.form(key=form_key):
                st.markdown("**Parámetros**")

                if widget_type == "CounterWidget":
                    start_value = st.number_input(
                        "start_value", 
                        value=widget_params.get('start_value', 0),
                        key=f"start_value_{widget_id}"
                    )
                    increment = st.number_input(
                        "increment", 
                        value=widget_params.get('increment', 1),
                        key=f"increment_{widget_id}"
                    )
                    
                    # Botón de guardar (solo afecta este widget)
                    if st.form_submit_button("Guardar cambios"):
                        # Actualizamos la config con los valores editados
                        config["widgets"][i]["params"]["start_value"] = start_value
                        config["widgets"][i]["params"]["increment"] = increment
                        save_config(config)
                        st.success(f"¡Parámetros guardados para {widget_id}!")
                        st.experimental_rerun()

                elif widget_type == "ChartWidget":
                    title = st.text_input(
                        "Título", 
                        value=widget_params.get("title", "Título por defecto"),
                        key=f"title_{widget_id}"
                    )
                    data_source = st.text_input(
                        "Archivo CSV",
                        value=widget_params.get("data_source", ""),
                        key=f"data_source_{widget_id}"
                    )

                    # Botón de guardar (solo afecta este widget)
                    if st.form_submit_button("Guardar cambios"):
                        config["widgets"][i]["params"]["title"] = title
                        config["widgets"][i]["params"]["data_source"] = data_source
                        save_config(config)
                        st.success(f"¡Parámetros guardados para {widget_id}!")
                        st.experimental_rerun()

                else:
                    st.info("Tipo de widget no reconocido o sin configuración específica.")
                    # Podrías mostrar campos genéricos, si fuera el caso.

            # Botón para eliminar el widget (fuera del form, o en otro form separado)
            if st.button(f"Eliminar {widget_id}", key=f"del_{widget_id}"):
                del config["widgets"][i]
                save_config(config)
                st.warning(f"Se eliminó el widget {widget_id}.")
                st.experimental_rerun()

    st.write("---")
    # 2. Agregar nuevo widget
    st.subheader("Agregar nuevo widget")
    new_widget_type = st.selectbox("Selecciona tipo de widget", ["CounterWidget", "ChartWidget"])
    new_widget_id = st.text_input("ID del widget", value="widget_nuevo")
    new_widget_column = st.number_input("Columna", min_value=0, value=0)

    # Parámetros específicos para el nuevo widget
    new_params = {}

    if new_widget_type == "CounterWidget":
        start_value = st.number_input("start_value", value=0)
        increment = st.number_input("increment", value=1)
        new_params = {
            "start_value": start_value,
            "increment": increment
        }

    elif new_widget_type == "ChartWidget":
        title = st.text_input("Título", value="Nuevo Gráfico")
        data_source = st.text_input("Archivo CSV", value="data.csv")
        new_params = {
            "title": title,
            "data_source": data_source
        }

    # Botón para confirmar adición de nuevo widget
    if st.button("Agregar widget"):
        new_widget = {
            "id": new_widget_id,
            "type": new_widget_type,
            "column": new_widget_column,
            "params": new_params
        }
        config["widgets"].append(new_widget)
        save_config(config)
        st.success(f"Widget {new_widget_id} agregado con éxito")
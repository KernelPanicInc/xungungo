import streamlit as st

def add_widget(widgets):
    """
    Lógica para añadir un widget a la configuración del dashboard.
    """
    st.write("Selecciona el tipo de widget y configura sus parámetros:")

    # Seleccionar widget
    widget_options = {widget.__name__: widget for widget in widgets}
    widget_name = st.selectbox("Selecciona un widget", list(widget_options.keys()))
    selected_widget = widget_options[widget_name]()

    # Configuración de parámetros del widget
    st.write("Configura los parámetros del widget:")
    selected_widget.render_form()

    # Guardar el widget en la configuración
    st.write("Widget configurado correctamente.")
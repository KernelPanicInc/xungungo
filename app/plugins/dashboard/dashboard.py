import streamlit as st
import plugins.dashboard.render_dashboard as render_dashboard
import plugins.dashboard.render_config as render_config

def render():
    """
    Modo único con un solo botón en la barra lateral que alterna entre:
      - Modo 'dashboard'
      - Modo 'config'
    Se utiliza st.rerun() para forzar la recarga inmediata de la app.
    """

    # Inicializa el modo del dashboard en 'dashboard' si no está definido
    if "dashboard_mode" not in st.session_state:
        st.session_state.dashboard_mode = "dashboard"

    # Decide la etiqueta del botón según el modo actual
    if st.session_state.dashboard_mode == "dashboard":
        button_label = "Configurar Dashboard"
    else:
        button_label = "Volver al Dashboard"

    # Botón en la barra lateral para alternar el modo
    if st.sidebar.button(button_label):
        if st.session_state.dashboard_mode == "dashboard":
            st.session_state.dashboard_mode = "config"
        else:
            st.session_state.dashboard_mode = "dashboard"
        
        # Forzamos recarga inmediata para que cambie el texto del botón
        st.rerun()

    # Renderizar la vista correspondiente
    if st.session_state.dashboard_mode == "config":
        render_config.render()
    else:
        render_dashboard.render()

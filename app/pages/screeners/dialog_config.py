import streamlit as st

@st.dialog("Configuración de Screeners")
def render_dialog(plugin, screener_config, config_manager):
    with st.form("config_form"):
        # Campo genérico: Nombre del screener
        nuevo_nombre = st.text_input("Nombre", value=screener_config.get("nombre", ""), key="nombre_screener")
        screener_config["nombre"] = nuevo_nombre

        # Invocar el render de configuración específico del plugin.
        # Se espera que este método actualice el diccionario `screener_config` según los campos propios.
        plugin["module"].render_config(screener_config)

        submitted = st.form_submit_button("Guardar cambios")
        if submitted:
            # Se guarda la configuración actualizada en el archivo YAML
            config_manager.save()
            st.success("¡Cambios guardados!")

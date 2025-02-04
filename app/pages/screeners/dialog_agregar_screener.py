import streamlit as st
from utils.plugins import obtener_plugins

@st.dialog("Agregar nuevo Screener")
def render_dialog_agregar_screener(config_manager):
    # 1. Obtener la lista completa de plugins disponibles
    plugins = obtener_plugins("screeners")
    
    # 2. Construir una lista segura para el selectbox (sin incluir objetos no pickleables)
    safe_plugins = [
        {"nombre": plugin["nombre"], "tipo": plugin["tipo"]}
        for plugin in plugins
    ]
    
    # 3. Seleccionar el plugin usando el selectbox; se mostrará el nombre pero se usará el "tipo"
    selected_safe_plugin = st.selectbox(
        "Tipo de Screener",
        safe_plugins,
        format_func=lambda p: p["nombre"],
        key="nuevo_plugin"
    )
    # Extraemos el tipo seleccionado
    nuevo_tipo = selected_safe_plugin["tipo"]
    
    # 4. Dentro del formulario se solicitan los demás datos.
    with st.form("form_nuevo_screener"):
        nuevo_screener = {}
        nuevo_screener["tipo"] = nuevo_tipo
        nuevo_screener["nombre"] = st.text_input("Nombre del Screener", key="nuevo_nombre")
        nuevo_screener["descripcion"] = st.text_area("Descripción del Screener", key="nuevo_descripcion")
        
        # Buscar el plugin según el tipo seleccionado y renderizar su configuración
        plugin = next((p for p in plugins if p["tipo"] == nuevo_tipo), None)
        if plugin and hasattr(plugin["module"], "render_config"):
            plugin["module"].render_config(nuevo_screener)
        
        submitted = st.form_submit_button("Agregar Screener")
        if submitted:
            # Se agrega el nuevo screener a la configuración y se guarda en el archivo YAML
            if "screener" not in config_manager.config_data:
                config_manager.config_data["screener"] = []
            config_manager.config_data["screener"].append(nuevo_screener)
            config_manager.save()
            st.success("¡Screener agregado correctamente!")
            st.rerun()

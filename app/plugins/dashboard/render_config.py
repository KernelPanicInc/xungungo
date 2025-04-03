import streamlit as st
from utils.config_manager import ConfigManager
from utils.plugins import obtener_plugins

def render():
    """
    Renderiza la pantalla de configuración del Dashboard.
    """
    st.title("Configuración del Dashboard")
    config_path = "config.yaml"
    config_manager = ConfigManager(config_path)

    # Sección de widgets en el YAML
    widgets_config = config_manager.get("dashboard.widget", {})

    st.subheader("Widgets existentes")
    if not widgets_config:
        st.write("No hay widgets configurados todavía.")
    else:
        # Mostramos cada widget en tres columnas para organizar mejor la UI
        for widget_name, widget_conf in widgets_config.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{widget_name}**")
                st.caption(f"Tipo: `{widget_conf.get('type', 'N/D')}`")
            
            with col2:
                # Botón que abre el diálogo de configuración
                if st.button("Configurar", key=f"btn_config_{widget_name}"):
                    configure_widget_dialog(config_manager, widget_name, widget_conf)
            
            with col3:
                # Botón para eliminar el widget
                if st.button("Eliminar", key=f"btn_delete_{widget_name}"):
                    delete_widget(config_manager, widget_name)

    st.markdown("---")
    # Botón para agregar un nuevo widget
    st.write("Agregar un nuevo widget")
    if st.button("Nuevo Widget"):
        add_widget_dialog(config_manager, list(widgets_config.keys()))

def delete_widget(config_manager: ConfigManager, widget_name: str):
    """
    Elimina el widget 'widget_name' del archivo YAML y refresca la página.
    """
    widget_section = config_manager.config_data.setdefault("dashboard", {}).setdefault("widget", {})
    if widget_name in widget_section:
        del widget_section[widget_name]
        config_manager.save()
        st.warning(f"Se eliminó el widget '{widget_name}'.")
        st.rerun()  # Recarga la pantalla
    else:
        st.info("El widget ya no existe.")

@st.dialog("Configurar Widget")
def configure_widget_dialog(config_manager: ConfigManager, widget_name: str, widget_conf: dict):
    """
    Diálogo que:
      1. Busca el plugin correspondiente a 'widget_conf["type"]'.
      2. Llama a la función config() del plugin, que retorna un dict con la nueva configuración.
      3. Ofrece un botón "Guardar Cambios" para actualizar el YAML.
    """
    st.markdown(f"### Configurando Widget: {widget_name}")

    widget_type = widget_conf.get("type", "")
    if not widget_type: 
        st.error("Este widget no tiene 'type'.")
        return

    # Buscar el plugin en la carpeta 'dashboard' (ajusta si tus plugins están en otra subcarpeta)
    plugins = obtener_plugins("dashboard")
    plugin = next((p for p in plugins if p["tipo"] == widget_type), None)
    if plugin is None:
        st.error(f"No se encontró un plugin para el tipo '{widget_type}'.")
        return

    # Verificar si el plugin tiene una función 'config'
    if not hasattr(plugin["module"], "config"):
        st.error(f"El plugin '{plugin['nombre']}' no tiene una función 'config'.")
        return

    st.write("**Configuración específica del plugin:**")
    # Llamamos a la función config() del plugin, que MUESTRA inputs y RETORNA un dict final
    nueva_config = plugin["module"].config(widget_conf)

    # Botón para guardar directamente la config devuelta por el plugin
    if st.button("Guardar Cambios"):
        if not isinstance(nueva_config, dict):
            st.error("El plugin no devolvió una configuración válida.")
            return

        # Aseguramos que se mantenga el 'type'
        nueva_config["type"] = widget_type

        # Guardar la nueva configuración en el YAML
        dashboard_widget = config_manager.config_data.setdefault("dashboard", {}).setdefault("widget", {})
        dashboard_widget[widget_name] = nueva_config
        config_manager.save()
        
        st.success("Configuración guardada correctamente.")
        st.rerun()  # Cierra el diálogo y refresca la vista

@st.dialog("Agregar un nuevo widget")
def add_widget_dialog(config_manager: ConfigManager, existing_names: list):
    """
    Diálogo para agregar un nuevo widget.
    Se muestra un selectbox con los plugins disponibles y, según la selección,
    se renderiza la configuración específica del plugin. Los cambios se guardan directamente en el YAML.
    """
    st.write("Completa la información del widget:")

    # Ingresar el nombre del widget
    widget_name = st.text_input("Nombre del Widget", value="")

    # Obtener la lista de plugins disponibles desde la carpeta 'dashboard'
    plugins = obtener_plugins("dashboard")
    if not plugins:
        st.error("No hay plugins disponibles.")
        return

    # Crear una lista de opciones con el 'tipo' de cada plugin,
    # pero usando un formateador para mostrar el 'nombre' del plugin.
    plugin_types = [p["tipo"] for p in plugins]
    selected_plugin_type = st.selectbox(
        "Selecciona el Plugin",
        options=plugin_types,
        format_func=lambda t: next(p["nombre"] for p in plugins if p["tipo"] == t)
    )

    # Buscar el plugin seleccionado
    selected_plugin = next(p for p in plugins if p["tipo"] == selected_plugin_type)

    st.write("### Configuración del Plugin")
    # Llama a la función config() del plugin con un diccionario vacío (para un nuevo widget)
    new_config = selected_plugin["module"].config({})

    # Botón para guardar la configuración del nuevo widget
    if st.button("Guardar Nuevo Widget"):
        if not widget_name:
            st.error("Debes proporcionar un nombre para el widget.")
            return
        if widget_name in existing_names:
            st.error(f"Ya existe un widget con el nombre '{widget_name}'.")
            return
        if not isinstance(new_config, dict):
            st.error("La configuración del plugin no es válida.")
            return

        # Aseguramos que se mantenga el tipo del plugin
        new_config["type"] = selected_plugin_type

        # Guardar la nueva configuración en el YAML
        config_manager.config_data.setdefault("dashboard", {}).setdefault("widget", {})[widget_name] = new_config
        config_manager.save()

        st.success(f"Se agregó el nuevo widget: '{widget_name}'.")
        st.rerun()  # Recarga la vista para mostrar los cambios


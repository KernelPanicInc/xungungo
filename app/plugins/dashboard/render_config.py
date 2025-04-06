import streamlit as st
from utils.config_manager import ConfigManager
from utils.plugins import obtener_plugins

def get_ordered_widgets(config_manager: ConfigManager):
    """
    Retorna una lista de tuplas (widget_name, widget_conf) ordenada según el valor de 'position'.
    Si algún widget no tiene 'position', se le asigna un valor por defecto según su orden de inserción.
    """
    widget_section = config_manager.config_data.setdefault("dashboard", {}).setdefault("widget", {})
    # Asignar posición por defecto si no existe
    for i, (wname, wconf) in enumerate(widget_section.items()):
        if "position" not in wconf:
            wconf["position"] = i
    # Ordenar los widgets por 'position'
    ordered = sorted(widget_section.items(), key=lambda x: x[1].get("position", 0))
    return ordered

def move_widget(config_manager: ConfigManager, widget_name: str, direction: str):
    """
    Cambia la posición de un widget en la lista, moviéndolo hacia arriba o abajo.
    direction: 'up' o 'down'
    """
    widgets = get_ordered_widgets(config_manager)
    names = [w[0] for w in widgets]
    try:
        index = names.index(widget_name)
    except ValueError:
        st.error("Widget no encontrado.")
        return

    if direction == "up":
        if index == 0:
            st.info("El widget ya está en la posición superior.")
            return
        # Intercambiar posición con el anterior
        prev_name, prev_conf = widgets[index - 1]
        curr_conf = widgets[index][1]
        prev_pos = prev_conf.get("position", index - 1)
        curr_pos = curr_conf.get("position", index)
        prev_conf["position"], curr_conf["position"] = curr_pos, prev_pos
    elif direction == "down":
        if index == len(widgets) - 1:
            st.info("El widget ya está en la posición inferior.")
            return
        # Intercambiar posición con el siguiente
        next_name, next_conf = widgets[index + 1]
        curr_conf = widgets[index][1]
        next_pos = next_conf.get("position", index + 1)
        curr_pos = curr_conf.get("position", index)
        next_conf["position"], curr_conf["position"] = curr_pos, next_pos
    else:
        st.error("Dirección no válida.")

    config_manager.save()
    st.rerun()

def render():
    """
    Renderiza la pantalla de configuración del Dashboard, permitiendo
    listar, configurar, eliminar y reordenar los widgets.
    """
    st.title("Configuración del Dashboard")
    config_path = "config.yaml"
    config_manager = ConfigManager(config_path)

    # Obtener la lista ordenada de widgets
    ordered_widgets = get_ordered_widgets(config_manager)

    st.subheader("Widgets existentes")
    if not ordered_widgets:
        st.write("No hay widgets configurados todavía.")
    else:
        for widget_name, widget_conf in ordered_widgets:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.markdown(f"**{widget_name}**")
                st.caption(f"Tipo: `{widget_conf.get('type', 'N/D')}`")
                st.caption(f"Posición: {widget_conf.get('position', 0)}")
            with col2:
                if st.button("Configurar", key=f"btn_config_{widget_name}"):
                    configure_widget_dialog(config_manager, widget_name, widget_conf)
            with col3:
                if st.button("Eliminar", key=f"btn_delete_{widget_name}"):
                    delete_widget(config_manager, widget_name)
            with col4:
                if st.button("↑", key=f"btn_up_{widget_name}"):
                    move_widget(config_manager, widget_name, "up")
            with col5:
                if st.button("↓", key=f"btn_down_{widget_name}"):
                    move_widget(config_manager, widget_name, "down")

    st.markdown("---")
    st.write("Agregar un nuevo widget")
    if st.button("Nuevo Widget"):
        add_widget_dialog(config_manager, list([w[0] for w in ordered_widgets]))

def delete_widget(config_manager: ConfigManager, widget_name: str):
    """
    Elimina el widget 'widget_name' del YAML y refresca la página.
    """
    widget_section = config_manager.config_data.setdefault("dashboard", {}).setdefault("widget", {})
    if widget_name in widget_section:
        del widget_section[widget_name]
        config_manager.save()
        st.warning(f"Se eliminó el widget '{widget_name}'.")
        st.rerun()
    else:
        st.info("El widget ya no existe.")

@st.dialog("Configurar Widget")
def configure_widget_dialog(config_manager: ConfigManager, widget_name: str, widget_conf: dict):
    st.markdown(f"### Configurando Widget: {widget_name}")

    widget_type = widget_conf.get("type", "")
    if not widget_type:
        st.error("Este widget no tiene 'type'.")
        return

    plugins = obtener_plugins("dashboard")
    plugin = next((p for p in plugins if p["tipo"] == widget_type), None)
    if plugin is None:
        st.error(f"No se encontró un plugin para el tipo '{widget_type}'.")
        return

    if not hasattr(plugin["module"], "config"):
        st.error(f"El plugin '{plugin['nombre']}' no tiene una función 'config'.")
        return

    st.write("**Configuración específica del plugin:**")
    # Llamamos a la función config() del plugin, que MUESTRA inputs y RETORNA un dict final
    nueva_config = plugin["module"].config(widget_conf)

    if st.button("Guardar Cambios"):
        if not isinstance(nueva_config, dict):
            st.error("El plugin no devolvió una configuración válida.")
            return

        # Aseguramos que se mantenga el 'type'
        nueva_config["type"] = widget_type
        # Preservamos el valor de "position" del widget original
        if "position" in widget_conf:
            nueva_config["position"] = widget_conf["position"]

        dashboard_widget = config_manager.config_data.setdefault("dashboard", {}).setdefault("widget", {})
        dashboard_widget[widget_name] = nueva_config
        config_manager.save()

        st.success("Configuración guardada correctamente.")
        st.rerun()

@st.dialog("Agregar un nuevo widget")
def add_widget_dialog(config_manager: ConfigManager, existing_names: list):
    st.write("Completa la información del widget:")

    widget_name = st.text_input("Nombre del Widget", value="")

    plugins = obtener_plugins("dashboard")
    if not plugins:
        st.error("No hay plugins disponibles.")
        return

    plugin_types = [p["tipo"] for p in plugins]
    selected_plugin_type = st.selectbox(
        "Selecciona el Plugin",
        options=plugin_types,
        format_func=lambda t: next(p["nombre"] for p in plugins if p["tipo"] == t)
    )

    selected_plugin = next(p for p in plugins if p["tipo"] == selected_plugin_type)

    st.write("### Configuración del Plugin")
    new_config = selected_plugin["module"].config({})

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

        new_config["type"] = selected_plugin_type
        # Asignar una posición nueva: al final de la lista (usamos la longitud actual)
        ordered = get_ordered_widgets(config_manager)
        new_config["position"] = len(ordered)
        config_manager.config_data.setdefault("dashboard", {}).setdefault("widget", {})[widget_name] = new_config
        config_manager.save()
        st.success(f"Se agregó el nuevo widget: '{widget_name}'.")
        st.rerun()

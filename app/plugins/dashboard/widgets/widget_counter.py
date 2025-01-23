import streamlit as st
from plugins.dashboard.widgets.widget_base import WidgetBase
import random

class CounterWidget(WidgetBase):
    def __init__(self, widget_id: str, params: dict):
        self.widget_id = widget_id
        
        # Parámetros configurables
        self.start_value = params.get('start_value', 0)
        self.increment = params.get('increment', 1)
        
        # Inicializamos el estado del contador en session_state
        if f"{self.widget_id}_value" not in st.session_state:
            st.session_state[f"{self.widget_id}_value"] = self.start_value

    def render(self):
        st.write(f"**CounterWidget (ID: {self.widget_id})**")

        # Botón para incrementar, con un key único
        if st.button("Incrementar", key=f"increment_button_{self.widget_id}"):
            st.session_state[f"{self.widget_id}_value"] += self.increment
        
        # Mostramos el valor actual del contador
        st.write(f"Valor actual: {st.session_state[f'{self.widget_id}_value']}")
        st.write(f"Incremento: {self.increment}")
        
        # Mostramos un número aleatorio para verificar cambios dinámicos
        random_number = random.randint(1, 100)
        st.write(f"Número aleatorio: {random_number}")

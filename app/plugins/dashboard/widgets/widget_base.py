# widgets/widget_base.py
from abc import ABC, abstractmethod

class WidgetBase(ABC):
    """
    Clase base que define la interfaz mínima que un widget debe implementar.
    """

    @abstractmethod
    def __init__(self, widget_id: str, params: dict):
        """
        :param widget_id: identificador único del widget.
        :param params: diccionario con parámetros de configuración.
        """
        pass

    @abstractmethod
    def render(self):
        """
        Lógica para renderizar el widget en Streamlit.
        """
        pass

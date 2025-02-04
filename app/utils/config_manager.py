import yaml
from typing import Any

class ConfigManager:
    _instance = None
    
    def __new__(cls, config_path: str):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.config_path = config_path
            cls._instance.config_data = cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> dict:
        """
        Carga la configuración desde el archivo YAML.
        :return: Diccionario con la configuración.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Archivo de configuración no encontrado: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error al leer el archivo YAML: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la configuración.
        :param key: Clave a buscar en la configuración.
        :param default: Valor por defecto si la clave no existe.
        :return: Valor correspondiente a la clave o el valor por defecto.
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            elif isinstance(value, list) and k.isdigit():
                index = int(k)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    return default
            else:
                return default
        return value
    
    def reload(self):
        """
        Recarga la configuración desde el archivo YAML.
        """
        self.config_data = self._load_config()
    
    def save(self) -> None:
        """
        Guarda la configuración en el archivo YAML.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(self.config_data, file, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"Error al guardar el archivo de configuración: {e}")
    
    def __repr__(self):
        return f"ConfigManager({self.config_path})"

import yaml
from pathlib import Path

class YamlConfigManager:
    def __init__(self, config_file):
        """
        Inicializa el gestor de configuraciones.
        :param config_file: Ruta al archivo YAML.
        """
        self.config_file = Path(config_file)
        if not self.config_file.exists():
            # Si el archivo no existe, crearlo vacío
            self.config_file.write_text(yaml.dump({}))

    def get(self, key, default=None):
        """
        Obtiene un valor del archivo YAML basado en una clave.
        :param key: Clave en formato de punto (e.g., "app.title").
        :param default: Valor por defecto si la clave no existe.
        :return: Valor correspondiente o el valor por defecto.
        """
        config = self._read_yaml()
        keys = key.split(".")
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
        return config

    def set(self, key, value):
        """
        Establece un valor en el archivo YAML.
        :param key: Clave en formato de punto (e.g., "app.title").
        :param value: Valor a establecer.
        """
        config = self._read_yaml()
        keys = key.split(".")
        d = config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self._write_yaml(config)

    def _read_yaml(self):
        """
        Lee el archivo YAML.
        :return: Diccionario con los datos del YAML.
        """
        with self.config_file.open("r") as file:
            return yaml.safe_load(file) or {}

    def _write_yaml(self, data):
        """
        Escribe datos al archivo YAML.
        :param data: Diccionario con los datos a guardar.
        """
        with self.config_file.open("w") as file:
            yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)

    def delete(self, key):
        """
        Elimina una clave del archivo YAML.
        :param key: Clave en formato de punto (e.g., "app.title").
        """
        config = self._read_yaml()
        keys = key.split(".")
        d = config
        for k in keys[:-1]:
            if k in d and isinstance(d[k], dict):
                d = d[k]
            else:
                return  # La clave no existe
        d.pop(keys[-1], None)
        self._write_yaml(config)

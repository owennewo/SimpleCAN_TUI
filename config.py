import yaml
from dataclasses import dataclass
from dacite import from_dict
from typing import Dict, Any


@dataclass
class CanField:
    name: str
    description: str
    value: Any = None
    datatype: str = "raw"

    def values(self):
        return (self.name, self.description, self.value, self.datatype)


@dataclass
class CanModule:
    name: str
    # description: str
    fields: Dict[int, CanField]


@dataclass
class Config:
    connection: Dict
    modules: Dict[int, CanModule]


def load_config_from_yaml(path="config.yaml") -> Config:
    with open(path, "r") as file:
        yaml_data = yaml.safe_load(file)
    config = from_dict(data_class=Config, data=yaml_data)
    return config

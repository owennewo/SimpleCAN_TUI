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
class CanDevice:
    name: str


@dataclass
class CanModule:
    name: str
    fields: Dict[int, CanField]


@dataclass
class Config:
    connection: Dict
    devices: Dict[int, CanDevice]
    modules: Dict[int, CanModule]


def load_config_from_yaml(path="config/config.yaml") -> Config:
    with open(path, "r") as file:
        yaml_data = yaml.safe_load(file)
    config = from_dict(data_class=Config, data=yaml_data)
    return config

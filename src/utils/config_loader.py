import json
import os
from typing import Any, Dict


class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_data: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        # check if the config file exists
        if not os.path.isfile(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        with open(self.config_path, 'r') as file:
            try:
                # load json data from the file
                self.config_data = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON: {e}")

        return self.config_data

    def get(self, key: str, default: Any = None) -> Any:
        # return the value for the given key, or default if it doesn't exist
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        # set the value for the given key
        self.config_data[key] = value

    def save(self) -> None:
        # save the current config data back to the file
        with open(self.config_path, 'w') as file:
            json.dump(self.config_data, file, indent=4)

# TODO: consider adding validation for config keys and types
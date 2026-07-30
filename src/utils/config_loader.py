import json
import os

class ConfigLoader:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file {self.config_file} not found")
        
        with open(self.config_file, 'r') as file:
            try:
                self.config_data = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing JSON in config file: {e}")

    def get(self, key: str, default=None):
        return self.config_data.get(key, default)

    def set(self, key: str, value):
        self.config_data[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config_data, file, indent=4)

# example usage
if __name__ == "__main__":
    config = ConfigLoader('config.json')
    print(config.get('some_key', 'default_value'))  # change 'some_key' to your actual key
    # TODO: add better handling for empty or missing keys
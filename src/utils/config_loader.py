import json
import os

class ConfigLoader:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            try:
                self.config_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing JSON: {e}")

    def get(self, key: str, default=None):
        return self.config_data.get(key, default)

    def set(self, key: str, value):
        self.config_data[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f, indent=4)

# example usage
if __name__ == "__main__":
    config_loader = ConfigLoader('config.json')
    print(config_loader.get('some_key', 'default_value'))  # just testing

    # TODO: implement better error handling and logging here
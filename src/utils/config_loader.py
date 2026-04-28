import json
import os

class ConfigLoader:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = {}

    def load(self) -> dict:
        # check if the file exists
        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(f"Config file {self.config_file} not found")
        
        # load the json config file
        with open(self.config_file, 'r') as file:
            self.config_data = json.load(file)
        
        return self.config_data

    def get(self, key: str, default=None):
        # get a specific key from the config
        return self.config_data.get(key, default)

    def set(self, key: str, value):
        # set a value in the config and save it
        self.config_data[key] = value
        self.save()

    def save(self):
        # save the current config data back to the file
        with open(self.config_file, 'w') as file:
            json.dump(self.config_data, file, indent=4)

# TODO: add validation for config keys and types if needed

# example usage
if __name__ == "__main__":
    config_loader = ConfigLoader('config.json')
    config = config_loader.load()
    print(f"Loaded config: {config}")
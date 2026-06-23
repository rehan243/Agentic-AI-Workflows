import json
import os

class ConfigLoader:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = {}
        self.load_config()

    def load_config(self):
        # check if the config file exists
        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        # load json data
        with open(self.config_file, 'r') as file:
            try:
                self.config_data = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON from config file: {e}")

    def get(self, key: str, default=None):
        # return the value for the given key or a default if not found
        return self.config_data.get(key, default)

    def set(self, key: str, value):
        # set a new key-value pair in the config data
        self.config_data[key] = value
        # TODO: consider saving changes back to the file

    def save(self):
        # save the current config data back to the json file
        with open(self.config_file, 'w') as file:
            json.dump(self.config_data, file, indent=4)

# example usage
if __name__ == "__main__":
    config_loader = ConfigLoader('config.json')
    print(config_loader.get('some_key', 'default_value'))  # adjust based on your config file
    config_loader.set('new_key', 'new_value')
    config_loader.save()  # save changes if needed
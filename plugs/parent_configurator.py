import json


class ParentConfigurator:

    def __init__(self, config_file=None):
        self.config_file = config_file
        with open(config_file) as conf_file:
            self.config = json.load(conf_file)

    def check_field_exist_in_config_or_ask(self, field_name: str, default_value=None):
        if field_name not in self.config:
            user_input = input(f"Please provide a value for {field_name} (default: {default_value}): ")
            if user_input.strip() == "":
                self.config[field_name] = default_value
            else:
                self.config[field_name] = user_input
        return self.config[field_name]

    def save_config_in_file(self):
        with open(self.config_file, 'w') as conf_file:
            json.dump(self.config, conf_file, indent=4)
        print(f"Configuration saved to {self.config_file}")
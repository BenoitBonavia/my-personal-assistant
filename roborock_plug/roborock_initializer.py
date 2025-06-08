import json
import os.path
from .roborock_manager import RoborockManager


class RoborockInitializer:
    """
    This class is used to initialize the test configuration if not done yet
    """
    def __init__(self, config_file='roborock_plug/roborock_configuration.json'):
        self.config_file = config_file
        if not os.path.exists(config_file):
            print(f"The configuration file for test doesn't exist")
            return

        with open(config_file) as config_file:
            self.config = json.load(config_file)
            self.roborock_manager = RoborockManager()

    def initialize(self):
        if self.config.get('initialized', False):
            print("Roborock initialized")
            return

        devices = self.roborock_manager.list_devices()

        if len(devices) == 0:
            print("No devices found")
            return

        for device in devices:
            device_id = device['id']
            device_default_name = device['default_name']
            new_device_name = input(f"Enter a new name for the device {device_default_name}: ")
            if 'devices' not in self.config:
                self.config['devices'] = []
            self.config['devices'].append({"id": device_id, "default_name": device_default_name, "name": new_device_name})

        self.config['initialized'] = True

        with open(self.config_file, "w") as file:
            json.dump(self.config, file, indent=4)


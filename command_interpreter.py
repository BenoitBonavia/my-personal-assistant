import json

from hue_plug.hue_manager import HueManager

class CommandInterpreter:
    def __init__(self, configuration):
        self.configuration = configuration

    def handle_command(self, command):
        manager_name = command['manager_name']
        available_managers = self.configuration['available_managers']
        if manager_name not in available_managers:
            print(f"Manager {manager_name} is not available")
            return
        if manager_name == 'hue':
            hue_manager = HueManager()
            hue_manager.handle_command(command)

    def handle_request(self, command_as_json):
        for command in command_as_json:
            self.handle_command(command)






from plugs.home_assistant_plug.home_assistant_manager import HomeAssistantManager
from plugs.hue_plug import HueManager
from plugs.roborock_plug.roborock_manager import RoborockManager

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
        elif manager_name == 'home_assistant':
            home_assistant_manager = HomeAssistantManager()
            home_assistant_manager.handle_command(command)
        elif manager_name == 'roborock':
            roborock_manager = RoborockManager()
            roborock_manager.handle_command(command)

    def handle_request(self, command_as_json):
        for command in command_as_json:
            self.handle_command(command)






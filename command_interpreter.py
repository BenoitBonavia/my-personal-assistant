import logging
from plugs.home_assistant_plug.home_assistant_manager import HomeAssistantManager
from plugs.hue_plug import HueManager
from plugs.roborock_plug.roborock_manager import RoborockManager

logger = logging.getLogger(__name__)

class CommandInterpreter:
    def __init__(self, configuration):
        self.configuration = configuration
        available_managers = self.configuration.get('available_managers', [])
        self.hue_manager = HueManager() if 'hue' in available_managers else None
        self.home_assistant_manager = HomeAssistantManager() if 'home_assistant' in available_managers else None
        self.roborock_manager = RoborockManager() if 'roborock' in available_managers else None

    def handle_command(self, command):
        manager_name = command['manager_name']
        available_managers = self.configuration['available_managers']
        if manager_name not in available_managers:
            logger.error("Manager %s is not available", manager_name)
            return
        if manager_name == 'hue' and self.hue_manager:
            self.hue_manager.handle_command(command)
        elif manager_name == 'home_assistant' and self.home_assistant_manager:
            self.home_assistant_manager.handle_command(command)
        elif manager_name == 'roborock' and self.roborock_manager:
            self.roborock_manager.handle_command(command)

    def handle_request(self, command_as_json):
        for command in command_as_json:
            self.handle_command(command)






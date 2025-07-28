import logging

logger = logging.getLogger(__name__)

class ParentManager:
    def __init__(self):
        self.manager_name = "Parent"

    def handle_command(self, command):
        command_name = command['command_name']
        params = command.get('params', [])
        logger.info("Executing command: %s with params: %s", command_name, params)
        try:
            method_to_call = getattr(self, command_name)
            method_to_call(*params)
        except AttributeError:
            logger.error("%s manager has no method named %s", self.manager_name, command_name)
        except TypeError:
            logger.error("%s throw an error because params passed to %s don't fit with the function signature", self.manager_name, command_name)
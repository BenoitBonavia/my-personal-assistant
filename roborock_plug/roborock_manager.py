import json

try:
    from miio import RoborockVacuum
except ImportError:  # pragma: no cover - library might not be available during tests
    RoborockVacuum = None


class RoborockManager:
    """
    Manager used to control a Roborock S7 vacuum cleaner.
    """

    def __init__(self, config_file='roborock_plug/roborock_configuration.json'):
        with open(config_file) as conf_file:
            self.config = json.load(conf_file)
            self.ip = self.config.get('ip')
            self.token = self.config.get('token')
        if RoborockVacuum is not None:
            self.vacuum = RoborockVacuum(self.ip, self.token)
        else:
            self.vacuum = None

    def finish_cleaning(self):
        """
        Stop the current cleaning cycle and return the vacuum to its dock.
        """
        self.vacuum.home()

    def clean_entire_house(self):
        """
        Start a full house cleaning cycle.
        """
        self.vacuum.start()

    def clean_room(self, rooms_id: list[int]):
        """
        Clean a specific room using its numeric identifier.
        """
        self.vacuum.segment_clean(rooms_id)

    def handle_command(self, command):
        command_name = command['command_name']
        params = command['params']
        print("EXECUTE COMMAND:", command_name, params)
        try:
            method_to_call = getattr(self, command_name)
            method_to_call(*params)
        except AttributeError:
            print(f"Command {command_name} is not available in RoborockManager or have wrong params")
        except Exception:
            print(f"An error occurred while executing command {command_name} with params {params}")

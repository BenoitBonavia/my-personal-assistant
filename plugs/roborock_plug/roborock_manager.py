import json

from plugs.parent_manager import ParentManager

try:
    from miio import RoborockVacuum
except ImportError:  # pragma: no cover - library might not be available during tests
    RoborockVacuum = None


class RoborockManager(ParentManager):
    """
    Manager used to control a Roborock S7 vacuum cleaner.
    """

    def __init__(self, config_file='plugs/roborock_plug/roborock_configuration.json'):
        super().__init__()
        self.manager_name = "roborock"
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

    def clean_room(self, rooms_id: list[int], number_of_cleaning: int = 1):
        """
        Clean specific rooms by their IDs, repeat the cleaning the number_of_cleaning specified times.
        """
        self.vacuum.segment_clean(rooms_id, number_of_cleaning)
import json

from miio import RoborockVacuum

from plugs.parent_configurator import ParentConfigurator


class RoborockConfigurator(ParentConfigurator):

    def __init__(self, config_file='plugs/roborock_plug/roborock_configuration.json'):
        super().__init__(config_file)
        self.check_field_exist_in_config_or_ask('ip')
        self.check_field_exist_in_config_or_ask('token')
        self.ip = self.config.get('ip')
        self.token = self.config.get('token')
        if RoborockVacuum is not None:
            self.vacuum = RoborockVacuum(self.ip, self.token)
        else:
            self.vacuum = None

    def get_rooms_available(self):
        """
        Get the list of rooms available in the Roborock vacuum cleaner.
        """
        if self.vacuum is not None:
            maps = self.vacuum.get_room_mapping()
            for idx, map_obj in enumerate(maps.map_list):
                print(map_obj)
        else:
            raise ImportError("RoborockVacuum is not available. Please install the miio library.")

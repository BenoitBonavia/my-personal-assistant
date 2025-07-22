from phue import Bridge
import json
import logging

from plugs.hue_plug.hue_configuration_type import HueConfigurationType, HueLightConfigurationType
from plugs.parent_manager import ParentManager

logger = logging.getLogger(__name__)


class HueManager(ParentManager):
    """
    This class is used to manage the lights of the house through the Hue Bridge
    """

    def __init__(self, config_file='plugs/hue_plug/hue_configuration.json'):
        super().__init__()
        self.manager_name = "hue"
        with open(config_file) as config_file:
            data = json.load(config_file)
            self.config = HueConfigurationType(**data)
            self.bridge = Bridge(self.config.bridge_ip)
            self.bridge.connect()

    @staticmethod
    def __handle_lights_indexes(lights_indexes: list[int]):
        """
        Handle the case where a single index is provided as an int instead of a list
        """
        if isinstance(lights_indexes, int):
            lights_indexes = [lights_indexes]
        return list(map(int, lights_indexes))

    def get_lights(self):
        """ Get list of lights connected to the Hue Bridge """
        available_lights = self.bridge.lights
        logger.info(available_lights)
        return available_lights

    def get_light(self, light_index: int):
        """
        Get a specific light connected to the Hue Bridge by its index
        """
        light_index = int(light_index)
        light = self.bridge.get_light(light_index)
        logger.info(light)
        return light

    def turn_on_lights(self, lights_indexes: list[int]):
        """
        Turn on lights with the specified indexes

        Parameters:
        lights_indexes (int list): List of indexes of lights to turn on
        """
        lights_indexes = self.__handle_lights_indexes(lights_indexes)
        self.bridge.set_light(lights_indexes, 'on', True)

    def turn_off_lights(self, lights_indexes: list[int]):
        """
        Turn off lights with the specified indexes

        Parameters:
        lights_indexes (int list): List of indexes of lights to turn off, it is required. To turn off all the lights, use all the ids
        """
        lights_indexes = self.__handle_lights_indexes(lights_indexes)
        self.bridge.set_light(lights_indexes, 'on', False)

    def set_lights_brightness(self, lights_indexes: list[int], brightness):
        """
        Set brightness of lights with the specified indexes

        Parameters:
        light_index (int list): List of indexes of lights to set brightness
        brightness (int): Brightness value to set (0-254)
        """
        lights_indexes = self.__handle_lights_indexes(lights_indexes)
        try:
            for index in lights_indexes:
                self.bridge.set_light(index, 'bri', brightness)
        except Exception:
            logger.exception("Error while setting brightness of lights %s", lights_indexes)

    def increase_brightness(self, lights_indexes: list[int], increase_percentage):
        """
        Increase brightness of lights with the specified indexes

        Parameters:
        lights_indexes (int list): List of index of all the lights to increase brightness
        increase_percentage (int): Percentage to increase brightness
        """
        lights_indexes = self.__handle_lights_indexes(lights_indexes)
        inc = int(increase_percentage / 100 * 254)
        try:
            self.bridge.set_light(lights_indexes, 'bri_inc', inc)
        except Exception:
            logger.exception("Error while increasing brightness of light %s", lights_indexes)

    def decrease_lights_brightness(self, lights_indexes: list[int], decrease_percentage):
        """
        Decrease brightness of lights with the specified indexes

        Parameters:
        lights_indexes (int list): List of index of all the lights to decrease brightness
        decrease_percentage (int): Percentage to decrease brightness
        """
        lights_indexes = self.__handle_lights_indexes(lights_indexes)
        inc = -int(decrease_percentage / 100 * 254)
        try:
            self.bridge.set_light(lights_indexes, 'bri_inc', inc)
        except Exception:
            logger.exception("Error while decreasing brightness of light %s", lights_indexes)

    def scan_hue_devices_not_configured(self):
        """
        Scan hue devices and compare the id list to the ids configured in the hue_manager configuration
        """
        configured_lights_ids = [light.id for light in self.config.hue_lights]

        all_lights = self.bridge.get_light_objects('id')  # dict {id: Light}

        for light_id, light in all_lights.items():
            if str(light_id) not in configured_lights_ids:
                print(f'Unconfigured light: {light_id} with name : {light.name}')


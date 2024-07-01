from phue import Bridge
import json


class HueManager:
    def __init__(self, config_file='hue/hue_configuration.json'):
        with open(config_file) as config_file:
            self.config = json.load(config_file)
            self.bridge = Bridge(self.config['bridge_ip'])
            self.bridge.connect()

    def get_lights(self):
        """ Get list of lights connected to the Hue Bridge """
        return self.bridge.lights

    def turn_on_lights(self, lights_indexes):
        lights_indexes = list(map(int, lights_indexes))
        self.bridge.set_light(lights_indexes, 'on', True)

    def turn_off_lights(self, lights_indexes):
        lights_indexes = list(map(int, lights_indexes))
        self.bridge.set_light(lights_indexes, 'on', False)

    def turn_on_light(self, light_index):
        if light_index is str:
            light_index = int(light_index)
        self.bridge.set_light(light_index, 'on', True)

    def turn_off_light(self, light_index):
        if light_index is str:
            light_index = int(light_index)
        self.bridge.set_light(light_index, 'on', False)

    def handle_command(self, command):
        command_name = command['command_name']
        params = command['params']
        print("EXECUTE COMMAND : ", command_name, params)
        if command_name == 'turn_on_lights':
            self.turn_on_lights(params)
        elif command_name == 'turn_off_lights':
            self.turn_off_lights(params)
        elif command_name == 'turn_on_light':
            self.turn_on_light(params[0])
        elif command_name == 'turn_off_light':
            self.turn_off_light(params[0])
        else:
            print(f"Command {command_name} is not available in HueManager")

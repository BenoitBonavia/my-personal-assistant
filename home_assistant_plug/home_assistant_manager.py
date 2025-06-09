import json
import os
from typing import Literal

import requests


ScriptName = Literal['switch_on_tv_box', 'switch_off_tv_box', 'android_tv_pause', 'android_tv_play']

class HomeAssistantManager:
    """
    This class is used to interact with my Home Assistant instance through the REST API.
    """

    def __init__(self, config_file='home_assistant_plug/home_assistant_configuration.json'):
        with open(config_file) as config_file:
            self.config = json.load(config_file)
            self.ha_url = self.config['url']
            self.access_token = os.environ['HOME_ASSISTANT_TOKEN']

    def use_ha_script(self, script_name: ScriptName):
        url = f"{self.ha_url}/api/services/script/{script_name}"
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Content-Type': 'application/json'
        }
        print(f"Executing script: {script_name} at {url}")
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            print(f"Script {script_name} executed successfully.")
        else:
            print(f"Failed to execute script {script_name}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()

    def handle_command(self, command):
        command_name = command['command_name']
        params = command.get('params', [])
        print("EXECUTE COMMAND: ", command_name, params)
        try:
            method_to_call = getattr(self, command_name)
            method_to_call(*params)
        except AttributeError:
            print(f"Command {command_name} is not available in Home Assistant Manager")

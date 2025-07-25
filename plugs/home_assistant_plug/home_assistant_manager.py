import json
import os
import logging
from typing import Literal

import requests

from plugs.parent_manager import ParentManager

logger = logging.getLogger(__name__)

class HomeAssistantManager(ParentManager):
    """
    This class is used to interact with my Home Assistant instance through the REST API.
    """

    def __init__(self, config_file='plugs/home_assistant_plug/home_assistant_configuration.json'):
        super().__init__()
        self.manager_name = "home_assistant"
        with open(config_file) as config_file:
            self.config = json.load(config_file)
            self.ha_url = self.config['url']
            self.access_token = os.environ['HOME_ASSISTANT_TOKEN']

    def use_ha_script(self, script_name: Literal['switch_on_tv_box', 'switch_off_tv_box', 'android_tv_pause', 'android_tv_play']):
        """
        This method is used to execute any Home Assistant script.
        """
        url = f"{self.ha_url}/api/services/script/{script_name}"
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Content-Type': 'application/json'
        }
        logger.info("Executing script: %s at %s", script_name, url)
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            logger.info("Script %s executed successfully.", script_name)
        else:
            logger.error(
                "Failed to execute script %s. Status code: %s", script_name, response.status_code
            )
            logger.error("Response: %s", response.text)
            response.raise_for_status()
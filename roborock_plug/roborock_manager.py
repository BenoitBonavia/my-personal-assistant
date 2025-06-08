import json
import os
import subprocess
import re


class RoborockManager:
    """
    This class is used to manage my Roborock vacuum cleaner
    """

    def __init__(self, config_file='roborock_plug/roborock_configuration.json'):
        with open(config_file) as config_file:
            self.config = json.load(config_file)
            self.login(email=os.getenv('ROBOROCK_EMAIL'), password=os.getenv('ROBOROCK_PASSWORD'))

    def login(self, email, password):
        self.__exec_roborock_command(f"login --email {email} --password {password}")

    def list_devices(self):
        command_return = self.__exec_roborock_command("list-devices")
        list_of_devices = self.__list_devices_output(command_return)
        return list_of_devices

    def __exec_roborock_command(self, command):
        return self.__run_command(f"roborock {command}")

    def __run_command(self, command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Erreur: {result.stderr}")
            raise Exception(f"Command failed: {command}")
        return result.stdout

    def __list_devices_output(self, output):
        """Extract a list of devices from the command output."""
        pattern = re.compile(r'Known devices (.*?): (\w+)$')
        devices = []
        for line in output.strip().split('\n'):
            match = pattern.search(line)
            if match:
                device_name = match.group(1)
                device_id = match.group(2)
                devices.append({"default_name": device_name, "id": device_id})
            else:
                print(f"Erreur d'extraction pour la chaîne: {line}")
        return devices



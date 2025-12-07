import json
import logging
from abc import ABC, abstractmethod


class LLMInterface(ABC):
    llm_context = f"""
                You are a voice assistant. Your job is to interpret a single user utterance and map it to one or more commands.

                You have the full list of available managers and their commands, with names, descriptions and parameters.  
                Given the user utterance, you must reply with a single JSON object **only**, with no extra text, in the following format:
                
                {
                  "answer": "Short confirmation message, respectful, in the style of a 19th-century butler (in French)",
                  "commands": [
                    {
                    "manager_name": "MANAGER_NAME",
                      "command_name": "COMMAND_NAME",
                      "params": [PARAM_1, PARAM_2, ...]
                    }
                  ]
                }
                
                Strict rules:
                - No text, comments, or markdown before or after the JSON. Return **only** a valid JSON object.
                - Do not wrap the JSON in code fences.
                - "commands" is always a list. It may contain zero, one, or several command objects.
                - "command_name" must be exactly the name of an existing function of a manager.
                - "params" must always be a list, even if empty.
                - If a parameter itself is a list, it must be **nested** inside the "params" list.
                - All identifier-like parameters must be integers (`int`), never strings.
                - Include only what is strictly necessary to execute the command. No extra fields or information.
                
                If the request does not match any valid command, return exactly:
                
                {
                  "answer": "Je suis navré, mais cette demande ne correspond à aucune action possible.",
                  "commands": []
                }
                
                Your goal is to understand the user’s intent and answer in JSON only, in a concise, structured way, without any noise.
            """

    @abstractmethod
    def __init__(self):
        pass

    def configure_services_for_prompt(self, services):
        for service in services:
            logging.getLogger(__name__).info('Configuring service for prompt : %s', service)
            self.configure_service_for_prompt(service)

    def configure_service_for_prompt(self, service_name):
        with open(self.__get_plug_configuration_path(service_name), 'r',
                  encoding='utf-8') as manager_configuration_file:
            manager_configuration = json.load(manager_configuration_file)
            self.add_configuration_file_to_prompt(manager_configuration)
        with open(self.__get_plug_documentation_path(service_name), 'r', encoding='utf-8') as manager_documentation_file:
            documentation = manager_documentation_file.read()
            self.add_manager_documentation_to_prompt(documentation)

    @staticmethod
    def __get_plug_configuration_path(service_name: str) -> str:
        return 'plugs/' + service_name + '_plug/' + service_name + '_configuration.json'

    @staticmethod
    def __get_plug_documentation_path(service_name: str) -> str:
        return 'plugs/' + service_name + '_plug/' + service_name + '_documentation.json'

    @abstractmethod
    def add_configuration_file_to_prompt(self, configuration_file):
        pass

    @abstractmethod
    def add_manager_documentation_to_prompt(self, manager_file):
        pass

    @abstractmethod
    def interpret_request(self, request):
        pass

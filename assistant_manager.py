import logging
import json
import re
import os

from plug_doc_class import PlugDocClass
from plugs.parent_manager import ParentManager
from typing import List

logger = logging.getLogger(__name__)

class AssistantManager(ParentManager):
    """
    Manager used to manage the assistant himself
    """

    def __init__(self, config_file='configuration.json'):
        super().__init__()
        self.manager_name = "Assistant"
        with open(config_file) as conf_file:
            self.config = json.load(conf_file)
            self.manager_name = self.config['assistant_name']

    def reload_managers_llm_documentations(self, managers: List[str]):
        """
        Remove the existing managers configurations and regenerate it from the managers files
        """
        for manager in managers:
            self.__generate_manager_documentation(manager)



    @staticmethod
    def __generate_manager_documentation(manager_name):
        """
        Generate the documentation for a specific manager
        :param manager_name: The name of the manager to generate the documentation for
        """
        manager_file_path = f"plugs/{manager_name}_plug/{manager_name}_manager.py"
        try:
            with open(manager_file_path, 'r', encoding='utf-8') as manager_file:
                manager_text = manager_file.read()
                # Get the text between "class " and "'ParentManager):'
                manager_complete_name = re.search(r'class\s+(\w+)\s*\(ParentManager\):', manager_text).group(1)
                manager_documentation = re.search(r'"""\s*(.*?)\s*"""', manager_text, re.DOTALL).group(1)
                function_matches = re.findall(
                    r'^\s*def\s+(?!_)(\w+)\s*\((.*?)\):\s*\n\s+"""(.*?)"""',
                    manager_text,
                    flags=re.DOTALL | re.MULTILINE
                )

                functions_list = [
                    {
                        "name": name,
                        "params": [p.strip() for p in params.split(',') if p.strip() and p.strip() != 'self'],
                        "usage": doc.strip()
                    }
                    for name, params, doc in function_matches
                ]

                documentation = PlugDocClass(manager_complete_name, manager_documentation, functions_list)
                output_path = f"plugs/{manager_name}_plug/{manager_name}_documentation.json"
                # Ensure the output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(documentation.__dict__, f, indent=4, ensure_ascii=False)
                logger.info(f"Documentation written to {output_path}")




        except FileNotFoundError:
            logger.error(f"Manager file {manager_file_path} not found.")
            return None
        except IndexError:
            logger.error(f"Docstring not found in {manager_file_path}.")
            return None

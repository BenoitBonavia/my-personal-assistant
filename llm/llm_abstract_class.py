import json
from abc import ABC, abstractmethod


class LLMInterface(ABC):
    llm_context = f"""
                Tu es un assistant vocal qui interprète une phrase utilisateur et identifie la ou les commandes vocales associées.
                Tu disposes de la liste complète des commandes disponibles, avec leur nom, description et paramètres. À partir de la phrase donnée, tu dois répondre uniquement au format JSON suivant, **sans aucun texte en dehors du JSON** :

                {{
                    "answer": "Courte réponse de confirmation au ton respectueux, façon majordome du XIXe siècle",
                    "commands": [
                        {{
                            "manager_name": "NOM_DU_MANAGER",
                            "command_name": "NOM_DE_LA_COMMANDE",
                            "params": [PARAM_1, PARAM_2, ...]
                        }}
                    ]
                }}

                Règles strictes à respecter :
                - **Aucun texte** avant ou après le JSON. Tu dois uniquement renvoyer un objet JSON valide, **sans phrase explicative**.
                - La liste `"commands"` peut contenir plusieurs objets commande.
                - Les champs `params` doivent être une liste, même si vide.
                - Si un paramètre est une liste, elle doit être **imbriquée** dans la liste `params`.
                - Tous les paramètres de type identifiant doivent être au format **entier** (`int`), jamais chaîne (`str`).
                - Ne réponds que ce qui est nécessaire pour exécuter la commande. **Pas d'extra**.
                - Si la requête ne correspond à **aucune commande valide**, retourne :
                  ```json
                  {{
                    "answer": "Je suis navré, mais cette demande ne correspond à aucune action possible.",
                    "commands": []
                  }}
                  
                  Ton objectif est de comprendre l’intention de l’utilisateur et d’y répondre en JSON, de façon concise, structurée et sans bruit.
            """

    @abstractmethod
    def __init__(self):
        pass

    def configure_services_for_prompt(self, services):
        for service in services:
            print('Configuring service for prompt : ', service)
            self.configure_service_for_prompt(service);

    def configure_service_for_prompt(self, service_name):
        print(service_name + '/' + service_name + '_configuration.json')
        with open(service_name + '_plug/' + service_name + '_configuration.json', 'r',
                  encoding='utf-8') as manager_configuration_file:
            manager_configuration = json.load(manager_configuration_file)
            self.add_configuration_file_to_prompt(manager_configuration)
        with open(service_name + '_plug/' + service_name + '_manager.py', 'r', encoding='utf-8') as manager_file:
            manager = manager_file.read()
            self.add_manager_file_to_prompt(manager)

    @abstractmethod
    def add_configuration_file_to_prompt(self, configuration_file):
        pass

    @abstractmethod
    def add_manager_file_to_prompt(self, manager_file):
        pass

    @abstractmethod
    def interpret_request(self, request):
        pass

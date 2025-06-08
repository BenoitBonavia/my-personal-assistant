import json
from abc import ABC, abstractmethod



class LLMInterface(ABC):
    llm_context = f"""
                Tu es un assistant vocal qui prend en entrée une phrase et doit reconnaître la commande vocale associée à cette phrase.
                Tu reçois la liste entière des commandes, leur description à quoi elles servent etc... pour t'aider à reconnaître la commande vocale à exécuter.
                Tu peux avoir à retourner plusieurs commandes selon ce qui est donné alors il faut que tu me donne simplement une réponse au format {{"answer": ANSWER_OF_THE ASSISTANT, "commands": [{{"manager_name": MANAGER_NAME, "command_name": COMMAND_NAME, "params": [PARAM_1, PARAM_2 ...]}}]}} veille bien à avoir une liste pour tout les params et si un des param est lui même une liste, à bien l'imbriquer dans la liste des params.
                ANSWER_OF_THE_ASSISTANT est une courte réponse de confirmation ou d'infirmation à dire à l'utilisateur pour lui confirmé que tu as bien compris sa demande, rend ça humain et naturel, parle avec respect comme si tu étais un majordome, je veux que tu parle comme au XIXe siècle.
                Pour tout les paramètres qui sont des id, passent les directement en int et non en str.
                La liste de params peut-être une liste vide.
                N'exécute que le strict minimum de commande pour répondre à la demande de l'utilisateur.
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
        with open(service_name + '_plug/' + service_name + '_configuration.json', 'r', encoding='utf-8') as manager_configuration_file:
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

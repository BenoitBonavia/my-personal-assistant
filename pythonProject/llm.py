import os
from openai import OpenAI


class LLM:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.messages = [{"role": "system", "content":
            f"""
                Tu es un assistant vocal qui prend en entrée une phrase et doit reconnaître la commande vocale associée à cette phrase.
                Tu reçois la liste entière des commandes, leur description à quoi elles servent etc... pour t'aider à reconnaître la commande vocale à exécuter.
                Tu peux avoir à retourner plusieurs commandes selon ce qui est donné alors il faut que tu me donne simplement une réponse au format [{{manager_name: MANAGER_NAME, command_name: COMMAND_NAME, params: [PARAM_1, PARAM_2 ...]}}]
                La liste de params peut-être une liste vide
            """}]

    def add_configuration_file_to_prompt(self, configuration_file):
        self.messages.append({"role": "system", "content":
            f"""Ce fichier te permet de prendre connaissance, de la configuration d'un des manager de service auquel tu as accès.
                Tu peux l'utiliser pour t'aider à reconnaître la commande vocale à exécuter, le nom du manager etc...
             {configuration_file}"
            """})

    def ask(self, request):
        self.messages.append({"role": "user", "content": request})
        response = self.client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=self.messages, temperature=0)
        answer = response.choices[0].message.content
        return answer

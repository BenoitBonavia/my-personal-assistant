import os
from openai import OpenAI

from llm.llm_abstract_class import LLMInterface


class OpenAiLLM(LLMInterface):
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.base_prompt = [{"role": "system", "content": self.llm_context
            }]

    def add_configuration_file_to_prompt(self, configuration_file):
        self.base_prompt.append({"role": "system", "content":
            f"""Ce fichier te permet de prendre connaissance, de la configuration d'un des manager de service auquel tu as accès.
                Tu peux t'en servir pour prendre connaissance de toute la configuration dont tu pourrais avoir besoin
             {configuration_file}"
            """})

    def add_manager_file_to_prompt(self, manager_file):
        self.base_prompt.append({"role": "system", "content":
            f"""Ce fichier te permet de prendre connaissance, du manager de service auquel tu as accès
                Tu peux l'utiliser pour t'aider à reconnaître la commande vocale à exécuter etc... chaque méthode documentée est utilisable etc...
             {manager_file}"
            """})

    def interpret_request(self, request):
        messages = list(self.base_prompt)
        messages.append({"role": "user", "content": request})
        response = self.client.chat.completions.create(model="gpt-4.1-nano", messages=messages,
                                                       temperature=0)
        answer = response.choices[0].message.content
        return answer

import os
from llm.llm_abstract_class import LLMInterface
from google import genai
from google.genai import types


class GeminiAILLM(LLMInterface):

    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def add_configuration_file_to_prompt(self, configuration_file):
        self.llm_context = self.llm_context + f"""
        Ce fichier te permet de prendre connaissance, de la configuration d'un des manager de service auquel tu as accès.
        Tu peux t'en servir pour prendre connaissance de toute la configuration dont tu pourrais avoir besoin
        {configuration_file}
        """

    def add_manager_file_to_prompt(self, manager_file):
        self.llm_context = self.llm_context + f"""
        Ce fichier te permet de prendre connaissance, du manager de service auquel tu as accès
        Tu peux l'utiliser pour t'aider à reconnaître la commande vocale à exécuter etc... chaque méthode documentée est utilisable etc...
        {manager_file}
        """

    def interpret_request(self, request):
        answer = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.llm_context),
            contents=request
        )
        return self.__sanitize_answer(answer.text)

    @staticmethod
    def __sanitize_answer(text_answer):
        if text_answer.startswith("```json"):
            text_answer = text_answer.replace("```json", "").strip()
        if text_answer.endswith("```"):
            text_answer = text_answer[:-3].strip()
        return text_answer
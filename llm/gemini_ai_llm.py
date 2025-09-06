import os
from llm.llm_abstract_class import LLMInterface
import google.genai as genai
from google.genai import types
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GeminiAILLM(LLMInterface):

    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.chat = None
        self.chat_initialization_timestamp = None

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
        self.init_chat_if_needed()
        answer = self.chat.send_message(request)
        return self.__sanitize_answer(answer.text)

    def init_chat_if_needed(self):
        if self.chat is None or (datetime.now() - self.chat_initialization_timestamp) > timedelta(hours=24):
            logger.info("Initializing chat")
            self.chat = self.client.chats.create(
                model="gemini-2.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=self.llm_context
                ),
            )
            self.chat_initialization_timestamp = datetime.now()

    @staticmethod
    def __sanitize_answer(text_answer):
        if text_answer.startswith("```json"):
            text_answer = text_answer.replace("```json", "").strip()
        if text_answer.endswith("```"):
            text_answer = text_answer[:-3].strip()
        return text_answer
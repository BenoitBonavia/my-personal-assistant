import logging
import json
from datetime import datetime

from llm.gemini_ai_llm import GeminiAILLM
from llm.grok_ai_llm import GrokAiLLM
from llm.open_ai_llm import OpenAiLLM
from services.file_logger import FileLoggerService

logger = logging.getLogger(__name__)
file_logger = FileLoggerService("logs/command_log.log")

class CommandUnderstander:
    def __init__(self, configuration):
        managers = configuration['available_managers']
        self.llm = GeminiAILLM()
        self.llm.configure_services_for_prompt(managers)

    def interpret_and_jsonify(self, command_phrase):
        logger.info("Exec command %s", command_phrase)
        start = datetime.now()
        llm_answer = self.llm.interpret_request(command_phrase)
        end = datetime.now()
        delta = end - start
        file_logger.info(f"{end} interpret \"{command_phrase}\" in {delta.total_seconds() * 1000} milliseconds")
        logger.info("Llm answer: %s", llm_answer)
        return json.loads(llm_answer)
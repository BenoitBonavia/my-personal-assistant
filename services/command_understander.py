import logging
import json

from llm.gemini_ai_llm import GeminiAILLM

logger = logging.getLogger(__name__)

class CommandUnderstander():
    def __init__(self, configuration):
        managers = configuration['available_managers']
        self.llm = GeminiAILLM()
        self.llm.configure_services_for_prompt(managers)

    def interpret_and_jsonify(self, command_phrase):
        logger.info("Exec command %s", command_phrase)
        llm_answer = self.llm.interpret_request(command_phrase)
        logger.info("Llm answer: %s", llm_answer)
        return json.loads(llm_answer)
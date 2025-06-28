import json
import sys
import logging

import speech_recognition as sr

from assistant_manager import AssistantManager
from command_interpreter import CommandInterpreter
from llm.gemini_ai_llm import GeminiAILLM
from plugs.plex_plug.plex_manager import PlexManager
from plugs.roborock_plug.roborock_configurator import RoborockConfigurator
from speaker import Speaker

logger = logging.getLogger(__name__)

file_path = 'configuration.json'


class Main:
    def __init__(self):
        self.configuration = None
        self.llm = GeminiAILLM()
        self.ci = None
        self.speaker = Speaker()

    def main(self):
        with open(file_path, 'r', encoding='utf-8') as configuration_file:
            self.configuration = json.load(configuration_file)
            self.ci = CommandInterpreter(self.configuration)
            managers = self.configuration['available_managers']
            if "--regenerate-doc" in sys.argv:
                assistant_manager = AssistantManager()
                print('Update managers documentation')
                assistant_manager.reload_managers_llm_documentations(managers)
            self.llm.configure_services_for_prompt(managers)
            recognizer = sr.Recognizer()
            if "--chat" in sys.argv:
                self.test_chat()
            else:
                self.constant_listening(recognizer)

    def __handle_command(self, command):
        logger.info("Exec command %s", command)
        llm_answer = self.llm.interpret_request(command)
        logger.info("Llm answer: %s", llm_answer)
        llm_answer_as_json = json.loads(llm_answer)
        if 'commands' in llm_answer_as_json:
            logger.info("Commands to execute: %s", llm_answer_as_json['commands'])
            self.ci.handle_request(llm_answer_as_json['commands'])
        self.speaker.say(llm_answer_as_json['answer'])

    def constant_listening(self, recognizer):
        with sr.Microphone() as source:
            logger.info("Calibrating microphone... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=5)
            logger.info("Microphone calibrated. Start speaking.")

            while True:
                try:
                    audio = recognizer.listen(source, timeout=0.5, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio, language="fr-FR")
                    if (self.configuration['assistant_name'] in text):
                        self.__handle_command(text)

                except sr.WaitTimeoutError:
                    logger.warning("Listening timed out while waiting for phrase to start")
                except sr.UnknownValueError:
                    logger.warning("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    logger.error("Could not request results from Google Speech Recognition service; %s", e)

    def test_chat(self):
        while True:
            user_input = input("Your request : ")
            self.__handle_command(user_input)


class ColorFormatter(logging.Formatter):
    """Simple color formatter for console output."""

    LEVEL_COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[37m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[31;1m",
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        fmt = color + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + self.RESET
        formatter = logging.Formatter(fmt)
        return formatter.format(record)


def __setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("app.log")
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColorFormatter())

    root_logger.handlers = [file_handler, stream_handler]


if __name__ == "__main__":
    __setup_logging()
    my_instance = Main()
    my_instance.main()
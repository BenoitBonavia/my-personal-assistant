import sys
import logging
import json

import speech_recognition as sr

from command_interpreter import CommandInterpreter
from services.command_understander import CommandUnderstander
from services.file_logger import FileLoggerService
from services.sentry_service import SentryService
from speaker import Speaker
from datetime import datetime

logger = logging.getLogger(__name__)
file_logger = FileLoggerService("logs/stt.log")

file_path = 'configuration.json'


class Main:
    def __init__(self):
        with open(file_path, 'r', encoding='utf-8') as configuration_file:
            self.configuration = json.load(configuration_file)
            self.ci = CommandInterpreter(self.configuration)
            self.speaker = Speaker()
            self.command_understanding = CommandUnderstander(configuration=self.configuration)

    def main(self):
        SentryService()
        recognizer = sr.Recognizer()
        if "--chat" in sys.argv:
            self.test_chat()
        else:
            self.constant_listening(recognizer)

    def __handle_command(self, command):
        llm_answer_as_json = self.command_understanding.interpret_and_jsonify(command_phrase=command)
        if 'commands' in llm_answer_as_json:
            logger.info("Commands to execute: %s", llm_answer_as_json['commands'])
            self.ci.handle_request(llm_answer_as_json['commands'])
        self.speaker.say(llm_answer_as_json['answer'])

    def constant_listening(self, recognizer):
        with sr.Microphone() as source:
            logger.info("Calibrating microphone... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=5)
            # Increase sensitivity for distant speech
            # Disable dynamic adjustment so our manual threshold stays fixed
            recognizer.dynamic_energy_threshold = False
            # Lower the threshold to be more sensitive to quieter voices
            # (typical values range widely; keeping a sensible floor)
            current_threshold = recognizer.energy_threshold
            recognizer.energy_threshold = max(50, int(current_threshold * 0.6))
            # Make VAD less strict so short gaps don't cut speech
            recognizer.pause_threshold = 0.5
            recognizer.non_speaking_duration = 0.2
            logger.info("Microphone calibrated. Start speaking.")

            while True:
                try:
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=12)
                    start = datetime.now()
                    text = recognizer.recognize_google(audio, language="fr-FR")
                    end = datetime.now()
                    delta = end - start
                    file_logger.info(f"{end} transcript command in {delta.total_seconds() * 1000} milliseconds", )
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
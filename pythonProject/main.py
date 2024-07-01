import speech_recognition as sr
from hue.hue_manager import HueManager
from llm import LLM
from command_interpreter import CommandInterpreter
import json

file_path = 'configuration.json'


class Main:
    def __init__(self):
        self.configuration = None
        self.hue = HueManager()
        self.llm = LLM()
        self.ci = None

    def main(self):
        with open(file_path, 'r', encoding='utf-8') as configuration_file:
            self.configuration = json.load(configuration_file)
            self.ci = CommandInterpreter(self.configuration)
            managers = self.configuration['available_managers']
            for manager in managers:
                # Try load the configurations for the manager with the path manager name as path
                with open(manager + '/' + manager + '_configuration.json', 'r', encoding='utf-8') as manager_configuration_file:
                    manager_configuration = json.load(manager_configuration_file)
                    self.llm.add_configuration_file_to_prompt(manager_configuration)

            recognizer = sr.Recognizer()
            self.constant_listening(recognizer)

    def listen_command(self, recognizer, source):
        try:
            print("J'écoute la commande")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            text = recognizer.recognize_google(audio, language="fr-FR")
            print(f"Your command is : {text}")
            llm_answer = self.llm.ask(text)
            self.ci.handle_request(llm_answer)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    def constant_listening(self, recognizer):
        with sr.Microphone() as source:
            print("Calibrating microphone... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=5)
            print("Microphone calibrated. Start speaking.")

            while True:
                try:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
                    text = recognizer.recognize_google(audio, language="fr-FR")
                    if (self.configuration['trigger_phrase'] in text):
                        self.listen_command(recognizer, source)

                except sr.WaitTimeoutError:
                    print("Listening timed out while waiting for phrase to start")
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    my_instance = Main()
    manager = HueManager()
    manager.turn_on_light(1)
    my_instance.main()
import json

import speech_recognition as sr

from command_interpreter import CommandInterpreter
from llm.gemini_ai_llm import GeminiAILLM
from speaker import Speaker

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
            self.llm.configure_services_for_prompt(managers)
            recognizer = sr.Recognizer()
            self.test_chat()
            #self.constant_listening(recognizer)

    def __handle_command(self, command):
        print("Exec command " + command)
        llm_answer = self.llm.interpret_request(command)
        print("Llm answer: " + llm_answer)
        llm_answer_as_json = json.loads(llm_answer)
        if 'commands' in llm_answer_as_json:
            print("Commands to execute: " + str(llm_answer_as_json['commands']))
            self.ci.handle_request(llm_answer_as_json['commands'])
        self.speaker.say(llm_answer_as_json['answer'])

    def constant_listening(self, recognizer):
        with sr.Microphone() as source:
            print("Calibrating microphone... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=5)
            print("Microphone calibrated. Start speaking.")

            while True:
                try:
                    audio = recognizer.listen(source, timeout=0.5, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio, language="fr-FR")
                    if (self.configuration['trigger_phrase'] in text):
                        self.__handle_command(text)

                except sr.WaitTimeoutError:
                    print("Listening timed out while waiting for phrase to start")
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

    def test_chat(self):
        while True:
            user_input = input("Your request : ")
            self.__handle_command(user_input)



if __name__ == "__main__":
    my_instance = Main()
    my_instance.main()
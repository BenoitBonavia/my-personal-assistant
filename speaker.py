import pyttsx3


class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()

    def say(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
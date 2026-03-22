# modules/voice_handler.py

import pyttsx3
import speech_recognition as sr
from typing import Optional


class VoiceHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 160)
        self.engine.setProperty("volume", 1.0)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True

    def speak(self, text: str):
        """Speaks text aloud."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout: int = 10) -> Optional[str]:
        """
        Listens for a spoken phrase and returns lowercase text.
        Returns None if nothing understood.
        """
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=6)
                text = self.recognizer.recognize_google(audio)
                print(f"[VoiceHandler] Heard: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                print(f"[VoiceHandler] API error: {e}")
                return None
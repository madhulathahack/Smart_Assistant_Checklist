import pyttsx3
import speech_recognition as sr

class VoiceHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Tune sensitivity
        self.recognizer.energy_threshold = 300       # mic sensitivity
        self.recognizer.pause_threshold = 0.8        # seconds of silence = end of phrase
        self.recognizer.dynamic_energy_threshold = True

    def speak(self, text: str):
        """Text-to-speech output."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self) -> str | None:
        """
        Listens for a spoken phrase and returns it as lowercase text.
        Returns None if speech could not be understood.
        """
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=6)
                text = self.recognizer.recognize_google(audio)
                print(f"[VoiceHandler] Heard: {text}")  # debug log
                return text.lower()
            except sr.WaitTimeoutError:
                return None   # nothing heard in time window
            except sr.UnknownValueError:
                return None   # speech not understood
            except sr.RequestError as e:
                print(f"[VoiceHandler] Google API error: {e}")
                return None
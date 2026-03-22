# modules/reminder_engine.py

import requests
from typing import Optional, List
from datetime import datetime


class ReminderEngine:
    def __init__(self, latitude: float = 12.97, longitude: float = 77.59):
        """
        Pass your city coordinates here.
        Default: Bangalore, India — change to your location.
        Examples:
          New York:  latitude=40.71, longitude=-74.01
          London:    latitude=51.51, longitude=-0.13
          Mumbai:    latitude=19.08, longitude=72.88

        Auto-detect your coordinates by running:
          import requests
          r = requests.get("https://ipapi.co/json/")
          print(r.json()["latitude"], r.json()["longitude"])
        """
        self.lat = latitude
        self.lon = longitude

        self.checklist: List[str] = [
            "wallet",
            "keys",
            "ID card",
            "phone",
        ]

        self.situational = {
            "umbrella":     self._is_rainy,
            "water bottle": self._is_hot,
            "jacket":       self._is_cold,
            "sunglasses":   self._is_sunny,
            "mask":         self._is_winter_morning,
        }

        self._weather_cache = None
        self._cache_time    = None

    # ── Weather fetching ───────────────────────────────────────────────────

    def _get_weather(self) -> dict:
        now = datetime.now()

        if self._weather_cache and self._cache_time:
            if (now - self._cache_time).seconds < 1800:
                return self._weather_cache

        try:
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={self.lat}&longitude={self.lon}"
                "&current_weather=true"
                "&hourly=temperature_2m,precipitation_probability,"
                "weathercode,apparent_temperature"
                "&forecast_days=1"
                "&timezone=auto"
            )
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            self._weather_cache = data
            self._cache_time    = now
            print(f"[Weather] Fetched: {self._summarise(data)}")
            return data

        except requests.exceptions.ConnectionError:
            print("[Weather] No internet — skipping weather check.")
            return {}
        except requests.exceptions.Timeout:
            print("[Weather] Timed out.")
            return {}
        except Exception as e:
            print(f"[Weather] Error: {e}")
            return {}

    def _summarise(self, data: dict) -> str:
        try:
            cw = data["current_weather"]
            return f"{cw['temperature']}°C, code={cw['weathercode']}"
        except Exception:
            return "unknown"

    def get_weather_summary(self) -> dict:
        data = self._get_weather()
        summary = {
            "temp":        None,
            "feels_like":  None,
            "rain_chance": None,
            "condition":   "Unknown",
            "icon":        "🌡️"
        }

        WEATHER_CODES = {
            0:  ("Clear sky",       "☀️"),
            1:  ("Mainly clear",    "🌤️"),
            2:  ("Partly cloudy",   "⛅"),
            3:  ("Overcast",        "☁️"),
            45: ("Foggy",           "🌫️"),
            48: ("Icy fog",         "🌫️"),
            51: ("Light drizzle",   "🌦️"),
            61: ("Light rain",      "🌧️"),
            63: ("Moderate rain",   "🌧️"),
            65: ("Heavy rain",      "🌧️"),
            71: ("Light snow",      "❄️"),
            80: ("Rain showers",    "🌦️"),
            95: ("Thunderstorm",    "⛈️"),
        }

        try:
            cw = data["current_weather"]
            summary["temp"]        = round(cw["temperature"])
            summary["feels_like"]  = round(data["hourly"]["apparent_temperature"][0])
            summary["rain_chance"] = data["hourly"]["precipitation_probability"][0]
            code    = cw["weathercode"]
            matched = WEATHER_CODES.get(code, ("Unknown", "🌡️"))
            summary["condition"] = matched[0]
            summary["icon"]      = matched[1]
        except (KeyError, IndexError):
            pass

        return summary

    # ── Condition checks ───────────────────────────────────────────────────

    def _is_rainy(self) -> bool:
        try:
            return self._get_weather()["hourly"]["precipitation_probability"][0] > 50
        except (KeyError, IndexError):
            return False

    def _is_hot(self) -> bool:
        try:
            return self._get_weather()["hourly"]["temperature_2m"][0] > 32
        except (KeyError, IndexError):
            return False

    def _is_cold(self) -> bool:
        try:
            return self._get_weather()["hourly"]["temperature_2m"][0] < 15
        except (KeyError, IndexError):
            return False

    def _is_sunny(self) -> bool:
        try:
            return self._get_weather()["current_weather"]["weathercode"] in [0, 1]
        except KeyError:
            return False

    def _is_winter_morning(self) -> bool:
        now = datetime.now()
        return now.month in [12, 1, 2] and 6 <= now.hour <= 10

    # ── Checklist management ───────────────────────────────────────────────

    def add_item(self, item: str) -> str:
        item = item.strip().lower()
        if item not in [i.lower() for i in self.checklist]:
            self.checklist.append(item)
            return f"Added '{item}' to your checklist."
        return f"'{item}' is already on your checklist."

    def remove_item(self, item: str) -> str:
        for i, existing in enumerate(self.checklist):
            if existing.lower() == item.strip().lower():
                self.checklist.pop(i)
                return f"Removed '{item}' from your checklist."
        return f"'{item}' was not found on your checklist."

    def get_checklist(self) -> List[str]:
        return self.checklist

    def get_active_items(self) -> List[str]:
        active = list(self.checklist)
        for item, fn in self.situational.items():
            try:
                if fn():
                    active.append(item)
            except Exception:
                pass
        return active

    # ── Message builder ────────────────────────────────────────────────────

    def _time_greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:  return "Good morning!"
        if hour < 17:  return "Good afternoon!"
        return "Good evening!"

    def get_checklist_message(self) -> str:
        items   = self.get_active_items()
        weather = self.get_weather_summary()

        if not items:
            return "Your checklist is empty — have a great trip!"

        if len(items) == 1:
            formatted = items[0]
        elif len(items) == 2:
            formatted = f"{items[0]} and {items[1]}"
        else:
            formatted = ", ".join(items[:-1]) + f" and {items[-1]}"

        greeting = self._time_greeting()

        tips = []
        if weather["rain_chance"] and weather["rain_chance"] > 50:
            tips.append(f"Rain chance is {weather['rain_chance']}% — take your umbrella!")
        elif weather["temp"] and weather["temp"] > 32:
            tips.append(f"It's {weather['temp']}°C out there — stay hydrated.")
        elif weather["temp"] and weather["temp"] < 15:
            tips.append(f"It's only {weather['temp']}°C — bundle up.")

        base = f"{greeting} Before you go, make sure you have your {formatted}."
        return f"{base} {' '.join(tips)}".strip()

    # ── Voice command parser ───────────────────────────────────────────────

    def handle_voice_command(self, phrase: str) -> Optional[str]:
        phrase = phrase.lower().strip()

        if any(phrase.startswith(p) for p in ["add ", "put "]):
            item = phrase
            for noise in ["add ", "put ", " to my list", " to the list",
                          " to checklist", " on my list"]:
                item = item.replace(noise, "")
            return self.add_item(item.strip())

        if any(phrase.startswith(p) for p in ["remove ", "delete ", "take off "]):
            item = phrase
            for noise in ["remove ", "delete ", "take off ",
                          " from my list", " from the list", " from checklist"]:
                item = item.replace(noise, "")
            return self.remove_item(item.strip())

        if any(p in phrase for p in ["what's on my list", "read my list",
                                      "read checklist", "what do i need",
                                      "show my list"]):
            items = self.get_checklist()
            return "Your checklist has: " + ", ".join(items) if items else "Your checklist is empty."

        if any(p in phrase for p in ["what's the weather", "weather today",
                                      "how's the weather", "weather outside"]):
            w = self.get_weather_summary()
            if w["temp"] is not None:
                return (f"It is currently {w['temp']}°C and {w['condition']}. "
                        f"Feels like {w['feels_like']}°C with "
                        f"{w['rain_chance']}% chance of rain.")
            return "Sorry, I couldn't fetch the weather right now."

        return None
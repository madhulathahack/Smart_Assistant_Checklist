# modules/context_engine.py

from typing import Optional, List, Dict
from datetime import datetime


class ContextEngine:
    """
    Detects the CONTEXT from what the user says and returns
    the right checklist. Each context's checklist is fully
    customisable — items can be added or removed per context.
    """

    def __init__(self):
        # Default checklists per context — user can edit these at runtime
        self.CONTEXTS: Dict[str, dict] = {

            "daily_exit": {
                "label":    "Going out",
                "icon":     "🚪",
                "triggers": [
                    "i'm leaving", "i am leaving", "heading out",
                    "going out", "i'm going out", "gotta go", "leaving now",
                    "i'm heading out", "going now"
                ],
                "checklist": ["wallet", "keys", "phone", "ID card"],
            },

            "meeting": {
                "label":    "Meeting / Office",
                "icon":     "💼",
                "triggers": [
                    "i have a meeting", "going to a meeting", "office meeting",
                    "heading to office", "going to office", "i have an interview",
                    "going for interview", "client meeting", "i have a call",
                    "team meeting", "conference"
                ],
                "checklist": [
                    "laptop", "charger", "notebook", "pen",
                    "ID card", "business cards", "phone", "keys"
                ],
            },

            "flight": {
                "label":    "Flight / Travel",
                "icon":     "✈️",
                "triggers": [
                    "going to airport", "i have a flight", "catching a flight",
                    "heading to airport", "i'm flying", "travelling today",
                    "travel today", "i'm travelling", "going on a trip"
                ],
                "checklist": [
                    "passport", "flight tickets", "hotel booking",
                    "wallet", "phone", "charger", "power bank",
                    "earphones", "travel adapter", "ID card",
                    "medicine", "clothes", "toiletries"
                ],
            },

            "road_trip": {
                "label":    "Road Trip",
                "icon":     "🚗",
                "triggers": [
                    "road trip", "long drive", "going on a drive",
                    "driving to", "road journey", "long road trip"
                ],
                "checklist": [
                    "driving license", "car documents", "wallet",
                    "phone", "charger", "water bottle", "snacks",
                    "sunglasses", "first aid kit", "emergency contact list"
                ],
            },

            "gym": {
                "label":    "Gym / Workout",
                "icon":     "🏋️",
                "triggers": [
                    "going to gym", "gym time", "heading to gym",
                    "workout time", "going for workout", "morning workout",
                    "evening workout", "going to fitness"
                ],
                "checklist": [
                    "gym bag", "water bottle", "towel",
                    "earphones", "phone", "gym membership card",
                    "change of clothes", "deodorant"
                ],
            },

            "grocery": {
                "label":    "Grocery / Shopping",
                "icon":     "🛒",
                "triggers": [
                    "going to grocery", "going to supermarket",
                    "going shopping", "need to buy groceries",
                    "heading to store", "going to market", "grocery run"
                ],
                "checklist": [
                    "wallet", "phone", "grocery list",
                    "reusable bags", "keys"
                ],
            },

            "hospital": {
                "label":    "Hospital / Doctor",
                "icon":     "🏥",
                "triggers": [
                    "going to hospital", "doctor appointment",
                    "going to clinic", "medical appointment",
                    "going to doctor", "health checkup", "doctor visit"
                ],
                "checklist": [
                    "health insurance card", "ID card", "wallet",
                    "medical records", "prescription", "phone",
                    "keys", "list of current medications"
                ],
            },

            "school_exam": {
                "label":    "School / Exam",
                "icon":     "🎓",
                "triggers": [
                    "going to school", "going to college", "heading to class",
                    "going for exam", "i have an exam", "exam today",
                    "going to university", "college today"
                ],
                "checklist": [
                    "ID card", "admit card", "pens", "pencils",
                    "notebook", "textbooks", "water bottle",
                    "phone", "wallet", "keys"
                ],
            },

        }

    # ── Context detection ──────────────────────────────────────────────────

    def detect_context(self, phrase: str) -> Optional[str]:
        """
        Returns context key if a trigger phrase is matched.
        Returns None if no context matched.
        """
        phrase = phrase.lower().strip()
        for key, data in self.CONTEXTS.items():
            for trigger in data["triggers"]:
                if trigger in phrase:
                    return key
        return None

    # ── Checklist access ───────────────────────────────────────────────────

    def get_checklist(self, context_key: str) -> List[str]:
        return list(self.CONTEXTS.get(context_key, {}).get("checklist", []))

    def get_label(self, context_key: str) -> str:
        return self.CONTEXTS.get(context_key, {}).get("label", "General")

    def get_icon(self, context_key: str) -> str:
        return self.CONTEXTS.get(context_key, {}).get("icon", "📋")

    def all_contexts(self) -> List[str]:
        return list(self.CONTEXTS.keys())

    # ── Checklist customisation ────────────────────────────────────────────

    def add_item(self, context_key: str, item: str) -> str:
        """Add an item to a specific context's checklist."""
        item = item.strip().lower()
        checklist = self.CONTEXTS[context_key]["checklist"]
        if item not in [i.lower() for i in checklist]:
            checklist.append(item)
            return f"Added '{item}' to your {self.get_label(context_key)} checklist."
        return f"'{item}' is already in your {self.get_label(context_key)} checklist."

    def remove_item(self, context_key: str, item: str) -> str:
        """Remove an item from a specific context's checklist."""
        checklist = self.CONTEXTS[context_key]["checklist"]
        for i, existing in enumerate(checklist):
            if existing.lower() == item.strip().lower():
                checklist.pop(i)
                return f"Removed '{item}' from your {self.get_label(context_key)} checklist."
        return f"'{item}' was not found in the {self.get_label(context_key)} checklist."

    def add_custom_context(self, key: str, label: str, icon: str,
                           triggers: List[str], checklist: List[str]):
        """Create a brand new custom context."""
        self.CONTEXTS[key] = {
            "label":     label,
            "icon":      icon,
            "triggers":  [t.lower() for t in triggers],
            "checklist": checklist,
        }

    # ── Message builder ────────────────────────────────────────────────────

    def build_message(self, context_key: str, weather: dict = None) -> str:
        items   = self.get_checklist(context_key)
        label   = self.get_label(context_key)
        greeting = self._time_greeting()

        if not items:
            return f"{greeting} Your {label} checklist is empty — have a great trip!"

        if len(items) == 1:
            formatted = items[0]
        elif len(items) == 2:
            formatted = f"{items[0]} and {items[1]}"
        else:
            formatted = ", ".join(items[:-1]) + f" and {items[-1]}"

        base = f"{greeting} Looks like you're heading out for {label}. Don't forget your {formatted}."

        tips = []
        if weather:
            if weather.get("rain_chance", 0) and weather["rain_chance"] > 50:
                tips.append(f"Rain chance is {weather['rain_chance']}% — take an umbrella!")
            elif weather.get("temp") and weather["temp"] > 32:
                tips.append(f"It's {weather['temp']}°C outside — carry water!")
            elif weather.get("temp") and weather["temp"] < 15:
                tips.append(f"It's only {weather['temp']}°C — wear a jacket!")

        return f"{base} {' '.join(tips)}".strip()

    def _time_greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:  return "Good morning!"
        if hour < 17:  return "Good afternoon!"
        return "Good evening!"

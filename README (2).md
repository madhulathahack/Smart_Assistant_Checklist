# 🧠 Smart Exit Assistant

> **No wake word. No manual trigger. Just say where you're going and it handles the rest.**

A voice-activated, context-aware checklist reminder that listens passively, understands your situation, and speaks the exact items you need — while simultaneously notifying your phone.

---

## 📖 What It Does

Most reminder apps wait for you to open them. This one listens.

Say **"I have a meeting"** → reminds you of laptop, charger, notebook, business cards
Say **"I have a flight"** → reminds you of passport, tickets, power bank, adapter, medicine
Say **"Going to gym"** → reminds you of gym bag, towel, earphones, membership card
Say **"I'm leaving"** → reminds you of wallet, keys, phone, ID card

All spoken aloud on your laptop. All sent as a notification to your phone. Automatically.

---

## 🎯 Every Situation Covered

| You say | Situation | Key items |
|---|---|---|
| "I'm leaving" / "Heading out" | 🚪 Daily exit | Wallet · Keys · Phone · ID card |
| "I have a meeting" / "Going to office" | 💼 Meeting | Laptop · Charger · Notebook · Business cards |
| "I have a flight" / "Going to airport" | ✈️ Flight | Passport · Tickets · Power bank · Adapter · Medicine |
| "Road trip" / "Long drive" | 🚗 Road trip | Driving license · Car docs · Snacks · First aid kit |
| "Going to gym" / "Workout time" | 🏋️ Gym | Gym bag · Towel · Earphones · Membership card |
| "Going shopping" / "Grocery run" | 🛒 Grocery | Wallet · Grocery list · Reusable bags |
| "Doctor appointment" / "Going to clinic" | 🏥 Hospital | Insurance card · Medical records · Prescription |
| "I have an exam" / "Going to college" | 🎓 Exam | Admit card · Pens · ID · Textbooks |
| Your own custom phrase | 📋 Custom | Your own checklist items |

---

## 🌦️ Weather-Smart

Every reminder checks live weather and auto-adds items:

| Condition | Auto-added |
|---|---|
| Rain chance > 50% | Umbrella |
| Temperature > 32°C | Water bottle |
| Temperature < 15°C | Jacket |
| Clear sky | Sunglasses |
| Winter morning (Dec–Feb, 6–10am) | Mask |

Uses [Open-Meteo](https://open-meteo.com) — **no API key required, completely free.**

---

## 📁 Project Structure

```
Python_project/
├── app.py                          ← Main Streamlit UI + thread manager
├── com.smartexit.assistant.plist   ← macOS auto-start service (launchd)
├── .python-version                 ← Pins Python 3.10.13
├── .gitignore
├── README.md
├── mobile_app/
│   ├── index.html                  ← Phone app (PWA)
│   ├── manifest.json               ← Makes it installable on home screen
│   └── sw.js                       ← Offline support (service worker)
└── modules/
    ├── __init__.py                 ← Package initialiser
    ├── voice_handler.py            ← Mic input + TTS + phone notifications
    ├── reminder_engine.py          ← Daily checklist + weather API
    └── context_engine.py           ← Context detection + all checklists
```

---

## 🗂️ What Each File Does

### `modules/voice_handler.py` — The ears and mouth
Handles everything audio. Listens to your microphone, transcribes speech via Google Speech API, speaks back via pyttsx3, and sends notifications to your phone via ntfy.sh.

```
Listens  → microphone → Google → text
Speaks   → text → pyttsx3 → laptop speakers
Notifies → text → ntfy.sh → your phone
```

Every context has its own alert so your phone shows the right title:

| Alert method | Phone notification |
|---|---|
| `alert_daily_exit()` | 🚪 Exit Reminder |
| `alert_meeting()` | 💼 Meeting Checklist |
| `alert_flight()` | ✈️ Travel Checklist |
| `alert_gym()` | 🏋️ Gym Checklist |
| `alert_hospital()` | 🏥 Hospital Checklist |
| `alert_exam()` | 🎓 Exam Checklist |
| `alert_morning()` | ⏰ Morning Reminder |

---

### `modules/reminder_engine.py` — Weather + daily checklist
Manages your always-on daily exit checklist and fetches real-time weather from Open-Meteo. Weather is cached for 30 minutes to avoid unnecessary calls. Situational items (umbrella, jacket, etc.) are evaluated automatically each time a reminder fires.

---

### `modules/context_engine.py` — The brain
Detects the situation from what you say and loads the correct checklist. All 8 built-in contexts have fully editable checklists. You can also create unlimited custom contexts from the UI — no code needed.

---

### `app.py` — Connects everything
The main Streamlit app. Starts two background threads on launch:
- **Thread 1** → `listen_loop()` — always listening to mic, never stops
- **Thread 2** → `scheduler_loop()` — fires morning reminder at 08:30 every day

Routes every trigger (voice, button tap, or scheduler) through `dispatch_alert()` which speaks on the laptop and notifies your phone simultaneously.

---

### `com.smartexit.assistant.plist` — Auto-starts on Mac boot
A macOS `launchd` service file. Install it once and the app starts automatically every time your Mac boots — no terminal needed ever again.

```
Without it → Mac restarts → manually open terminal → run command
With it    → Mac restarts → app starts by itself ✓
```

Key settings inside:
- `RunAtLoad: true` → starts on login
- `KeepAlive: true` → restarts automatically if it crashes
- `ThrottleInterval: 5` → waits 5 seconds before restarting
- Logs saved to `app.log` and `app_error.log`

---

### `mobile_app/index.html` — The phone app
A full mobile app with three pages:
- **Home** — weather card, 8 context buttons, interactive tick-off checklist
- **Notify** — set your ntfy topic, send test notification
- **Settings** — set your city coordinates, auto-detect location

---

### `mobile_app/manifest.json` — Makes it installable
Without this it is just a website. With it, your phone treats it like a native app — opens without a browser bar, appears on your home screen, has a custom splash screen.

---

### `mobile_app/sw.js` — Offline support
A service worker that caches all app files on first visit. The app loads instantly on every subsequent visit, even without internet.

---

## 🔗 How Everything Connects

```
Mac boots
    ↓
launchd reads plist → app starts automatically
    ↓
app.py launches two background threads
    ├── Thread 1: mic always open, always listening
    └── Thread 2: scheduler ready for 8:30am

You speak "I have a flight"
    ↓
voice_handler.py hears and transcribes it
    ↓
context_engine.py matches → "flight" context
    ↓
reminder_engine.py checks weather
    ↓
voice_handler.alert_flight() fires
    ├── 🖥️  Laptop speaks checklist aloud
    └── 📱  Phone buzzes with notification

You open the phone app
    ├── See the same checklist
    ├── Tick off items as you pack
    └── Weather updates automatically
```

---

## 💻 Laptop Installation (macOS)

Everything below runs on your Mac. Do these steps once.

### Step 1 — Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2 — Install pyenv (Python version manager)
```bash
brew install pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3 — Install Python 3.10.13
```bash
pyenv install 3.10.13
cd /Users/madhulatha/Downloads/Python_project
pyenv local 3.10.13
python --version   # should say Python 3.10.13
```

### Step 4 — Install PortAudio (required for microphone)
```bash
brew install portaudio
```

### Step 5 — Install all Python packages
```bash
pip install streamlit opencv-python torch torchvision transformers \
    Pillow numpy pyttsx3 SpeechRecognition pyaudio requests schedule
```

### Step 6 — Run the app
```bash
cd /Users/madhulatha/Downloads/Python_project
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501` — the app is running.

---

## 📱 Phone Installation

The phone app is a **PWA (Progressive Web App)** — installed directly from the browser, no App Store needed.

### Step 1 — Find your Mac's local IP address
```bash
ipconfig getifaddr en0
# Example output: 192.168.1.42
```

### Step 2 — Serve the phone app from your Mac
```bash
cd /Users/madhulatha/Downloads/Python_project/mobile_app
python -m http.server 8080
```

### Step 3 — Install on iPhone
1. On your iPhone, open **Safari** (must be Safari, not Chrome)
2. Go to `http://192.168.1.42:8080` (use your actual IP from Step 1)
3. Tap the **Share** button (box with arrow at bottom)
4. Tap **Add to Home Screen**
5. Tap **Add**
6. The 🧠 icon now appears on your home screen like a real app

### Step 4 — Install on Android
1. On your Android phone, open **Chrome**
2. Go to `http://192.168.1.42:8080`
3. Tap the **three dots menu** (top right)
4. Tap **Add to Home Screen** or **Install App**
5. Tap **Install**
6. The 🧠 icon now appears on your home screen

### Step 5 — Install ntfy for notifications
| Platform | Link |
|---|---|
| iPhone (iOS) | [App Store — ntfy](https://apps.apple.com/app/ntfy/id1625396347) |
| Android | [Play Store — ntfy](https://play.google.com/store/apps/details?id=io.heckel.ntfy) |

After installing ntfy:
1. Open the ntfy app
2. Tap **+** to subscribe to a topic
3. Enter your topic name: `smart-exit-madhulatha` (or whatever you set in the app)
4. Tap **Subscribe**
5. Done — every reminder now fires a notification on your phone

---

## ▶️ How to Activate

### Activate the laptop app manually
```bash
cd /Users/madhulatha/Downloads/Python_project
python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### Activate to auto-start on every Mac boot (recommended)
Run this once — the app will start automatically every time your Mac starts:
```bash
# Copy the service file
cp com.smartexit.assistant.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.smartexit.assistant.plist

# Start it right now (without rebooting)
launchctl start com.smartexit.assistant
```

### Check it is running
```bash
launchctl list | grep smartexit
# You should see: 0  -  com.smartexit.assistant
```

### View live logs
```bash
# Normal output
tail -f /Users/madhulatha/Downloads/Python_project/app.log

# Errors only
tail -f /Users/madhulatha/Downloads/Python_project/app_error.log
```

### Restart the app (after making code changes)
```bash
launchctl stop com.smartexit.assistant
launchctl start com.smartexit.assistant
```

---

## ⏹️ How to Deactivate / Delete

### Stop the app temporarily (keeps auto-start intact)
```bash
launchctl stop com.smartexit.assistant
```
Start it again with:
```bash
launchctl start com.smartexit.assistant
```

### Disable auto-start permanently (stops running on boot)
```bash
launchctl unload ~/Library/LaunchAgents/com.smartexit.assistant.plist
```

### Delete the service completely
```bash
# Stop and unload
launchctl stop com.smartexit.assistant
launchctl unload ~/Library/LaunchAgents/com.smartexit.assistant.plist

# Delete the service file
rm ~/Library/LaunchAgents/com.smartexit.assistant.plist

# Confirm it is gone
launchctl list | grep smartexit
# Should return nothing
```

### Delete the phone app
**iPhone:** Long press the 🧠 icon → tap **Remove App** → tap **Delete App**

**Android:** Long press the 🧠 icon → tap **Uninstall** → tap **OK**

### Unsubscribe from ntfy notifications
Open the ntfy app → swipe left on `smart-exit-madhulatha` → tap **Delete**

### Uninstall all Python packages (if you want a clean slate)
```bash
pip uninstall streamlit opencv-python torch torchvision transformers \
    Pillow numpy pyttsx3 SpeechRecognition pyaudio requests schedule -y
```

---

## ⚠️ Limitations

### Internet required
- **Voice recognition** uses Google Speech API — requires active internet. Spoken phrases are sent to Google for transcription. If offline, the listener silently retries.
- **Weather data** uses Open-Meteo API — requires internet. If offline, the app falls back to the core checklist without weather-based additions.
- **Phone notifications** via ntfy.sh — require internet on both laptop and phone.

**How to handle this in the future:**

**For voice recognition (go fully offline):**

Replace Google Speech API with **OpenAI Whisper** — it runs entirely on your laptop, no internet needed:
```python
# pip install openai-whisper
import whisper

model = whisper.load_model("base")  # downloads once (~140MB), then works offline

def listen_offline(audio_file):
    result = model.transcribe(audio_file)
    return result["text"].lower()
```
Whisper is more accurate than Google for noisy environments and works with no internet, no API key, and no rate limits.

**For weather (offline fallback):**

Cache the last known weather to a local file. If the API fails, use the cached data instead of skipping weather entirely:
```python
import json, os

CACHE_FILE = "weather_cache.json"

def save_weather_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

def load_weather_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

# In _get_weather(): if API fails → load_weather_cache()
```
This way even without internet the app uses yesterday's weather as a reasonable fallback.

**For phone notifications (offline queuing):**

Queue notifications locally when offline and send them when internet is restored:
```python
import queue, threading

notification_queue = queue.Queue()

def notification_worker():
    while True:
        title, message = notification_queue.get()
        while True:  # retry until sent
            try:
                requests.post(ntfy_url, data=message, headers={"Title": title}, timeout=5)
                break
            except Exception:
                time.sleep(30)  # wait 30s and retry

# Start worker thread once
threading.Thread(target=notification_worker, daemon=True).start()

# Instead of sending directly, just add to queue
notification_queue.put((title, message))
# Worker sends it when internet is available
```

**Summary of future internet independence:**

| Feature | Current | Future fix |
|---|---|---|
| Voice recognition | Google API (needs internet) | OpenAI Whisper (fully offline) |
| Weather | Open-Meteo API (needs internet) | Local JSON cache as fallback |
| Phone notifications | ntfy.sh (needs internet) | Offline queue + retry on reconnect |
| Full offline mode | Not possible | Whisper + cache + queue = works with no internet |

### Microphone access required
- The app needs permission to access the microphone on your Mac.
- Go to **System Settings → Privacy & Security → Microphone** and make sure your terminal / Python is allowed.
- On macOS Sonoma and above, you may see a permission prompt on first run — click **Allow**.

### English only (currently)
- Voice recognition is configured for English. Phrases in other languages will not be detected.
- Google Speech API supports other languages but code changes are needed to enable them.

**How to handle this in the future:**

| Approach | How |
|---|---|
| Switch language in Google API | Change `recognize_google(audio, language="hi-IN")` for Hindi, `"es-ES"` for Spanish etc. |
| Auto-detect language | Use `langdetect` library to identify the language first, then pass it to the recogniser |
| Fully offline + multilingual | Replace Google Speech API with **OpenAI Whisper** — runs locally, supports 99 languages, no internet needed |
| User preference setting | Add a language dropdown in the Streamlit UI — user picks their language once and it is saved |

The cleanest long-term fix is Whisper:
```python
# pip install openai-whisper
import whisper
model = whisper.load_model("base")  # runs fully on your laptop
result = model.transcribe("audio.wav")  # auto-detects language
print(result["text"])
```
No API key. No internet. Works in Hindi, Tamil, Spanish, French and 96 other languages out of the box.

### No persistent storage
- Custom contexts and checklist edits are lost when the app restarts.
- This will be fixed in a future version with JSON file storage.

### Same Wi-Fi network required for phone app
- The phone app communicates with the laptop over your local network.
- Your phone and laptop must be on the same Wi-Fi for the phone to reach `http://192.168.x.x:8501`.
- Does not work over mobile data or different networks without a tunnelling tool like ngrok.

### Google Speech API has rate limits
- The free tier of Google Speech API has generous limits but very heavy usage could be throttled.
- If recognition stops working, wait a few minutes and it will resume.

### Laptop must be awake
- The microphone listener only works when the Mac is awake.
- If your Mac sleeps, the listener pauses and resumes when the Mac wakes up.
- Disable sleep during active hours in **System Settings → Battery → Options → Prevent automatic sleeping**.

### pyttsx3 voice quality
- The text-to-speech uses your Mac's built-in system voice, which is robotic.
- For a more natural voice, upgrade to gTTS (Google Text-to-Speech) in a future version.

---

## 📱 Phone Notifications Setup

1. Download the **ntfy** app on your phone — free on iOS and Android
2. In the Streamlit app, scroll to **Phone notification settings**
3. Your topic name is shown — subscribe to it in the ntfy app
4. Tap **Send test notification** to confirm it works

Every reminder from now on fires on both laptop and phone simultaneously.

---

## 🎤 Voice Commands

| Say | Action |
|---|---|
| `"I'm leaving"` | Daily exit checklist |
| `"I have a meeting"` | Meeting checklist |
| `"I have a flight"` | Travel checklist |
| `"Going to gym"` | Gym checklist |
| `"Add [item] to my list"` | Adds item to daily checklist |
| `"Remove [item] from my list"` | Removes item |
| `"What's on my list"` | Reads back your checklist |
| `"What's the weather"` | Speaks current conditions |

---

## 🛠️ Common Errors

| Error | Fix |
|---|---|
| `streamlit: command not found` | Use `python -m streamlit run app.py` |
| `str \| None TypeError` | You are on Python < 3.10. Use `Optional[str]` from `typing` |
| `ModuleNotFoundError: modules` | `cd` into the project folder before running |
| `PyAudio install fails` | Run `brew install portaudio` first |
| `pyenv version mismatch` | Run `pyenv local 3.10.13` in the project folder |

---

## 🚀 Future Roadmap

- [ ] Persistent checklist storage (save custom lists between sessions)
- [ ] Google Calendar sync (auto-detect meeting context)
- [ ] Wake word engine (Porcupine — fully offline)
- [ ] Confirmation flow ("Yes I have them" dismisses reminder)
- [ ] GPS-based trigger (remind when leaving home geofence)
- [ ] Multi-language support (Hindi, Spanish, French)
- [ ] Camera verification (visually confirm items picked up)

---

## 🧰 Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10.13 | Core language |
| Streamlit | Web UI |
| SpeechRecognition | Microphone + Google transcription |
| pyttsx3 | Offline text-to-speech |
| PyAudio | Microphone access |
| requests | Weather API + ntfy notifications |
| schedule | Daily 8:30am scheduler |
| Open-Meteo API | Free real-time weather |
| ntfy.sh | Free push notifications to phone |
| PWA (HTML/JS) | Installable mobile app |

---

*Built by Madhulatha · March 2026*

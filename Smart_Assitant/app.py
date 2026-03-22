# app.py

import streamlit as st
import threading
import schedule
import time
from modules.reminder_engine import ReminderEngine
from modules.voice_handler    import VoiceHandler
from modules.context_engine   import ContextEngine

st.set_page_config(page_title="Smart Exit Assistant", page_icon="🧠", layout="wide")

@st.cache_resource
def load_engines():
    return (
        ReminderEngine(),
        VoiceHandler(ntfy_topic="smart-exit-madhulatha"),  # ← change to your unique topic
        ContextEngine()
    )

reminder, voice, context_engine = load_engines()

ALERT_MAP = {
    "daily_exit":  voice.alert_daily_exit,
    "meeting":     voice.alert_meeting,
    "flight":      voice.alert_flight,
    "gym":         voice.alert_gym,
    "hospital":    voice.alert_hospital,
    "school_exam": voice.alert_exam,
    "grocery":     voice.alert_grocery,
    "road_trip":   voice.alert_road_trip,
}

defaults = {
    "trigger_reminder": False,
    "active_context":   None,
    "context_items":    [],
    "spoken_message":   "",
    "status_msg":       "",
    "listener_started": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def dispatch_alert(ctx_key, message):
    alert_fn = ALERT_MAP.get(ctx_key)
    if alert_fn:
        alert_fn(message)
    else:
        voice.alert_custom(context_engine.get_label(ctx_key), message)

def listen_loop():
    while True:
        phrase = voice.listen(timeout=10)
        if not phrase:
            continue
        ctx = context_engine.detect_context(phrase)
        if ctx:
            weather = reminder.get_weather_summary()
            msg     = context_engine.build_message(ctx, weather)
            st.session_state.active_context   = ctx
            st.session_state.context_items    = context_engine.get_checklist(ctx)
            st.session_state.spoken_message   = msg
            st.session_state.trigger_reminder = True
            st.session_state.status_msg       = f"🎤 Heard: \"{phrase}\""
            dispatch_alert(ctx, msg)
            st.rerun()
            continue
        response = reminder.handle_voice_command(phrase)
        if response:
            st.session_state.status_msg = f"✅ {response}"
            voice.speak(response)
            voice.send_notification("Smart Exit", response, tags="white_check_mark")
            st.rerun()

def morning_reminder():
    weather = reminder.get_weather_summary()
    msg     = context_engine.build_message("daily_exit", weather)
    st.session_state.active_context   = "daily_exit"
    st.session_state.context_items    = context_engine.get_checklist("daily_exit")
    st.session_state.spoken_message   = msg
    st.session_state.trigger_reminder = True
    st.session_state.status_msg       = "⏰ Morning reminder triggered"
    voice.alert_morning(msg)

def scheduler_loop():
    schedule.every().day.at("08:30").do(morning_reminder)
    while True:
        schedule.run_pending()
        time.sleep(30)

if not st.session_state.listener_started:
    st.session_state.listener_started = True
    threading.Thread(target=listen_loop,    daemon=True).start()
    threading.Thread(target=scheduler_loop, daemon=True).start()

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🧠 Smart Exit Assistant")
st.caption("No wake word, no manual trigger. Just say where you're going and it handles the rest.")

if st.session_state.status_msg:
    st.info(st.session_state.status_msg)

weather = reminder.get_weather_summary()
if weather["temp"] is not None:
    w1, w2, w3, w4 = st.columns(4)
    w1.metric(f"{weather['icon']} Condition", weather["condition"])
    w2.metric("🌡️ Temperature",  f"{weather['temp']}°C")
    w3.metric("🤔 Feels like",   f"{weather['feels_like']}°C")
    w4.metric("🌧️ Rain chance",  f"{weather['rain_chance']}%")
else:
    st.warning("⚠️ Weather unavailable — check internet connection.")

st.divider()
left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("🎯 What are you doing?")
    st.caption("Tap a context or say it aloud.")
    for ctx_key in context_engine.all_contexts():
        icon  = context_engine.get_icon(ctx_key)
        label = context_engine.get_label(ctx_key)
        if st.button(f"{icon}  {label}", key=f"btn_{ctx_key}", use_container_width=True):
            w   = reminder.get_weather_summary()
            msg = context_engine.build_message(ctx_key, w)
            st.session_state.active_context   = ctx_key
            st.session_state.context_items    = context_engine.get_checklist(ctx_key)
            st.session_state.spoken_message   = msg
            st.session_state.trigger_reminder = True
            st.session_state.status_msg       = f"{icon} {label} checklist loaded."
            dispatch_alert(ctx_key, msg)
            st.rerun()
    st.divider()
    st.subheader("➕ Create your own context")
    with st.expander("Add a new situation"):
        new_label    = st.text_input("Situation name",  placeholder="e.g. Wedding")
        new_icon     = st.text_input("Icon (emoji)",    placeholder="e.g. 💍")
        new_triggers = st.text_area("Voice triggers (one per line)", placeholder="going to wedding\nwedding day")
        new_items    = st.text_area("Checklist items (one per line)", placeholder="invitation\ngift\noutfit")
        if st.button("💾 Save context"):
            if new_label and new_triggers and new_items:
                key      = new_label.lower().replace(" ", "_")
                triggers = [t.strip() for t in new_triggers.splitlines() if t.strip()]
                items    = [i.strip() for i in new_items.splitlines()    if i.strip()]
                icon_val = new_icon.strip() if new_icon.strip() else "📋"
                context_engine.add_custom_context(key, new_label, icon_val, triggers, items)
                st.session_state.status_msg = f"✅ '{new_label}' context created!"
                st.rerun()
            else:
                st.warning("Please fill in name, triggers and items.")

with right:
    ctx = st.session_state.active_context
    if st.session_state.trigger_reminder and ctx:
        icon  = context_engine.get_icon(ctx)
        label = context_engine.get_label(ctx)
        st.subheader(f"{icon} {label} — Checklist")
        st.info(f"🔊 _{st.session_state.spoken_message}_")
        st.write("**Tick off as you pack:**")
        for item in st.session_state.context_items:
            st.checkbox(item.capitalize(), key=f"chk_{ctx}_{item}")
        st.divider()
        st.subheader("✏️ Edit this checklist")
        col_a, col_b = st.columns([3, 1])
        new_item = col_a.text_input("Add item:", placeholder="e.g. hand sanitiser", key="add_ctx_item")
        if col_b.button("Add", key="add_ctx_btn"):
            if new_item.strip():
                context_engine.add_item(ctx, new_item.strip())
                st.session_state.context_items = context_engine.get_checklist(ctx)
                st.rerun()
        for item in context_engine.get_checklist(ctx):
            ca, cb = st.columns([4, 1])
            ca.write(f"• {item}")
            if cb.button("✕", key=f"rm_{ctx}_{item}"):
                context_engine.remove_item(ctx, item)
                st.session_state.context_items = context_engine.get_checklist(ctx)
                st.rerun()
        st.session_state.trigger_reminder = False
    else:
        st.subheader("👋 Ready to help!")
        st.write("""
**How to use:**
- 🎤 Say *"I'm leaving"*, *"I have a meeting"*, *"Going to the gym"* etc.
- 👆 Or tap a context button on the left
- 📱 Your phone gets a notification at the same time
- ✏️ Edit any checklist to match your needs

**Voice commands:**

| Say | Action |
|---|---|
| "Add [item] to my list" | Adds to daily exit list |
| "Remove [item] from my list" | Removes from daily exit list |
| "What's on my list" | Reads your daily checklist |
| "What's the weather" | Speaks current weather |
        """)

st.divider()
st.subheader("📋 Daily exit checklist")
d1, d2 = st.columns(2)
with d1:
    for item in reminder.get_checklist():
        ca, cb = st.columns([4, 1])
        ca.write(f"• {item}")
        if cb.button("✕", key=f"daily_rm_{item}"):
            reminder.remove_item(item)
            st.rerun()
with d2:
    daily_new = st.text_input("Add to daily checklist:", placeholder="e.g. headphones")
    if st.button("Add to daily list") and daily_new:
        reminder.add_item(daily_new)
        st.rerun()

st.divider()
st.subheader("📱 Phone notification settings")
st.write(f"**Your ntfy topic:** `{voice.ntfy_topic}`")
st.caption("Download the ntfy app on your phone and subscribe to this topic.")
if st.button("🔔 Send test notification to phone"):
    ok = voice.send_notification(
        "Smart Exit Assistant",
        "Test notification! You are connected and ready to go.",
        tags="white_check_mark"
    )
    st.success("✅ Sent! Check your phone.") if ok else st.error("❌ Failed — check internet.")

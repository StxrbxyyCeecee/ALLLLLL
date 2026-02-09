import io
import os
import json
import time
import threading
import asyncio
import tempfile
import shutil
import subprocess
import webbrowser
from datetime import datetime
import psutil
import pyautogui
import pyttsx3
import speech_recognition as sr
import smtplib
from email.message import EmailMessage
import openai

import sounddevice as sd
import soundfile as sf
import edge_tts
from scipy.io.wavfile import write

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# =========================
# OPENAI CLIENT
# =========================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
# =========================
# FLASK APP
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# CONFIG
# =========================
VOICE = "en-US-GuyNeural"
RATE = "+0%"
VOLUME = "+100%"
PITCH = "+0Hz"

WAKE_WORDS = ["hey shiron", "shiron", "starra"]

MEMORY_FILE = "memory.json"
MAX_MEMORY = 20

stop_speaking_flag = threading.Event()
is_speaking = False
awake = False

# =========================
# MEMORY
# =========================
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except Exception as e:
        print("⚠ Memory corrupted, resetting:", e)
        return []

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory[-MAX_MEMORY:], f, indent=2)

def remember(role, content):
    memory = load_memory()
    memory.append({"role": role, "content": content})
    save_memory(memory)

# =========================
# TEXT TO SPEECH
# =========================
def edge_speak(text):
    global is_speaking
    if not text.strip():
        return

    def run():
        global is_speaking
        is_speaking = True

        async def speak():
            communicate = edge_tts.Communicate(
                text=text,
                voice=VOICE,
                rate=RATE,
                volume=VOLUME,
                pitch=PITCH
            )

            audio = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio.write(chunk["data"])

            audio.seek(0)
            data, sr_ = sf.read(audio, dtype="float32")
            channels = 1 if len(data.shape) == 1 else data.shape[1]

            with sd.OutputStream(samplerate=sr_, channels=channels) as stream:
                stream.write(data)

        asyncio.run(speak())
        is_speaking = False

    threading.Thread(target=run, daemon=True).start()

# =========================
# SPEECH TO TEXT
# =========================
recognizer = sr.Recognizer()

def listen(duration=5):
    if is_speaking:
        return ""
    fs = 16000
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        write(tmp.name, fs, recording)
        with sr.AudioFile(tmp.name) as source:
            audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio).lower()
    except:
        return ""

# =========================
# CHATGPT BRAIN
# =========================
def chatgpt_reply(user_text):
    memory = load_memory()
    messages = [
        {"role": "system", "content": "You are Shiron, a luxury AI assistant. Calm, intelligent, precise, and loyal."}
    ]
    messages.extend(memory)
    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    reply = response.choices[0].message.content.strip()
    remember("user", user_text)
    remember("assistant", reply)
    return reply

# =========================
# JARVIS COMMAND LIBRARY
# =========================

# System Commands
def open_calculator(): subprocess.run("calc")
def open_notepad(): subprocess.run("notepad")
def open_chrome(): subprocess.run("start chrome", shell=True)
def open_vs_code(): subprocess.run("code", shell=True)
def shutdown_pc(): os.system("shutdown /s /t 0")
def restart_pc(): os.system("shutdown /r /t 0")
def lock_pc(): os.system("rundll32.exe user32.dll,LockWorkStation")
def sleep_pc(): os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
def show_desktop(): os.system("powershell -command \"(new-object -com shell.application).minimizeall()\"")
def open_task_manager(): subprocess.run("taskmgr")

# File & Folder
def create_folder(path): os.makedirs(path, exist_ok=True)
def delete_file(path): os.remove(path) if os.path.exists(path) else None
def move_file(src, dest): shutil.move(src, dest)
def copy_file(src, dest): shutil.copy(src, dest)
def open_file(path): os.startfile(path)
def list_files(folder): return os.listdir(folder)
def search_files(folder, extension): return [os.path.join(r,f) for r,d,files in os.walk(folder) for f in files if f.endswith(extension)]

# Internet
def open_website(url): webbrowser.open(url)
def search_google(query): webbrowser.open(f"https://www.google.com/search?q={query}")
def open_youtube(): webbrowser.open("https://www.youtube.com")
def download_file(url, save_path): os.system(f"curl -o \"{save_path}\" {url}")
def open_email(): webbrowser.open("https://mail.google.com")

# Audio
def play_music(path): os.startfile(path)
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    def increase_volume():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(min(volume.GetMasterVolumeLevelScalar() + 0.1, 1.0), None)
    def decrease_volume():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(max(volume.GetMasterVolumeLevelScalar() - 0.1, 0.0), None)
    def mute_volume():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)
except:
    print("pycaw not installed, volume control disabled")

# =========================
# AUTOMATIC COMMAND DETECTION
# =========================
COMMANDS = {
    "open calculator": open_calculator,
    "open notepad": open_notepad,
    "open chrome": open_chrome,
    "open vs code": open_vs_code,
    "shutdown pc": shutdown_pc,
    "restart pc": restart_pc,
    "lock pc": lock_pc,
    "sleep pc": sleep_pc,
    "show desktop": show_desktop,
    "open task manager": open_task_manager,
    "play music": lambda: play_music("C:\\Users\\Rayce\\Music\\song.mp3"),
}

def execute_command(command_text):
    for key, func in COMMANDS.items():
        if key in command_text:
            func()
            edge_speak(f"Executing {key}")
            return True
    return False

# =========================
# BRAIN
# =========================
def brain(text):
    global awake
    if not awake:
        if any(w in text for w in WAKE_WORDS):
            awake = True
            edge_speak("I am awake.")
        return ""
    if "go to sleep" in text:
        awake = False
        edge_speak("Going to sleep.")
        return ""
    if "forget everything" in text:
        save_memory([])
        edge_speak("Memory cleared.")
        return ""
    if "what do you remember" in text:
        memory = load_memory()
        summary = "Here is what I remember. "
        for m in memory[-5:]:
            summary += f"{m['role']} said {m['content']}. "
        edge_speak(summary)
        return summary

    if execute_command(text):
        return f"Executed command: {text}"

    reply = chatgpt_reply(text)
    edge_speak(reply)
    return reply

# =========================
# API
# =========================
@app.route("/health")
def health():
    return jsonify({"alive": True, "awake": awake})

@app.route("/speak", methods=["POST"])
def speak_from_web():
    data = request.json or {}
    text = data.get("text", "").lower()
    if not text:
        return jsonify({"status": "empty"})
    reply = brain(text)
    return jsonify({"status": "ok", "reply": reply})

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            f.write("[]")

    print("Shiron running on port 5000")
    edge_speak("Shiron initialized. Starra online.")

    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False),
        daemon=True
    ).start()

    while True:
        command = listen()
        if command:
            brain(command)

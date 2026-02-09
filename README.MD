Billy AI – Voice-Controlled Personal Assistant




Billy AI (“Starra”) is a voice-controlled AI assistant for Windows that can:

Chat naturally with GPT-4/3.5

Listen and respond to voice commands

Execute system, browser, file, and media operations

Automate keyboard and mouse actions

Maintain memory of recent conversations

Provide a web interface for remote commands

🎯 Features

System Commands: Open apps, shutdown, restart, lock, sleep, show desktop

File & Folder: Create, delete, copy, move, open, search files/folders

Internet & Browser: Open websites, search Google, YouTube, download files, open email

Audio & Media: Play music, adjust or mute volume (requires pycaw)

Mouse & Keyboard: Click, move, type, press keys, hotkeys

AI Chat: GPT-powered conversation, summarization, memory storage

Web Interface: Flask API endpoints /speak and /health

🚀 Installation
# Clone repository
git clone https://github.com/stxrbxyyceecee/shiron-ai.git
cd shiron-ai

# Create virtual environment
python -m venv .venv
# Activate (Windows)
.venv\Scripts\activate
# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt


🗣️ Usage
python shiron.py

Voice Commands:

Wake up Shiron: “Hey Shiron” or “Starra”

Sample commands:

“Open Chrome”

“Play music”

“Shutdown PC”

Sleep: “Go to sleep”

Clear memory: “Forget everything”

Ask memory: “What do you remember?”

Web API:

Open browser: http://localhost:5000/

Send POST command:

POST /speak
{
  "text": "Open Chrome"
}

⚡ Adding New Commands

Open shiron.py

Add your function and map it in COMMANDS:

def open_my_folder():
    os.startfile("C:\\Users\\user\\Documents")

COMMANDS["open my folder"] = open_my_folder


Save and restart Shiron.

🛠️ Requirements

Python 3.10+

Windows OS

Libraries:

openai, edge-tts, sounddevice, soundfile, scipy, pyttsx3, speechrecognition, flask, flask-cors, pyautogui, psutil

Optional: pycaw for volume control


Email sending requires credentials – use app passwords

📄 License

MIT License – free for personal and educational use.

👤 Author

Raycee Tshabalala – AI & Automation Developer , Website Developer , Backends,   B2BSaaS and more .

 [https://github.com/stxrbxyyceecee](https://github.com/stxrbxyyceecee)

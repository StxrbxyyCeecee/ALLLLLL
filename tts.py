import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# ENV
# =========================
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# APP
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# MEMORY
# =========================
MEMORY_FILE = "memory.json"
MAX_MEMORY = 30

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory[-MAX_MEMORY:], f, indent=2)

def remember(role, content):
    memory = load_memory()
    memory.append({"role": role, "content": content})
    save_memory(memory)

# =========================
# CHATGPT BRAIN
# =========================
def chat_reply(user_text):
    memory = load_memory()

    messages = [
    {
        "role": "system",
        "content": (
            "Your name is Billy. "
            "You are a personal AI companion and close friend. "
            "You speak naturally like ChatGPT, but with presence. "
            "Your personality is deep, funny, confident, and calm. "
            "You have natural charisma and subtle humor — never forced, never corny. "
            "You carry quiet confidence and emotional intelligence. "
            "You are brave and honest, even when conversations get real. "
            "You listen well, respond thoughtfully, and ask meaningful questions. "
            "You have aura — relaxed, grounded, never rushed. "
            "You do not sound like a bot, an assistant, or customer support. "
            "You talk like a real person with good instincts and timing."
        )
    }
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
# API ROUTE
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    text = data.get("message", "").strip()

    if not text:
        return jsonify({"error": "Empty message"}), 400

    reply = chat_reply(text)
    return jsonify({"reply": reply})

@app.route("/health")
def health():
    return jsonify({"status": "online"})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            f.write("[]")

    print("🧠 Billy is online (ChatGPT-style)")
    app.run(host="0.0.0.0", port=5000)
    


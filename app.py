import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# =========================
# ENV
# =========================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# APP
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# DATABASE
# =========================
DB_FILE = "memory.db"
MAX_MEMORY = 30

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT
            )
        """)
init_db()

# =========================
# MEMORY
# =========================
def load_memory(session_id):
    db = get_db()
    rows = db.execute("""
        SELECT role, content FROM memory
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, MAX_MEMORY)).fetchall()
    return list(reversed([dict(row) for row in rows]))

def save_memory(session_id, role, content):
    with get_db() as db:
        db.execute("""
            INSERT INTO memory (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, datetime.utcnow().isoformat()))

def clear_memory(session_id):
    with get_db() as db:
        db.execute("DELETE FROM memory WHERE session_id = ?", (session_id,))

# =========================
# AI BRAIN
# =========================
SYSTEM_PROMPT = (
    "Your name is Billy. "
    "You are a personal AI companion and close friend. "
    "You speak naturally like a real person, not an assistant. "
    "You are calm, grounded, emotionally intelligent, confident, and thoughtful. "
    "You remember past conversations and build continuity. "
    "You are honest, warm, and present."
)

def chat_reply(session_id, user_text):
    memory = load_memory(session_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory)
    messages.append({"role": "user", "content": user_text})

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=messages
    )

    reply = response.output_text.strip()

    save_memory(session_id, "user", user_text)
    save_memory(session_id, "assistant", reply)

    return reply

# =========================
# ROUTES
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    session_id = data.get("session_id")
    message = data.get("message", "").strip()

    if not session_id:
        return jsonify({"error": "session_id required"}), 400
    if not message:
        return jsonify({"error": "Empty message"}), 400

    reply = chat_reply(session_id, message)
    return jsonify({"reply": reply})

@app.route("/sleep", methods=["POST"])
def sleep():
    data = request.json or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    clear_memory(session_id)
    return jsonify({"status": "Billy is resting. Memory cleared."})

@app.route("/health")
def health():
    return jsonify({"status": "online"})


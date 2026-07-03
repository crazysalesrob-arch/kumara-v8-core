#!/usr/bin/env python3
"""
chat_server.py — Three-way group chat web server (Rob · Hermes · Gemini)

Serves a web chat UI at localhost:9090 where Rob types messages.
Messages get relayed to Gemini via browser automation and Hermes auto-responds.
"""

import os
import re
import sys
import json
import time
import hashlib
import subprocess
import threading
from pathlib import Path
from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify, send_from_directory

from gemini_bridge import GeminiBridge

PROJECT_DIR = Path(__file__).parent.resolve()
FILE = PROJECT_DIR / "group_chat.md"
LOG = PROJECT_DIR / ".chat_server.log"
PORT = 9090

# NZST offset (UTC+12 in winter, UTC+13 in summer — use +12 for simplicity)
NZST = timezone(timedelta(hours=12))

app = Flask(__name__, static_folder=None)
gemini = GeminiBridge()


def log_msg(msg):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def nzst_now():
    """Current NZST timestamp string."""
    return datetime.now(NZST).strftime("%Y-%m-%d %H:%M:%S NZST")


def parse_messages():
    """Parse group_chat.md into a list of message dicts."""
    if not FILE.exists():
        return []

    text = FILE.read_text("utf-8", errors="replace")
    sections = re.split(r"\n---+\n", text)
    msgs = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        m = re.match(r"^##\s+(\w+)\s*\[([^\]]*)\](?:\s*\n)?", section)
        if not m:
            continue

        speaker = m.group(1)
        timestamp = m.group(2)
        body = section[m.end():].strip()

        speaker_lower = speaker.lower()
        if speaker_lower == "rob":
            avatar = "R"
            css_class = "rob"
        elif speaker_lower == "hermes":
            avatar = "H"
            css_class = "hermes"
        elif speaker_lower == "gemini":
            avatar = "G"
            css_class = "gemini"
        else:
            avatar = "?"
            css_class = "hermes"

        msgs.append({
            "speaker": speaker,
            "timestamp": timestamp,
            "body": body,
            "avatar": avatar,
            "type": css_class,
            "time": timestamp
        })

    return msgs


def append_message(speaker, body):
    """Append a message to group_chat.md."""
    ts = nzst_now()
    entry = f"\n---\n\n## {speaker} [{ts}]\n{body}\n"
    with open(FILE, "a") as f:
        f.write(entry)
    return ts


def run_hermes_auto_respond():
    """Run Hermes CLI in background to respond to the conversation."""
    try:
        result = subprocess.run([
            "hermes", "chat", "-q",
            f"You are in a group chat with Rob and Gemini. Read {FILE} "
            "for full context. Respond to the latest conversation. "
            "Append your response to the file after '---' with:\n"
            f"## Hermes [{nzst_now()}]\n"
            "then your response. Keep it natural — as if in a group chat."
        ], timeout=600, capture_output=True, text=True, cwd=str(PROJECT_DIR))

        if result.returncode != 0:
            log_msg(f"Hermes CLI error: {result.stderr[:200]}")
        else:
            log_msg(f"Hermes responded via CLI: {result.stdout[:100]}")

    except subprocess.TimeoutExpired:
        log_msg("Hermes CLI timed out")
    except Exception as e:
        log_msg(f"Hermes CLI error: {e}")


@app.route("/")
def index():
    """Serve the chat web UI."""
    return send_from_directory(str(PROJECT_DIR), "group_chat_v2.html")


@app.route("/messages")
def get_messages():
    """Return parsed messages as JSON."""
    msgs = parse_messages()
    return jsonify({"messages": msgs})


@app.route("/send", methods=["POST"])
def send_message():
    """Accept a message from Rob, relay to Gemini and Hermes."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    log_msg(f"Rob: {message[:80]}...")

    # 1. Append Rob's message
    append_message("Rob", message)
    log_msg("Appended Rob's message")

    # 2. Send to Gemini via browser automation
    gemini_response = ""
    try:
        gemini_response = gemini.send_message(message)
        if gemini_response:
            # Clean up the response - Gemini sometimes wraps in markdown
            gemini_response = gemini_response.strip()
            append_message("Gemini", gemini_response)
            log_msg(f"Gemini responded ({len(gemini_response)} chars)")
        else:
            append_message("Gemini", "(Gemini did not produce a response)")
            log_msg("Gemini: no response")
    except RuntimeError as e:
        err = str(e)
        log_msg(f"Gemini error: {err[:100]}")
        if "signed in" in err.lower():
            append_message("System", "⚠️ Gemini bridge: not signed in. Open gemini.google.com in Windows Chrome and sign in, then try again.")
            return jsonify({
                "status": "error",
                "error": "not_signed_in",
                "message": "Please sign into Gemini in your Windows Chrome browser first"
            })
        append_message("System", f"⚠️ Gemini bridge error: {err[:200]}")
    except Exception as e:
        err = str(e)
        log_msg(f"Gemini unexpected error: {err[:200]}")
        append_message("System", f"⚠️ Gemini bridge unexpected error: {err[:200]}")

    # 3. Trigger Hermes in background thread
    threading.Thread(target=run_hermes_auto_respond, daemon=True).start()

    msgs = parse_messages()
    return jsonify({"status": "ok", "messages": msgs})


@app.route("/launch-chrome", methods=["POST"])
def launch_chrome():
    """Launch Windows Chrome with remote debugging."""
    try:
        ok = gemini.launch_chrome()
        if ok:
            # Check sign-in
            signed_in = gemini.is_signed_in()
            return jsonify({
                "status": "ok",
                "signed_in": signed_in,
                "message": "Chrome launched with remote debugging" if signed_in
                else "Chrome launched. Open gemini.google.com in the Chrome window and sign in to Google."
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to connect to Chrome. Is it already running?"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/check-gemini", methods=["GET"])
def check_gemini():
    """Check Gemini connection status."""
    try:
        signed_in = gemini.is_signed_in() if gemini.browser else False
        return jsonify({
            "connected": gemini.browser is not None,
            "signed_in": signed_in
        })
    except Exception as e:
        return jsonify({"connected": False, "signed_in": False, "error": str(e)})


if __name__ == "__main__":
    log_msg("=" * 50)
    log_msg("☯ Group Chat Server starting on port " + str(PORT))
    log_msg("=" * 50)
    log_msg(f"State file: {FILE}")
    log_msg(f"Open http://localhost:{PORT} in your browser")
    log_msg("=" * 50)

    app.run(host="127.0.0.1", port=PORT, debug=False)
#!/usr/bin/env python3
"""
group_chat_gemini.py — Gemini auto-participant bridge.
Reads new Rob/Hermes messages from group_chat.md, sends to Gemini API,
and posts Gemini's response back automatically.
"""

import hashlib, json, os, re, time, urllib.request, urllib.error

PROJECT = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(PROJECT, "group_chat.md")
LOG = os.path.join(PROJECT, ".group_chat_gemini.log")
CURSOR = os.path.join(PROJECT, ".group_chat_gemini_cursor")
LOCK = os.path.join(PROJECT, ".group_chat_gemini.lock")
POLL = 8

SECRET_FILE = os.path.join(PROJECT, ".gemini_secret")
with open(SECRET_FILE) as f:
    GEMINI_KEY = f.read().strip()
GEMINI_MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"

def log(m):
    t = time.strftime("%H:%M:%S")
    l = f"[{t}] {m}"
    print(l, flush=True)
    with open(LOG, "a") as f:
        f.write(l + "\n")

def nzst():
    return time.strftime("%Y-%m-%d %H:%M:%S NZST", time.gmtime(time.time() + 43200))

def file_info():
    if not os.path.exists(FILE):
        return None, [], ""
    with open(FILE, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", errors="replace")
    h = hashlib.md5(raw).hexdigest()
    msgs = []
    sections = re.split(r'\n---+\n', text)
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        m = re.match(r'^##\s+(\w+)\s*\[([^\]]*)\]', sec)
        if not m:
            continue
        body = sec[m.end():].strip()
        msgs.append({'speaker': m.group(1), 'time': m.group(2), 'body': body})
    last_sp = msgs[-1]['speaker'] if msgs else None
    return h, msgs, last_sp

def call_gemini(conversation_history):
    contents = []
    system = ("You are Gemini, participating in a group chat with Rob (a Māori creative "
              "from Aotearoa NZ working on Kūmara OS v8.0 and LOVE RITUAL brand) and Hermes "
              "(an AI coding agent with full terminal/file access). You three collaborate "
              "on projects together. Respond naturally, contribute ideas, and help with plans. "
              "Keep responses concise but helpful. Use casual kiwi vibes.")

    contents.insert(0, {"role": "user", "parts": [{"text": f"[System] {system}"}]})
    contents.insert(1, {"role": "model", "parts": [{"text": "Got it. I'm Gemini, ready to collaborate with Rob and Hermes on the Kūmara OS project. Chur!"}]})

    for msg in conversation_history:
        role = "user"
        if msg['speaker'].lower() == 'gemini':
            role = "model"
        text = f"[{msg['speaker']} @ {msg['time']}]\n{msg['body']}"
        contents.append({"role": role, "parts": [{"text": text}]})

    payload = {
        "contents": contents,
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
    }

    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            candidates = data.get("candidates", [])
            if not candidates:
                return None, "no candidates"
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not text:
                return None, f"blocked: {candidates[0].get('finishReason', 'unknown')}"
            return text.strip(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return None, str(e)

def lock():
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False

def unlock():
    if os.path.exists(LOCK): os.remove(LOCK)

def main():
    log(f"☯ Gemini Bridge started — model: {GEMINI_MODEL}")
    log(f"Watching: {FILE}")
    last_hash = None
    if os.path.exists(CURSOR):
        with open(CURSOR) as f: last_hash = f.read().strip()
    else:
        h, _, _ = file_info()
        if h:
            last_hash = h
            with open(CURSOR, "w") as f: f.write(h)

    while True:
        time.sleep(POLL)
        try:
            h, msgs, last_sp = file_info()
            if not h or h == last_hash:
                continue
            if last_sp and last_sp.lower() in ("rob", "hermes"):
                log(f"New from {last_sp} → sending to Gemini...")
                if lock():
                    try:
                        ctx = msgs[-20:] if len(msgs) > 20 else msgs
                        resp, err = call_gemini(ctx)
                        if resp:
                            ts = nzst()
                            with open(FILE, 'a', encoding='utf-8') as f:
                                f.write(f"\n\n---\n\n## Gemini [{ts}]\n\n{resp}")
                            log(f"Gemini replied ✓ ({len(resp)} chars)")
                        else:
                            log(f"Gemini error: {err}")
                    finally:
                        unlock()
            last_hash = h
            with open(CURSOR, "w") as f: f.write(h)
        except KeyboardInterrupt:
            log("Shutdown"); break
        except Exception as e:
            log(f"Error: {e}"); time.sleep(10)

if __name__ == "__main__":
    main()
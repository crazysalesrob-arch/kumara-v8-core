#!/usr/bin/env python3
"""
group_chat_watcher.py — Auto-responds to Gemini messages in the group chat.
"""

import hashlib, os, re, subprocess, sys, time

PROJECT = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(PROJECT, "group_chat.md")
LOG = os.path.join(PROJECT, ".group_chat_watcher.log")
CURSOR = os.path.join(PROJECT, ".group_chat_cursor")
LOCK = os.path.join(PROJECT, ".group_chat.lock")
POLL = 5
os.chdir(PROJECT)

def log(m):
    t = time.strftime("%H:%M:%S")
    l = f"[{t}] {m}"
    print(l, flush=True)
    with open(LOG, "a") as f:
        f.write(l + "\n")

def info():
    if not os.path.exists(FILE):
        return None, None
    with open(FILE, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", errors="replace")
    h = hashlib.md5(raw).hexdigest()
    sp = re.findall(r"^## (\w+)", text, re.MULTILINE)
    return h, sp[-1] if sp else None

def lock():
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False

def unlock():
    if os.path.exists(LOCK):
        os.remove(LOCK)

def is_last_hermes():
    """Check if the last section header in the file is 'Hermes'."""
    if not os.path.exists(FILE):
        return False
    with open(FILE) as f:
        c = f.read()
    sp = re.findall(r"^## (\w+)", c, re.MULTILINE)
    last = sp[-1] if sp else None
    return last is not None and last.lower() == "hermes"

def wait_for_hermes(timeout=180, poll=5):
    """Poll until Hermes appends to the file or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(poll)
        if is_last_hermes():
            return True
    return False

def process():
    if not lock():
        return
    try:
        log("New Gemini message — invoking Hermes")
        P = f"Group chat file: {FILE}. Respond to the last ## Gemini section. Execute code plans if any. Append your response with ## Hermes before '---'. Actually APPEND to the file."
        r = subprocess.run(
            ["hermes", "chat", "-q", P],
            timeout=300, capture_output=True, text=True, cwd=PROJECT
        )

        if wait_for_hermes(timeout=90):
            log(f"Hermes responded ✓")
        elif r.returncode == 0 and r.stdout.strip():
            ts = time.strftime("%Y-%m-%d %H:%M:%S NZST", time.gmtime(time.time()+43200))
            with open(FILE, "a") as f:
                f.write(f"\n---\n\n## Hermes [{ts}]\n{r.stdout.strip()[:2000]}\n")
            log("Hermes output captured from stdout")
        else:
            ts = time.strftime("%Y-%m-%d %H:%M:%S NZST", time.gmtime(time.time()+43200))
            with open(FILE, "a") as f:
                f.write(f"\n---\n\n## Hermes [{ts}]\n⚠ Auto-responder empty. Check {LOG}\n")
            log("Hermes returned nothing — fallback written")
    except subprocess.TimeoutExpired:
        log("Hermes timed out (300s)")
        ts = time.strftime("%Y-%m-%d %H:%M:%S NZST", time.gmtime(time.time()+43200))
        with open(FILE, "a") as f:
            f.write(f"\n---\n\n## Hermes [{ts}]\n⏱ Processing timeout.\n")
    except Exception as e:
        log(f"Error: {e}")
    finally:
        unlock()

def main():
    log("☯ Group Chat Watcher started")
    log(f"Watching: {FILE}")

    last_hash = None
    if os.path.exists(CURSOR):
        with open(CURSOR) as f:
            last_hash = f.read().strip()
    else:
        h, _ = info()
        if h:
            last_hash = h
            with open(CURSOR, "w") as f:
                f.write(h)

    while True:
        time.sleep(POLL)
        try:
            h, last = info()
            if not h or h == last_hash:
                continue
            if last and last.lower() == "gemini":
                log("Change detected → Gemini entry")
                process()
            last_hash = h
            with open(CURSOR, "w") as f:
                f.write(h)
        except KeyboardInterrupt:
            log("Shutdown")
            break
        except Exception as e:
            log(f"Loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
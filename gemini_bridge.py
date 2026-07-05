"""
gemini_bridge.py — Browser automation for Gemini Web UI via Playwright + Windows Chrome

Connects to Chrome running on Windows with --remote-debugging-port=9222,
navigates gemini.google.com, sends Rob's messages and captures Gemini's replies.
"""

import json
import time
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_DIR = Path(__file__).parent.resolve()
CHROME_WIN = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUG_PORT = 9222
GEMINI_URL = "https://gemini.google.com"


class GeminiBridge:
    """Bridge to Gemini Web UI via Playwright + Windows Chrome."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def launch_chrome(self):
        """Launch Windows Chrome with remote debugging."""
        cmd = [
            "powershell.exe", "-Command",
            f"Start-Process '{CHROME_WIN}' -ArgumentList "
            f"'--remote-debugging-port={DEBUG_PORT}', "
            f"'--no-first-run', "
            f"'--disable-sync', "
            f"'--no-default-browser-check'"
        ]
        subprocess.run(cmd, capture_output=True, timeout=10)
        time.sleep(4)  # Wait for Chrome to start
        return self._connect()

    def _connect(self):
        """Connect to existing Chrome via CDP."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{DEBUG_PORT}"
            )
            # Use the first existing page or create a new one
            pages = self.browser.contexts[0].pages if self.browser.contexts else []
            self.page = pages[0] if pages else self.browser.new_page()
            return True
        except Exception as e:
            print(f"  CDP connect failed: {e}")
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            return False

    def is_signed_in(self):
        """Check if signed into Gemini."""
        try:
            self.page.goto(GEMINI_URL, wait_until="networkidle", timeout=15)
            time.sleep(2)
            # Check for sign-in indicators
            title = self.page.title().lower()
            if "sign in" in title or "log in" in title:
                # Check URL too
                if "accounts.google.com" in self.page.url:
                    return False
            # Check for Gemini-specific elements
            body = self.page.content().lower()
            if "sign in to continue" in body or "sign in with google" in body:
                return False
            return True
        except Exception as e:
            print(f"  is_signed_in error: {e}")
            return False

    def send_message(self, message: str, timeout_sec: int = 90) -> str:
        """Send a message to Gemini, return the reply text."""
        if not self.browser:
            if not self._connect():
                raise RuntimeError(
                    "Chrome not running with remote debugging. "
                    "Launch Chrome first."
                )

        # Navigate to Gemini
        self.page.goto(GEMINI_URL, wait_until="networkidle", timeout=30)
        time.sleep(2)

        # Check sign-in
        if not self.is_signed_in():
            # A more thorough check
            page_url = self.page.url
            if "accounts.google.com" in page_url or "signin" in page_url:
                raise RuntimeError(
                    "Not signed in to Google. Open gemini.google.com in your "
                    "Windows Chrome browser, sign in, then click 'Gemini Ready' on the chat page."
                )

        # Find and fill the input
        selectors = [
            "textarea[placeholder*='Enter']",
            "textarea[placeholder*='ask']",
            "textarea",
            "div[contenteditable='true']",
            "div[role='textbox']",
            "div.ql-editor",
            "input[type='text']",
        ]

        input_el = None
        for sel in selectors:
            try:
                input_el = self.page.query_selector(sel)
                if input_el:
                    break
            except Exception:
                continue

        if not input_el:
            # Debug: dump page structure
            html = self.page.content()[:3000]
            raise RuntimeError(
                f"Could not find Gemini input field. Page HTML preview:\n{html[:500]}"
            )

        # Clear and type
        input_el.click()
        time.sleep(0.5)
        input_el.fill("")
        input_el.type(message, delay=10)
        time.sleep(0.5)

        # Send via Enter
        self.page.keyboard.press("Enter")

        # Wait for response - look for new content appearing
        # Gemini generates responses incrementally
        start = time.time()
        last_content = ""
        stable_count = 0

        while time.time() - start < timeout_sec:
            time.sleep(2)

            # Try to extract latest response content
            js = """
            () => {
                // Get all message-like elements
                const selectors = [
                    '.message-content',
                    '[data-message]',
                    '.response-content',
                    '[data-test-id="response-content"]',
                    '.gemini-text',
                    '.conversation-turn',
                    // Generic: all text blocks in the main area
                    'main article',
                    'main div[class*="response"]',
                    'main div[class*="message"]'
                ];
                for (const sel of selectors) {
                    const els = document.querySelectorAll(sel);
                    if (els.length > 0) {
                        return Array.from(els)
                            .map(e => e.innerText.trim())
                            .filter(t => t.length > 10)
                            .join('\\n\\n---\\n\\n');
                    }
                }
                return '';
            }
            """

            try:
                new_content = self.page.evaluate(js)
            except Exception:
                continue

            # Check if content has changed
            if new_content and new_content != last_content:
                # Content is still changing - reset stable count
                last_content = new_content
                stable_count = 0
            elif new_content and new_content == last_content:
                # Stable content - the response might be done
                stable_count += 1
                if stable_count >= 3:  # Stable for ~6 seconds
                    # But also check if there's a "stop" button (generating)
                    try:
                        stop_btn = self.page.query_selector(
                            "button[aria-label*='Stop'], button[aria-label*='stop']"
                        )
                        if not stop_btn:
                            break  # Generation complete
                    except Exception:
                        break
            elif not new_content:
                # Still waiting for first content
                pass

        if not last_content:
            # Last resort: get all visible text
            try:
                last_content = self.page.evaluate(
                    "() => document.body.innerText"
                )[:5000]
            except Exception:
                last_content = "(could not extract Gemini response)"

        return last_content

    def close(self):
        """Close Playwright (Chrome stays running on Windows)."""
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        self.playwright = None
        self.browser = None
        self.page = None
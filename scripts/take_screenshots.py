"""يصوّر الموقع تلقائيًا (جوال وكمبيوتر، عربي وإنجليزي) ويحفظ الصور في docs/screenshots.

يشغّل الموقع بنفسه على منفذ مؤقت، ويستخدم متصفح Edge المثبّت في الجهاز عبر Playwright.
التشغيل: python scripts/make_sample_invoice.py ثم python scripts/take_screenshots.py
"""

import threading
import time
from pathlib import Path

import uvicorn
from playwright.sync_api import Page, sync_playwright

from smart_flow.web.app import app

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "docs" / "screenshots"
SAMPLE = PROJECT_ROOT / "data" / "inbox" / "sample_invoice.pdf"
PORT = 8765
BASE_URL = f"http://127.0.0.1:{PORT}"

PHONE = {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 2, "is_mobile": True}
DESKTOP = {"viewport": {"width": 1280, "height": 800}, "device_scale_factor": 1}


def start_server() -> uvicorn.Server:
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(0.1)
    return server


def upload_sample(page: Page) -> None:
    page.set_input_files("#file-input", SAMPLE)
    page.wait_for_selector("#result-card:not(.hidden)")


def shoot(browser, name: str, device: dict, locale: str, scheme: str = "light", action=None) -> None:
    context = browser.new_context(**device, locale=locale, color_scheme=scheme)
    page = context.new_page()
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")  # ننتظر تحميل الخط العربي
    if action:
        action(page)
    page.screenshot(path=OUTPUT / f"{name}.png")
    print(f"Saved {name}.png")
    context.close()


def main() -> None:
    if not SAMPLE.exists():
        raise SystemExit("Run scripts/make_sample_invoice.py first")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    server = start_server()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge")
        shoot(browser, "mobile-ar-home", PHONE, "ar-SA")
        shoot(browser, "mobile-ar-result", PHONE, "ar-SA", action=upload_sample)
        shoot(browser, "mobile-en-result", PHONE, "en-US", action=upload_sample)
        shoot(browser, "mobile-ar-dark", PHONE, "ar-SA", scheme="dark", action=upload_sample)
        shoot(browser, "desktop-en-home", DESKTOP, "en-US")

        # صفحة توثيق الـ API التي تنشئها FastAPI تلقائيًا
        context = browser.new_context(**DESKTOP)
        page = context.new_page()
        page.goto(f"{BASE_URL}/docs")
        page.wait_for_selector(".opblock")
        page.screenshot(path=OUTPUT / "api-docs.png")
        print("Saved api-docs.png")
        browser.close()

    server.should_exit = True


if __name__ == "__main__":
    main()

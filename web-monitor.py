# main.py
from playwright.sync_api import sync_playwright
import hashlib
import os
import json
import requests

URL = "https://www.webhallen.com/se/product/377253-Pokemon-Scarlet-Violet-10-Destined-Rivals-Booster-Box-36-Boosters"
HASH_FILE = "status_hash.txt"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def get_availability_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(3000)  # Vänta så JS hinner ladda

        try:
            # Sök efter knappen inom rätt div
            button = page.locator("div#add-product-to-cart button.text-btn._disabled span")
            if button.count() > 0:
                return button.first.inner_text().strip()
            else:
                return "Status ej hittad"
        finally:
            browser.close()

def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("Ingen Discord-webhook angiven.")
        return

    payload = { "content": message }
    headers = { "Content-Type": "application/json" }

    response = requests.post(DISCORD_WEBHOOK, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print("Notis skickad till Discord.")
    else:
        print(f"Fel vid Discord-notis: {response.status_code} {response.text}")

def main():
    current_status = get_availability_status()
    current_hash = hashlib.sha256(current_status.encode()).hexdigest()
    print(f"Aktuell status: {current_status}")

    previous_hash = ""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            previous_hash = f.read()

    if current_hash != previous_hash:
        print("🔄 Förändring upptäckt!")
        send_discord_message(f"📦 Statusändring: {current_status}\n{URL}")
        with open(HASH_FILE, 'w') as f:
            f.write(current_hash)
    else:
        print("✅ Ingen förändring.")

if __name__ == "__main__":
    main()

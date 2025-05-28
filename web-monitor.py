from playwright.sync_api import sync_playwright
import hashlib
import os
import json
import requests

URLS = [
    "https://www.webhallen.com/se/product/377253-Pokemon-Scarlet-Violet-10-Destined-Rivals-Booster-Box-36-Boosters",
    "https://www.webhallen.com/se/product/377246-Pokemon-Scarlet-Violet-8-5-Prismatic-Evolutions-Super-Premium-Collection",
    "https://www.webhallen.com/se/product/377231-Pokemon-Scarlet-Violet-151-Blooming-Waters-Premium-Collection",
    "https://www.webhallen.com/se/product/377238-Pokemon-Scarlet-Violet-9-Journey-Together-Elite-Trainer-Box",
    "https://www.webhallen.com/se/product/376704-Pokemon-Scarlet-Violet-8-5-Prismatic-Evolutions-Booster-Bundle-6-boosters",
    # Lägg till fler URL:er här om du vill
]

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
HASH_FILE = "status_hashes.json"  # Bytt till .json-fil

def get_availability_status(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)  # Vänta så JS hinner ladda

        try:
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

    response = requests.post(DISCORD_WEBHOOK, json=payload, headers=headers)
    if response.status_code == 204:
        print("Notis skickad till Discord.")
    else:
        print(f"Fel vid Discord-notis: {response.status_code} {response.text}")

def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f)

def main():
    previous_hashes = load_hashes()
    current_hashes = {}

    for url in URLS:
        print(f"Kollar URL: {url}")
        status = get_availability_status(url)
        if status == "Status ej hittad":
            print("⚠️ Status ej hittad – hoppar över.")
            continue
        current_hash = hashlib.sha256(status.encode()).hexdigest()
        current_hashes[url] = current_hash

        previous_hash = previous_hashes.get(url, "")

        print(f"Aktuell status: {status}")
        if current_hash != previous_hash:
            print("🔄 Förändring upptäckt!")
            send_discord_message(f"📦 Statusändring: {status}\n{url}")
        else:
            print("✅ Ingen förändring.")

    save_hashes(current_hashes)

if __name__ == "__main__":
    main()

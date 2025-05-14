import requests
from bs4 import BeautifulSoup
import hashlib
import os
import json

# Webbsidan att bevaka
URL = "https://www.webhallen.com/se/product/377253-Pokemon-Scarlet-Violet-10-Destined-Rivals-Booster-Box-36-Boosters"
# Fil där vi sparar senaste hash
HASH_FILE = "status_hash.txt"
# Discord-webhook (lägg in i GitHub Secrets som DISCORD_WEBHOOK)
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def get_availability_status():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Välj knappen som innehåller status
    button = soup.select_one("button.text-btn")
    if button and button.find("span"):
        return button.find("span").get_text(strip=True)
    else:
        return "Status ej hittad"

def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("Ingen Discord-webhook angiven.")
        return

    payload = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(DISCORD_WEBHOOK, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print("Notis skickad till Discord.")
    else:
        print(f"Fel vid skickande av Discord-notis: {response.status_code} {response.text}")

def main():
    current_status = get_availability_status()
    current_hash = hashlib.sha256(current_status.encode()).hexdigest()

    print(f"Aktuell status: {current_status}")
    print(f"Hash: {current_hash}")

    previous_hash = ""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            previous_hash = f.read()

    if current_hash != previous_hash:
        print("🟡 Förändring upptäckt!")
        send_discord_message(f"🔔 Produktstatus har ändrats: {current_status}\n{URL}")
        with open(HASH_FILE, 'w') as f:
            f.write(current_hash)
    else:
        print("✅ Ingen förändring.")

if __name__ == "__main__":
    main()

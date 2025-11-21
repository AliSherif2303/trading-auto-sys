#app/services/telegram_service.py
import requests
from datetime import datetime, timedelta
from threading import Timer
from app.core.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(user_id, text):
    payload = {"chat_id": user_id, "text": text}
    response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
    return response.json()

def add_to_channel(user_id):
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "user_id": user_id}
    response = requests.post(f"{BASE_URL}/inviteChatMember", json=payload)
    return response.json()

def kick_from_channel(user_id):
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "user_id": user_id}
    response = requests.post(f"{BASE_URL}/kickChatMember", json=payload)
    return response.json()

def schedule_auto_expire(user_id, end_time):
    seconds = (end_time - datetime.now()).total_seconds()
    if seconds <= 0:
        kick_from_channel(user_id)
        send_message(user_id, "انتهت مدتك وتمت إزالتك من القناة.")
        return
    Timer(seconds, lambda: expire_user(user_id)).start()

def expire_user(user_id):
    kick_from_channel(user_id)
    send_message(user_id, "انتهت مدتك وتمت إزالتك من القناة.")

def activate_subscription(user_id, duration_hours):
    add_to_channel(user_id)
    end_time = datetime.now() + timedelta(hours=duration_hours)
    schedule_auto_expire(user_id, end_time)
    send_message(user_id, f"تم تفعيل الاشتراك / التجربة لمدة {duration_hours} ساعة.")

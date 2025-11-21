#app/services/payment_service.py
import requests
from datetime import datetime, timedelta
from threading import Timer
from app.core.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, PAYMENTS, PAYPAL_CLIENT_ID, PAYPAL_SECRET, CRYPTO_WALLET, WHOP_API_KEY
from app.db.database_postgres import get_conn, add_user
from app.services.telegram_service import send_message, add_to_channel, schedule_auto_expire

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def generate_payment_link(user_id, plan, method, amount=10.0):
    payment_conf = PAYMENTS.get(method, {})
    if not payment_conf.get('enabled'):
        return None

    payment_url = None

    if method == "paypal":
        token_res = requests.post(
            "https://api-m.sandbox.paypal.com/v1/oauth2/token",
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
            data={"grant_type": "client_credentials"}
        )
        access_token = token_res.json()["access_token"]

        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [{"amount": {"currency_code": "USD", "value": f"{amount:.2f}"}}]
        }
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        order_res = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders", json=order_data, headers=headers)
        order = order_res.json()
        for link in order["links"]:
            if link["rel"] == "approve":
                payment_url = link["href"]
                break

    elif method == "whop":
        payment_url = f"https://api.whop.com/pay/{user_id}/{plan}"

    elif method == "crypto":
        payment_url = f"{CRYPTO_WALLET}/pay/{user_id}/{plan}"

    elif method == "local_bank":
        payment_url = f"https://localbank.example.com/pay/{user_id}/{plan}"

    if not payment_url:
        return None

    invoice_id = f"inv_{user_id}_{plan}_{int(datetime.now().timestamp())}"
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO payments (invoice_id, user_id, plan, method, status, amount, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    ''', (invoice_id, user_id, plan, method, 'pending', amount, datetime.now()))
    conn.commit()
    conn.close()

    # إرسال الرابط مباشرة للعميل عبر البوت
    send_message(user_id, f"اخترت الباقة: {plan}. اضغط هنا لإتمام الدفع: {payment_url}")

    return payment_url

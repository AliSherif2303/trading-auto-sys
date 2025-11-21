# app/services/tiktok_service.py
import requests
from app.services.telegram_service import send_message, activate_subscription
from app.db.database_postgres import check_user
from app.core.config import FREE_TRIAL_HOURS, TIKTOK_ACCESS_TOKEN

TIKTOK_API_URL = "https://sandbox.tiktokapis.com/message/send"  # استخدم Sandbox URL للتجارب

def send_message_to_bot(user_id, message):
    """
    دالة لمعالجة الرسائل القادمة من TikTok.
    - لو المستخدم جديد: يبدأ Free Trial ويضيفه على Telegram
    - لو موجود: يرسل له تأكيد استلام الرسالة
    """

    # التأكد من وجود المستخدم في قاعدة البيانات
    user = check_user(user_id)

    if not user:
        # مستخدم جديد → بدء Free Trial على Telegram
        activate_subscription(user_id, FREE_TRIAL_HOURS)
        send_message(user_id, f"أهلاً بك! لقد تم تفعيل تجربة مجانية لمدة {FREE_TRIAL_HOURS} ساعة.")

    else:
        send_message(user_id, f"رسالتك وصلت: {message}")

    # إرسال رسالة تأكيد للمستخدم على TikTok عبر API
    headers = {"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
    payload = {
        "recipient_id": user_id,
        "message": f"لقد استلمنا رسالتك: {message}"
    }

    try:
        res = requests.post(TIKTOK_API_URL, headers=headers, json=payload)
        if res.status_code == 200:
            print(f"[TikTok] رسالة تأكيد أرسلت لـ {user_id}")
        else:
            print(f"[TikTok] خطأ في إرسال الرسالة لـ {user_id}: {res.text}")
    except Exception as e:
        print(f"[TikTok] Exception عند الإرسال لـ {user_id}: {str(e)}")

# app/services/twitter_service.py
from app.services.telegram_service import send_message, activate_subscription
from app.db.database_postgres import check_user
from app.core.config import FREE_TRIAL_HOURS

def send_message_to_bot(user_id, message):
    print(f"[Twitter] رسالة مستلمة من {user_id}: {message}")

    user = check_user(user_id)

    if not user:
        activate_subscription(user_id, FREE_TRIAL_HOURS)
        send_message(user_id, f"أهلاً بك! لقد تم تفعيل تجربة مجانية لمدة {FREE_TRIAL_HOURS} ساعة.")
    else:
        send_message(user_id, f"رسالتك وصلت: {message}")

from fastapi import APIRouter, Request
from app.services.subscription_service import start_subscription
from app.services.payment_service import generate_payment_link
from app.services.telegram_service import send_message, add_to_channel, schedule_auto_expire
from app.core.config import FREE_TRIAL_HOURS
from app.db.database_postgres import check_user, add_user
from datetime import datetime, timedelta

router = APIRouter()

@router.post('/choose_plan')
async def choose_plan(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    username = data.get('username', 'Client')
    plan = data.get('plan')       # weekly, monthly, 6months, yearly, trial
    method = data.get('method')   # paypal, whop, crypto, local_bank

    existing_user = check_user(user_id)

    # ====== Free Trial Logic ======
    if plan == "trial":
        if existing_user and existing_user[3] == 'trial':
            return {"status": "error", "message": "لقد استخدمت التجربة المجانية بالفعل."}

        # إضافة المستخدم وبدء Free Trial
        add_user(user_id, username, platform="telegram", subscription_type="trial", duration_hours=FREE_TRIAL_HOURS)
        add_to_channel(user_id)
        end_time = datetime.now() + timedelta(hours=FREE_TRIAL_HOURS)
        schedule_auto_expire(user_id, end_time)
        send_message(user_id, f"أهلاً {username}! تم تفعيل تجربة مجانية لمدة {FREE_TRIAL_HOURS} ساعة.")
        return {"status": "ok", "message": "Free Trial started"}

    # ====== Paid Subscription Logic ======
    payment_url = generate_payment_link(user_id, plan, method)
    if not payment_url:
        return {"status": "error", "message": "طريقة الدفع غير مفعلة."}

    # لاحقًا بعد الدفع، webhook سيقوم بتفعيل الاشتراك وتحديث DB
    return {"status": "ok", "payment_url": payment_url, "message": f"اخترت الاشتراك: {plan}. بعد الدفع سيتم تفعيل الاشتراك تلقائيًا."}

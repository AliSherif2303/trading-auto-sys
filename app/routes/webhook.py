#app/routes/webhook.py
from fastapi import APIRouter, Request
from app.services.telegram_service import send_message, activate_subscription
from app.db.database_postgres import check_user_by_mobile, add_user
from app.core.config import FREE_TRIAL_HOURS

router = APIRouter()

@router.post('/platform')
async def platform_webhook(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    username = data.get('username', 'Client')
    platform = data.get('platform', 'unknown')
    mobile = data.get('mobile')
    choice = data.get('choice')  # "trial" أو أي plan مثل "weekly", "monthly"

    if not mobile:
        return {"status": "error", "message": "يرجى إرسال رقم الموبايل قبل اختيار الاشتراك"}

    # التحقق من Free Trial مسبقًا
    existing_user = check_user_by_mobile(mobile)
    if choice == 'trial':
        if existing_user:
            return {"status": "error", "message": "لقد استخدمت Free Trial مسبقًا"}
        # إضافة المستخدم وبدء Free Trial
        add_user(user_id, username, platform, mobile, subscription_type='trial', duration_hours=FREE_TRIAL_HOURS)
        activate_subscription(user_id, FREE_TRIAL_HOURS)
        return {"status": "ok", "message": f"تم تفعيل تجربة مجانية لمدة {FREE_TRIAL_HOURS} ساعة"}

    # الاشتراك المدفوع
    if choice in ["weekly", "monthly", "6months", "yearly"]:
        # هنا ممكن توليد رابط الدفع أو أي إجراء للدفع
        return {"status": "ok", "message": f"اخترت الاشتراك: {choice}"}

    # خيار غير معروف
    return {"status": "error", "message": "الباقة غير معروفة، يرجى الاختيار مجددًا"}


@router.post('/tiktok')
async def tiktok_webhook(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    message = data.get('message')
    from app.services.tiktok_service import send_message_to_bot
    send_message_to_bot(user_id, message)
    return {"status": "ok"}


@router.post('/twitter')
async def twitter_webhook(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    message = data.get('message')
    from app.services.twitter_service import send_message_to_bot
    send_message_to_bot(user_id, message)
    return {"status": "ok"}

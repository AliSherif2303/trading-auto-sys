# app/routes/telegram.py
from fastapi import APIRouter, Request
from app.services.telegram_service import send_message
from app.db.database_postgres import add_user, check_user
from app.core.config import FREE_TRIAL_HOURS

router = APIRouter()

@router.post('/start_free_trial')
async def start_free_trial(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    username = data.get('username', 'Client')
    platform = data.get('platform', 'unknown')

    existing_user = check_user(user_id)
    if existing_user and existing_user[4] == 'active':
        return {"status": "error", "message": "User already has an active subscription"}

    add_user(user_id, username, platform, subscription_type='trial', duration_hours=FREE_TRIAL_HOURS)
    send_message(user_id, f"أهلاً {username}! لقد تم تفعيل تجربة مجانية لمدة {FREE_TRIAL_HOURS} ساعة.")
    return {"status": "ok", "message": "Free trial started"}

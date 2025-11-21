from fastapi import APIRouter, Request
from app.services.payment_service import generate_payment_link
from app.services.subscription_service import start_subscription
from app.db.database_postgres import get_conn
from datetime import datetime

router = APIRouter()

@router.post("/create")
async def create_payment(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    plan = data.get("plan")
    method = data.get("method")

    payment_url = generate_payment_link(user_id, plan, method)
    if not payment_url:
        return {"status": "error", "message": "Payment method not enabled"}

    invoice_id = f"inv_{user_id}_{plan}_{int(datetime.now().timestamp())}"

    return {"status": "created", "payment_url": payment_url, "invoice_id": invoice_id}


@router.post("/webhook")
async def payment_webhook(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    status = data.get("status")  # 'paid' أو 'pending'

    action = "activated" if status.lower() == "paid" else "pending"

    if action == "activated":
        conn = get_conn()
        c = conn.cursor()
        # تحديث حالة الدفع
        c.execute("UPDATE payments SET status=%s WHERE user_id=%s AND status='pending'", ('paid', user_id))
        conn.commit()
        conn.close()

        # تفعيل الاشتراك تلقائيًا في DB وTelegram
        start_subscription(user_id, plan_key='weekly')  # ← يمكن تعديل plan_key حسب الـ invoice أو البيانات المرسلة

    return {"status": "ok", "action": action}

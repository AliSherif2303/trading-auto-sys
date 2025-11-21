from datetime import datetime, timedelta
from app.db.database_postgres import add_user, check_user, get_conn
from app.services.telegram_service import send_message, add_to_channel, kick_from_channel, schedule_auto_expire

def start_subscription(user_id, plan_key):
    now = datetime.now()
    duration_hours = 0

    if plan_key == 'weekly': duration_hours = 168
    elif plan_key == 'monthly': duration_hours = 720
    elif plan_key == '6months': duration_hours = 4320
    elif plan_key == 'yearly': duration_hours = 8760
    elif plan_key == 'trial': duration_hours = 12
    else: return False

    end_time = now + timedelta(hours=duration_hours)

    # تحقق من وجود المستخدم
    user = check_user(user_id)
    if user:
        conn = get_conn()
        c = conn.cursor()
        c.execute('''
            UPDATE users
            SET subscription_type=%s, status=%s, start_time=%s, end_time=%s
            WHERE user_id=%s
        ''', (plan_key, 'active', now, end_time, user_id))
        conn.commit()
        conn.close()
    else:
        # إذا المستخدم جديد → إضافة للمستخدم وبدء الاشتراك
        add_user(user_id, "Client", "unknown", subscription_type=plan_key, duration_hours=duration_hours)

    # بدء الاشتراك على Telegram
    add_to_channel(user_id)
    schedule_auto_expire(user_id, end_time)
    send_message(user_id, f"تم تفعيل الاشتراك/التجربة لمدة {duration_hours} ساعة.")

    return {
        'user_id': user_id,
        'plan': plan_key,
        'start_time': now,
        'end_time': end_time,
        'status': 'active'
    }

def check_subscription(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT subscription_type, status, end_time FROM users WHERE user_id=%s', (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None

    plan_type, status, end_time = row
    now = datetime.now()
    if status == 'active' and now > end_time:
        # تحديث حالة الاشتراك إلى expired
        conn = get_conn()
        c = conn.cursor()
        c.execute('UPDATE users SET status=%s WHERE user_id=%s', ('expired', user_id))
        conn.commit()
        conn.close()

        # طرد المستخدم من القناة وإرسال رسالة انتهاء
        kick_from_channel(user_id)
        send_message(user_id, "انتهت الفترة التجريبية أو الاشتراك. لتجديد الاشتراك اختر خطة من هنا.")
        status = 'expired'

    return {
        'user_id': user_id,
        'plan': plan_type,
        'status': status,
        'end_time': end_time
    }

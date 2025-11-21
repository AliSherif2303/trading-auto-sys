#app/db/database_postgres.py
import psycopg2
from datetime import datetime, timedelta
from app.core.config import POSTGRES_CONFIG

def get_conn():
    return psycopg2.connect(
        host=POSTGRES_CONFIG['host'],
        port=POSTGRES_CONFIG['port'],
        dbname=POSTGRES_CONFIG['dbname'],
        user=POSTGRES_CONFIG['user'],
        password=POSTGRES_CONFIG['password']
    )

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            platform TEXT,
            subscription_type TEXT,
            status TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            mobile TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            invoice_id TEXT PRIMARY KEY,
            user_id TEXT,
            plan TEXT,
            method TEXT,
            status TEXT,
            amount REAL,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username, platform, mobile=None, subscription_type='trial', duration_hours=12):
    conn = get_conn()
    c = conn.cursor()
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    c.execute('''
        INSERT INTO users (user_id, username, platform, subscription_type, status, start_time, end_time, mobile)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            username=EXCLUDED.username,
            platform=EXCLUDED.platform,
            subscription_type=EXCLUDED.subscription_type,
            status=EXCLUDED.status,
            start_time=EXCLUDED.start_time,
            end_time=EXCLUDED.end_time,
            mobile=EXCLUDED.mobile
    ''', (user_id, username, platform, subscription_type, 'active', start_time, end_time, mobile))
    conn.commit()
    conn.close()

def check_user_by_mobile(mobile):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE mobile=%s', (mobile,))
    user = c.fetchone()
    conn.close()
    return user

# app/main.py
from fastapi import FastAPI
from app.routes import webhook, telegram, payment, subscription

app = FastAPI()

# Include all routers
app.include_router(webhook.router, prefix='/webhook', tags=['Webhook'])
app.include_router(telegram.router, prefix='/telegram', tags=['Telegram'])
app.include_router(payment.router, prefix='/payment', tags=['Payment'])
app.include_router(subscription.router, prefix='/subscription', tags=['Subscription'])

@app.get('/')
def root():
    return {"status": "Trading Automation FastAPI Running"}

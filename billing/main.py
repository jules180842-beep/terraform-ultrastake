from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Billing Service")

class Subscription(BaseModel):
    user_id: str
    plan: str
    amount: float
    billing_cycle: str = "monthly"

class Invoice(BaseModel):
    invoice_id: str
    user_id: str
    amount: float
    date: datetime
    status: str

INVOICES = {}
SUBSCRIPTIONS = {}

@app.post("/subscribe")
async def create_subscription(sub: Subscription):
    """Create new subscription"""
    SUBSCRIPTIONS[sub.user_id] = sub.dict()
    return {"status": "subscribed", "user_id": sub.user_id}

@app.get("/invoices/{user_id}")
async def get_invoices(user_id: str):
    """Get user invoices"""
    return {"invoices": INVOICES.get(user_id, [])}

@app.get("/usage/{user_id}")
async def get_usage(user_id: str):
    """Get usage metrics"""
    return {"user_id": user_id, "usage": {}}

@app.get("/health")
async def health():
    return {"status": "healthy"}

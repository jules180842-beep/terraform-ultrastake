from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Dict

app = FastAPI(title="Usage Service")

class UsageEvent(BaseModel):
    user_id: str
    event_type: str
    amount: float
    timestamp: datetime = None

class UsageSummary(BaseModel):
    user_id: str
    total_compute: float = 0
    total_api_calls: int = 0
    total_storage: float = 0
    period: str = "monthly"

USAGE_EVENTS = {}
USAGE_SUMMARY = {}

@app.post("/usage/log")
async def log_usage(event: UsageEvent):
    """Log usage event"""
    event.timestamp = datetime.utcnow()
    
    if event.user_id not in USAGE_EVENTS:
        USAGE_EVENTS[event.user_id] = []
    
    USAGE_EVENTS[event.user_id].append(event.dict())
    return {"status": "logged", "event": event}

@app.get("/usage/summary/{user_id}")
async def get_usage_summary(user_id: str):
    """Get user usage summary"""
    events = USAGE_EVENTS.get(user_id, [])
    
    summary = {
        "user_id": user_id,
        "total_events": len(events),
        "events": events
    }
    return summary

@app.get("/usage/metrics/{org_id}")
async def get_metrics(org_id: str):
    """Get organization metrics"""
    return {"org_id": org_id, "metrics": {}}

@app.get("/health")
async def health():
    return {"status": "healthy"}

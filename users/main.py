from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Users Service")

class User(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: datetime = None
    updated_at: datetime = None

USERS_DB = {}

@app.post("/users")
async def create_user(user: User):
    """Create new user"""
    if user.user_id in USERS_DB:
        raise HTTPException(status_code=409, detail="User already exists")
    
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    USERS_DB[user.user_id] = user.dict()
    return {"status": "created", "user": user}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user profile"""
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS_DB[user_id]

@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    """Update user profile"""
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.updated_at = datetime.utcnow()
    USERS_DB[user_id] = user.dict()
    return {"status": "updated", "user": user}

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    if user_id in USERS_DB:
        del USERS_DB[user_id]
        return {"status": "deleted", "user_id": user_id}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/health")
async def health():
    return {"status": "healthy"}

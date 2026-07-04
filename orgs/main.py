from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI(title="Organizations Service")

class Organization(BaseModel):
    org_id: str
    name: str
    description: str = ""
    owner_id: str
    created_at: datetime = None

class Member(BaseModel):
    user_id: str
    role: str = "member"
    joined_at: datetime = None

ORGS_DB = {}
MEMBERS_DB = {}

@app.post("/orgs")
async def create_organization(org: Organization):
    """Create new organization"""
    if org.org_id in ORGS_DB:
        raise HTTPException(status_code=409, detail="Organization already exists")
    
    org.created_at = datetime.utcnow()
    ORGS_DB[org.org_id] = org.dict()
    MEMBERS_DB[org.org_id] = {org.owner_id: {"role": "owner", "joined_at": datetime.utcnow()}}
    return {"status": "created", "org": org}

@app.get("/orgs/{org_id}")
async def get_organization(org_id: str):
    """Get organization"""
    if org_id not in ORGS_DB:
        raise HTTPException(status_code=404, detail="Organization not found")
    return ORGS_DB[org_id]

@app.post("/orgs/{org_id}/members")
async def add_member(org_id: str, member: Member):
    """Add member to organization"""
    if org_id not in ORGS_DB:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    member.joined_at = datetime.utcnow()
    MEMBERS_DB[org_id][member.user_id] = member.dict()
    return {"status": "added", "member": member}

@app.get("/orgs/{org_id}/members")
async def get_members(org_id: str):
    """List organization members"""
    if org_id not in ORGS_DB:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"members": MEMBERS_DB.get(org_id, {})}

@app.delete("/orgs/{org_id}/members/{user_id}")
async def remove_member(org_id: str, user_id: str):
    """Remove member from organization"""
    if org_id not in ORGS_DB:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if user_id in MEMBERS_DB[org_id]:
        del MEMBERS_DB[org_id][user_id]
        return {"status": "removed", "user_id": user_id}
    raise HTTPException(status_code=404, detail="Member not found")

@app.get("/health")
async def health():
    return {"status": "healthy"}

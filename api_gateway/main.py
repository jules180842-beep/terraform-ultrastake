from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Optional

app = FastAPI(title="API Gateway")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth:8001"),
    "users": os.getenv("USERS_SERVICE_URL", "http://users:8002"),
    "billing": os.getenv("BILLING_SERVICE_URL", "http://billing:8003"),
    "orgs": os.getenv("ORGS_SERVICE_URL", "http://orgs:8004"),
    "usage": os.getenv("USAGE_SERVICE_URL", "http://usage:8005"),
}

@app.get("/health")
async def health():
    """API Gateway health check"""
    return {"status": "healthy", "services": SERVICES}

@app.get("/services")
async def get_services():
    """List all available services"""
    return {"services": SERVICES}

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request):
    """Proxy requests to Auth Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{SERVICES['auth']}/{path}",
                headers=request.headers
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Auth service error: {str(e)}")

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(path: str, request):
    """Proxy requests to Users Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{SERVICES['users']}/{path}",
                headers=request.headers
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Users service error: {str(e)}")

@app.api_route("/billing/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def billing_proxy(path: str, request):
    """Proxy requests to Billing Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{SERVICES['billing']}/{path}",
                headers=request.headers
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Billing service error: {str(e)}")

@app.api_route("/orgs/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def orgs_proxy(path: str, request):
    """Proxy requests to Organizations Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{SERVICES['orgs']}/{path}",
                headers=request.headers
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Orgs service error: {str(e)}")

@app.api_route("/usage/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def usage_proxy(path: str, request):
    """Proxy requests to Usage Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{SERVICES['usage']}/{path}",
                headers=request.headers
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Usage service error: {str(e)}")

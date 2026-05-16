"""Add Stripe payment foundation and user auth to AgentForge."""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import secrets

# Simulated database (replace with PostgreSQL in production)
users_db = {}
subscriptions_db = {}

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class SubscriptionTier(BaseModel):
    tier: str  # starter, professional, enterprise

# JWT-like simple token (use proper JWT in production)
def create_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    users_db[token] = {"email": email, "created": datetime.now().isoformat()}
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = credentials.credentials
    if token not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    return users_db[token]

# Auth routes
@app.post("/api/auth/register")
async def register(user: UserCreate):
    if user.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hashlib.sha256(user.password.encode()).hexdigest()
    token = create_token(user.email)
    users_db[token]["password_hash"] = hashed
    users_db[token]["subscription"] = "free"
    return {"token": token, "email": user.email}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    hashed = hashlib.sha256(user.password.encode()).hexdigest()
    for token, data in users_db.items():
        if data["email"] == user.email and data.get("password_hash") == hashed:
            return {"token": token, "email": user.email}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Subscription routes
@app.get("/api/subscription")
async def get_subscription(user: dict = Depends(verify_token)):
    return {
        "tier": user.get("subscription", "free"),
        "email": user["email"],
        "limits": {
            "free": {"deployments": 0, "repos": 50},
            "starter": {"deployments": 5, "repos": 740, "price": 49},
            "professional": {"deployments": -1, "repos": 740, "price": 149},
            "enterprise": {"deployments": -1, "repos": 740, "price": 499}
        }.get(user.get("subscription", "free"), {})
    }

@app.post("/api/subscription/create-checkout")
async def create_checkout(tier: SubscriptionTier, user: dict = Depends(verify_token)):
    """Create Stripe checkout session."""
    prices = {
        "starter": "price_starter_placeholder",
        "professional": "price_professional_placeholder",
        "enterprise": "price_enterprise_placeholder"
    }
    if tier.tier not in prices:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    # In production, call Stripe API here
    return {
        "checkout_url": f"https://buy.stripe.com/test_placeholder_{tier.tier}",
        "tier": tier.tier,
        "price": {"starter": 4900, "professional": 14900, "enterprise": 49900}[tier.tier]
    }

@app.post("/api/subscription/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook for payment confirmation."""
    payload = await request.body()
    # In production: verify Stripe signature, update subscription
    return {"status": "received"}

# Deployment limits
def check_deployment_limit(user: dict, current_count: int):
    tier = user.get("subscription", "free")
    limits = {"free": 0, "starter": 5, "professional": 999, "enterprise": 999}
    if current_count >= limits.get(tier, 0):
        raise HTTPException(status_code=403, detail="Deployment limit reached. Upgrade your plan.")

print("Stripe + Auth module loaded")
print("Add these routes to your main.py")

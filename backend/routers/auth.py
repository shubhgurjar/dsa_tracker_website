from fastapi import APIRouter, HTTPException, Header, Response, Cookie
from typing import Optional
from backend.config import load_config, save_config, verify_pin, hash_pin, generate_session_token, verify_session_token
from backend.models import LoginRequest, PinUpdateRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/status")
def auth_status(authorization: Optional[str] = Header(None)):
    cfg = load_config()
    auth_enabled = cfg.get("auth_enabled", True)
    
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    
    is_authenticated = False
    if not auth_enabled:
        is_authenticated = True
    elif token and verify_session_token(token):
        is_authenticated = True

    return {
        "auth_enabled": auth_enabled,
        "is_authenticated": is_authenticated,
        "app_name": cfg.get("app_name", "Minimal DSA Tracker"),
        "trip_name": cfg.get("trip_name", "3 Months DSA Sprint")
    }

@router.post("/login")
def login(req: LoginRequest):
    cfg = load_config()
    if not cfg.get("auth_enabled", True):
        token = generate_session_token()
        return {"success": True, "token": token, "message": "Auth not required"}
    
    if verify_pin(req.pin):
        token = generate_session_token()
        return {"success": True, "token": token, "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid PIN. Default is 1234 if not modified.")

@router.post("/update-pin")
def update_pin(req: PinUpdateRequest, authorization: Optional[str] = Header(None)):
    token = authorization[7:] if authorization and authorization.startswith("Bearer ") else None
    if not verify_session_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not verify_pin(req.old_pin):
        raise HTTPException(status_code=400, detail="Current PIN is incorrect.")
    
    new_pin = req.new_pin.strip()
    if len(new_pin) < 4:
        raise HTTPException(status_code=400, detail="New PIN must be at least 4 digits/characters.")
    
    cfg = load_config()
    cfg["auth_pin_hash"] = hash_pin(new_pin)
    save_config(cfg)
    
    new_token = generate_session_token()
    return {"success": True, "token": new_token, "message": "PIN updated successfully"}

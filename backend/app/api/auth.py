"""
PDF NEXUS - Auth API
User registration, login, and JWT session handling.
"""

import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.pdf_schemas import UserRegister, UserLogin, TokenResponse
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user_optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register_user(req: UserRegister):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (req.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
            
        user_id = str(uuid.uuid4())
        hashed = hash_password(req.password)
        conn.execute(
            "INSERT INTO users (id, email, hashed_password, full_name) VALUES (?, ?, ?, ?)",
            (user_id, req.email, hashed, req.full_name or req.email.split("@")[0])
        )
        
    token = create_access_token({"sub": user_id, "email": req.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": req.email, "full_name": req.full_name}
    }

@router.post("/login", response_model=TokenResponse)
def login_user(req: UserLogin):
    with get_db() as conn:
        row = conn.execute("SELECT id, email, hashed_password, full_name FROM users WHERE email = ?", (req.email,)).fetchone()
        if not row or not verify_password(req.password, row["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
            
    token = create_access_token({"sub": row["id"], "email": row["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": row["id"], "email": row["email"], "full_name": row["full_name"]}
    }

@router.get("/me")
def get_current_user_profile(user_payload: dict = Depends(get_current_user_optional)):
    if not user_payload:
        return {"authenticated": False, "mode": "guest"}
    return {"authenticated": True, "user": user_payload}

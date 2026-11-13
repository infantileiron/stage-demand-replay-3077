from fastapi import APIRouter, Depends, HTTPException
from src.schemas.auth import LoginRequest
from src.utils.database import list_rows
from src.utils.security import password_matches, token_for
from src.utils.dependencies import current_user

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login")
def login(body: LoginRequest):
    user = next((u for u in list_rows("users") if u["email"] == body.email), None)
    if not user or not password_matches(body.password, user["password_hash"]): raise HTTPException(401, "账号或密码错误")
    return {"access_token": token_for(user), "token_type": "bearer", "user": {k:v for k,v in user.items() if k != "password_hash"}}

@router.get("/me")
def me(user=Depends(current_user)): return user

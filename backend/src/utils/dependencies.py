from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.utils.security import decode_token
from src.constants.enums import Role
from src.utils.database import get_row

bearer = HTTPBearer(auto_error=False)

def current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not credentials: raise HTTPException(401, "请先登录")
    try:
        user = get_row("users", decode_token(credentials.credentials))
    except Exception:
        raise HTTPException(401, "登录已过期，请重新登录")
    request.state.user = user
    return {k:v for k,v in user.items() if k != "password_hash"}

def writer(user=Depends(current_user)):
    if user["role"] not in (Role.ADMIN.value, Role.ANALYST.value): raise HTTPException(403, "仅分析员或管理员可执行")
    return user

def administrator(user=Depends(current_user)):
    if user["role"] != Role.ADMIN.value: raise HTTPException(403, "仅管理员可审批")
    return user

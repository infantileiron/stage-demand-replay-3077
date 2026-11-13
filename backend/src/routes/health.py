from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.utils.database import connection,execute,list_rows
from src.utils.dependencies import administrator
from src.utils import queue
router=APIRouter()

@router.get("/health")
def health():
    try:
        with connection() as db: execute(db,"SELECT 1")
        if not queue.ping(): raise RuntimeError("redis")
        return {"status":"ok","db":"ok","redis":"ok"}
    except Exception: return JSONResponse({"status":"unavailable"},status_code=503)

@router.get("/audit")
def audit(user=Depends(administrator)): return list_rows("audit")[:100]

from fastapi import APIRouter, Depends
from src.schemas.report import ReportCreate
from src.controllers import report as controller
from src.utils.dependencies import current_user,writer,administrator
router=APIRouter(prefix="/reports",tags=["reports"])

@router.get("")
def listing(user=Depends(current_user)): return controller.listing()

@router.post("",status_code=201)
def create(body:ReportCreate,user=Depends(writer)): return controller.create(body)

@router.get("/{ident}/download")
def download(ident: int, user=Depends(current_user)): return controller.download(ident)

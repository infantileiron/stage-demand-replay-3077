from datetime import date
from fastapi import APIRouter,Depends
from src.controllers import schedule as controller
from src.schemas.schedule import ScheduleCreate,ScheduleToggle
from src.utils.dependencies import current_user,administrator
router=APIRouter(prefix="/schedules",tags=["站内报送"])

@router.get("")
def listing(user=Depends(current_user)):return controller.listing()

@router.post("",status_code=201)
def create(body:ScheduleCreate,user=Depends(administrator)):return controller.create(body)

@router.post("/{ident}/toggle")
def toggle(ident:int,body:ScheduleToggle,user=Depends(administrator)):return controller.toggle(ident,body)

@router.get("/{ident}/deliveries/{business_date}/download")
def download(ident:int,business_date:date,user=Depends(current_user)):return controller.download(ident,business_date.isoformat())

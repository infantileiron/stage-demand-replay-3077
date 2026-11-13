from fastapi import APIRouter, Depends
from src.schemas.plan import PlanCreate
from src.controllers import plan as controller
from src.utils.dependencies import current_user,writer,administrator
router=APIRouter(prefix="/plans",tags=["plans"])

@router.get("")
def listing(user=Depends(current_user)): return controller.listing()

@router.post("",status_code=201)
def create(body:PlanCreate,user=Depends(writer)): return controller.create(body)

@router.post("/{ident}/approve")
def approve(ident: int, user=Depends(administrator)): return controller.approve(ident,user)

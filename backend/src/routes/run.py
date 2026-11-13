from fastapi import APIRouter, Depends
from src.schemas.run import RunCreate
from src.controllers import run as controller
from src.utils.dependencies import current_user,writer,administrator
router=APIRouter(prefix="/runs",tags=["runs"])

@router.get("")
def listing(user=Depends(current_user)): return controller.listing()

@router.post("",status_code=201)
def create(body:RunCreate,user=Depends(writer)): return controller.create(body)

@router.get("/{ident}")
def detail(ident: int, user=Depends(current_user)): return controller.detail(ident)

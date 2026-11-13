from fastapi import APIRouter, Depends
from src.schemas.dataset import DatasetCreate
from src.controllers import dataset as controller
from src.utils.dependencies import current_user,writer,administrator
router=APIRouter(prefix="/datasets",tags=["datasets"])

@router.get("")
def listing(user=Depends(current_user)): return controller.listing()

@router.post("",status_code=201)
def create(body:DatasetCreate,user=Depends(writer)): return controller.create(body)

@router.get("/{ident}")
def detail(ident: int, user=Depends(current_user)): return controller.detail(ident)

from fastapi import APIRouter, Depends
from src.schemas.scenario import ScenarioCreate
from src.controllers import scenario as controller
from src.utils.dependencies import current_user,writer,administrator
router=APIRouter(prefix="/scenarios",tags=["scenarios"])

@router.get("")
def listing(user=Depends(current_user)): return controller.listing()

@router.post("",status_code=201)
def create(body:ScenarioCreate,user=Depends(writer)): return controller.create(body)

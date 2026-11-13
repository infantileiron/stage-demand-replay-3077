from src.services import plan as service
from src.utils.database import get_row

def listing(): return service.list_plans()
def create(body): return service.create(body)

def approve(ident,user): return service.approve(ident,user)

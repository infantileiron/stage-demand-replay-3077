from src.services import run as service
from src.utils.database import get_row

def listing(): return service.list_runs()
def create(body): return service.create(body)

def detail(ident): return get_row("runs",ident)

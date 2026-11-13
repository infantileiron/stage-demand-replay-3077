from src.services import dataset as service
from src.utils.database import get_row

def listing(): return service.list_datasets()
def create(body): return service.create(body)

def detail(ident): return service.detail(ident)

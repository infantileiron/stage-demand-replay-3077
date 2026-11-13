from src.services import scenario as service
from src.utils.database import get_row

def listing(): return service.list_scenarios()
def create(body): return service.create(body)

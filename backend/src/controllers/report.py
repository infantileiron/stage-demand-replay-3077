from src.services import report as service
from src.utils.database import get_row

def listing(): return service.list_reports()
def create(body): return service.create(body)

def download(ident):
    from fastapi.responses import Response
    return Response(service.export(ident),media_type="text/csv; charset=utf-8",headers={"Content-Disposition":f'attachment; filename="stage-demand-{ident}.csv"'})

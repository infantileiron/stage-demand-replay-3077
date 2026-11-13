from fastapi.responses import Response
from src.services import schedule as service

def listing():return service.listing()
def create(body):return service.create(body)
def toggle(ident,body):return service.toggle(ident,body.enabled)
def download(ident,business_date):
    return Response(service.download(ident,business_date),media_type="text/csv; charset=utf-8",headers={"Content-Disposition":f'attachment; filename="delivery-{ident}-{business_date}.csv"'})

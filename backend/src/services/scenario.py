from fastapi import HTTPException
from src.models.scenario import Scenario
from src.utils.database import list_rows, get_row, insert_row
from src.services.dataset import detail

def list_scenarios(): return list_rows(Scenario.table)
def create(body):
    data=body.model_dump()
    source=detail(data["dataset_id"])
    if len([r for r in source["rows"] if r["venue"]==data["venue"]])<70: raise HTTPException(422,"所选厅至少需要70天观测")
    return insert_row(Scenario.table,data["name"],Scenario(**data).payload())

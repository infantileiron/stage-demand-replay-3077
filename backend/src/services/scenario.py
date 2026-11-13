from fastapi import HTTPException
from src.models.scenario import Scenario
from src.utils.database import list_rows, get_row, insert_row
from src.services.dataset import detail

def list_scenarios(): return list_rows(Scenario.table)
def create(body):
    data=body.model_dump(mode="json")
    source=detail(data["dataset_id"])
    venue_rows=[r for r in source["rows"] if r["venue"]==data["venue"]]
    cutoff=data.get("cutoff_date")
    if cutoff:
        if len([r for r in venue_rows if r["date"]<=cutoff])<70: raise HTTPException(422,"截至复盘截止日，该厅可用历史不足70天，无法计算")
    elif len(venue_rows)<70: raise HTTPException(422,"所选厅至少需要70天观测")
    return insert_row(Scenario.table,data["name"],Scenario(**data).payload())

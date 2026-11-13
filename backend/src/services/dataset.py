from fastapi import HTTPException
from src.models.dataset import Dataset
from src.utils.database import list_rows, get_row, insert_row

def list_datasets():
    return [{k:v for k,v in d.items() if k != "rows"} for d in list_rows(Dataset.table)]

def detail(ident): return get_row(Dataset.table, ident)

def validate_rows(rows):
    seen = set()
    for row in rows:
        key = (str(row["date"]), row["venue"])
        if key in seen: raise HTTPException(422, "同一厅同一天不可重复")
        seen.add(key)
        if row["attendance"] > row["capacity"]: raise HTTPException(422, "到场人数不能超过容量")
    return rows

def create(body):
    data = body.model_dump(mode="json")
    validate_rows(data["rows"])
    data["row_count"] = len(data["rows"])
    data["venues"] = sorted({r["venue"] for r in data["rows"]})
    return insert_row(Dataset.table, data["name"], Dataset(**data).payload())

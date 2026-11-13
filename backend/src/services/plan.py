from fastapi import HTTPException
from src.models.plan import Plan
from src.constants.enums import ReviewStatus,RunStatus
from src.utils.database import list_rows,get_row,insert_row,update_row

def list_plans(): return list_rows(Plan.table)

def create(body):
    run=get_row("runs",body.run_id)
    if run["status"]!=RunStatus.COMPLETED.value: raise HTTPException(409,"仅已完成预测可生成排班建议")
    scenario=get_row("scenarios",run["scenario_id"])
    return insert_row(Plan.table,body.name,Plan(name=body.name,run_id=run["id"],venue=scenario["venue"],days=run["result"]["forecast"],status=ReviewStatus.DRAFT.value,approved_by=None).payload())

def approve(ident,user):
    plan=get_row(Plan.table,ident)
    if plan["status"]==ReviewStatus.APPROVED.value: return plan
    return update_row(Plan.table,ident,{"status":ReviewStatus.APPROVED.value,"approved_by":user["email"]})

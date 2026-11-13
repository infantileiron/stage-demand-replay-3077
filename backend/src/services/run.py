from uuid import uuid4
from fastapi import HTTPException
from src.models.run import Run
from src.constants.enums import RunStatus
from src.utils.database import list_rows,get_row,insert_row,update_row
from src.utils import queue
from src.services.forecast import analyze

def list_runs(): return list_rows(Run.table)

def create(body):
    get_row("scenarios",body.scenario_id)
    active=[r for r in list_runs() if r["status"] in (RunStatus.QUEUED.value,RunStatus.RUNNING.value)]
    if len(active)>=10: raise HTTPException(429,"队列最多10个任务，请等待后重试")
    run=insert_row(Run.table,uuid4().hex,Run(scenario_id=body.scenario_id,status=RunStatus.QUEUED.value,result=None,error=None).payload())
    try: queue.enqueue(run["id"])
    except Exception:
        update_row(Run.table,run["id"],{"status":RunStatus.FAILED.value,"error":"Redis 队列不可用，可恢复后新建任务"})
        raise HTTPException(503,"任务未入队，请检查Redis后重试")
    return run

def process(ident):
    run=get_row(Run.table,ident)
    if run["status"]!=RunStatus.QUEUED.value: return run
    update_row(Run.table,ident,{"status":RunStatus.RUNNING.value})
    try:
        scenario=get_row("scenarios",run["scenario_id"])
        dataset=get_row("datasets",scenario["dataset_id"])
        result=analyze(dataset["rows"],scenario)
        return update_row(Run.table,ident,{"status":RunStatus.COMPLETED.value,"result":result,"error":None})
    except Exception as exc:
        return update_row(Run.table,ident,{"status":RunStatus.FAILED.value,"error":str(exc)[:400]})

def verify(ident, body):
    """Read-only check of a completed run against an observation set; never mutates the run."""
    run=get_row(Run.table,ident)
    if run["status"]!=RunStatus.COMPLETED.value or not run.get("result"):
        raise HTTPException(409,"仅已完成的计算可以核验实到记录")
    dataset=get_row("datasets",body.dataset_id)
    result=run["result"]
    venue=result["venue"]
    actuals={r["date"]:r["attendance"] for r in dataset["rows"] if r["venue"]==venue}
    pairs,missing=[],[]
    for day in result["forecast"]:
        actual=actuals.get(day["date"])
        if actual is None: missing.append(day["date"])
        else: pairs.append({"date":day["date"],"prediction":day["prediction"],"lower":day["lower"],"upper":day["upper"],"actual":actual})
    complete=not missing
    for pair in pairs: pair["error"]=round(pair["actual"]-pair["prediction"],1) if complete else None
    mae=coverage=None
    if complete:
        mae=round(sum(abs(p["error"]) for p in pairs)/len(pairs),2)
        coverage=round(sum(1 for p in pairs if p["lower"]<=p["actual"]<=p["upper"])/len(pairs),3)
    return {"run_id":run["id"],"dataset_id":dataset["id"],"dataset_name":dataset["name"],"venue":venue,
        "pairs":pairs,"missing":missing,"complete":complete,"mae":mae,"coverage":coverage}

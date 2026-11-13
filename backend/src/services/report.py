import csv
import io
from fastapi import HTTPException
from src.models.report import Report
from src.utils.database import list_rows,get_row,insert_row

def list_reports(): return list_rows(Report.table)

def create(body):
    plan=get_row("plans",body.plan_id)
    if plan["status"]!="approved": raise HTTPException(409,"请管理员先审批排班建议")
    return insert_row(Report.table,body.title,Report(title=body.title,plan_id=plan["id"],venue=plan["venue"],days=plan["days"],status="approved").payload())

def export(ident):
    report=get_row(Report.table,ident)
    stream=io.StringIO(); stream.write("\ufeff")
    writer=csv.writer(stream);writer.writerow(["日期","场馆","预测人数","90%下界","90%上界","建议引导员"])
    for r in report["days"]: writer.writerow([r["date"],report["venue"],r["prediction"],r["lower"],r["upper"],r["ushers"]])
    return stream.getvalue()

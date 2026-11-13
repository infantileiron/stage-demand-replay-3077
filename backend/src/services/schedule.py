"""Daily station-local delivery. No emails, external webhooks or recipients."""
import csv
import io
import logging
from datetime import datetime,time,timedelta,timezone
from fastapi import HTTPException
from src.models.schedule import DeliverySchedule
from src.utils.database import list_rows,get_row,insert_row,update_row

SHANGHAI=timezone(timedelta(hours=8))

def clock(): return datetime.now(SHANGHAI)

def next_occurrence(daily_time,now):
    hour,minute=map(int,daily_time.split(":"))
    candidate=datetime.combine(now.astimezone(SHANGHAI).date(),time(hour,minute),SHANGHAI)
    if candidate<=now: candidate+=timedelta(days=1)
    return candidate.isoformat()

def listing():
    snapshots=list_rows("delivery_snapshots")
    return [{**schedule,"deliveries":[{"id":s["id"],"business_date":s["business_date"],"delivered_at":s["delivered_at"],"row_count":len(s["rows"])} for s in snapshots if s["schedule_id"]==schedule["id"]]} for schedule in list_rows("schedules")]

def create(body):
    if body.source_report_id is not None:
        report=get_row("reports",body.source_report_id)
        if report["status"]!="approved": raise HTTPException(409,"仅确认纪要可报送")
    schedule=DeliverySchedule(name=body.name,source_report_id=body.source_report_id,daily_time=body.daily_time,
       enabled=body.enabled,next_run=next_occurrence(body.daily_time,clock()))
    return insert_row("schedules",body.name,schedule.payload())

def toggle(ident,enabled):
    schedule=get_row("schedules",ident)
    changes={"enabled":enabled,"last_error":None}
    if enabled:changes["next_run"]=next_occurrence(schedule["daily_time"],clock())
    return update_row("schedules",ident,changes)

def source_reports(schedule):
    if schedule["source_report_id"] is not None:
        return [get_row("reports",schedule["source_report_id"])]
    # Latest approved report per venue; avoids double counting archived plan versions.
    selected={}
    for report in list_rows("reports"):
        if report["status"]=="approved" and report["venue"] not in selected:selected[report["venue"]]=report
    if not selected: raise ValueError("没有已确认纪要，报送等待数据")
    return list(selected.values())

def pivot_rows(reports):
    grouped={}
    for report in reports:
        plan=get_row("plans",report["plan_id"])
        run=get_row("runs",plan["run_id"])
        capacity=run["result"]["capacity"]
        for day in report["days"]:
            key=(day["date"],report["venue"])
            if key in grouped:raise ValueError("同一厅同一天有多份纪要，请先选择唯一来源")
            grouped[key]={"date":day["date"],"venue":report["venue"],"prediction":day["prediction"],
                "capacity":capacity,"occupancy_rate":round(day["prediction"]/capacity*100,2),"ushers":day["ushers"]}
    return [grouped[key] for key in sorted(grouped)]

def run_due(now=None):
    now=(now or clock()).astimezone(SHANGHAI)
    delivered=[]
    for schedule in list_rows("schedules"):
        if not schedule["enabled"] or datetime.fromisoformat(schedule["next_run"])>now:continue
        # Business date is the scheduled due date, so a late restart does not mislabel a snapshot.
        due=datetime.fromisoformat(schedule["next_run"]).astimezone(SHANGHAI)
        business_date=due.date().isoformat()
        natural_key=str(schedule["id"])+":"+business_date
        try:
            existing=next((s for s in list_rows("delivery_snapshots") if s["key"]==natural_key),None)
            if existing: snapshot=existing
            else:
                snapshot=insert_row("delivery_snapshots",natural_key,{"schedule_id":schedule["id"],
                    "business_date":business_date,"delivered_at":now.isoformat(),"rows":pivot_rows(source_reports(schedule)),
                    "metrics":{"prediction":"日到场人数点预测（人）","occupancy_rate":"预测人数/场馆容量×100%","ushers":"ceil(预测90%上界/每引导员人数)，最少2名"}},preserve=True)
            update_row("schedules",schedule["id"],{"last_run":now.isoformat(),"last_error":None,
                 "next_run":next_occurrence(schedule["daily_time"],now)})
            delivered.append(snapshot["id"])
        except Exception as exc:
            logging.exception("Station-local delivery failed")
            update_row("schedules",schedule["id"],{"last_error":str(exc)[:300]})
    return delivered

def download(ident,business_date):
    get_row("schedules",ident)
    snapshot=next((s for s in list_rows("delivery_snapshots") if s["key"]==str(ident)+":"+business_date),None)
    if not snapshot: raise HTTPException(404,"尚无该日快照，请等待报送时刻")
    rows=snapshot["rows"];venues=sorted({row["venue"] for row in rows});dates=sorted({row["date"] for row in rows})
    lookup={(row["date"],row["venue"]):row for row in rows}
    output=io.StringIO();output.write("\ufeff");writer=csv.writer(output)
    writer.writerow(["预演日期"]+[venue+" / "+metric for venue in venues for metric in ("预测人数","预测上座率(%)","引导员建议")])
    for day in dates:
        values=[]
        for venue in venues:
            row=lookup.get((day,venue))
            values.extend([row["prediction"],row["occupancy_rate"],row["ushers"]] if row else ["","",""])
        writer.writerow([day]+values)
    return output.getvalue()

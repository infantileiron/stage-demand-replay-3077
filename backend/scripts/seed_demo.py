"""Natural-key insert-only seed; never overwrites user edits."""
from datetime import date,timedelta
import math
import random
from src.utils.database import init_db,insert_row,list_rows
from src.utils.security import password_hash
from src.services.forecast import analyze

def demo_rows():
    rng=random.Random(261104)
    rows=[]
    for venue,capacity,base in (("大剧场",800,410),("黑匣子",300,142),("实验厅",500,225)):
        for i in range(420):
            day=date(2025,9,17)+timedelta(days=i)
            weekend=day.weekday()>=5
            event=int(i%31 in (8,9))
            people=base+95*weekend+65*event+i*.09+22*math.sin(i*2*math.pi/365)+rng.gauss(0,14)
            rows.append({"date":day.isoformat(),"venue":venue,"attendance":int(max(0,min(capacity,round(people)))),"capacity":capacity,"event":event})
    return rows

def seed():
    init_db()
    for role,name in (("admin","陈溪·值班主管"),("analyst","林予·排演分析"),("viewer","周末值班组")):
        insert_row("users",role+"@stage.local",{"email":role+"@stage.local","name":name,"role":role,"password_hash":password_hash("Stage2611!")},preserve=True)
    rows=demo_rows()
    dataset=insert_row("datasets","拾光剧场420天到场记录",{"name":"拾光剧场420天到场记录","filename":"attendance_daily_202611.csv","row_count":1260,"venues":["大剧场","黑匣子","实验厅"],"rows":rows},preserve=True)
    first=insert_row("scenarios","11月常规排演",{"name":"11月常规排演","dataset_id":dataset["id"],"venue":"大剧场","horizon":7,"weekend_event":False,"people_per_usher":65},preserve=True)
    insert_row("scenarios","黑匣子周末特别场",{"name":"黑匣子周末特别场","dataset_id":dataset["id"],"venue":"黑匣子","horizon":14,"weekend_event":True,"people_per_usher":45},preserve=True)
    existing=next((r for r in list_rows("runs") if r["key"]=="seed-run-november"),None)
    result=existing["result"] if existing else analyze(dataset["rows"],first)
    run=insert_row("runs","seed-run-november",{"scenario_id":first["id"],"status":"completed","error":None,"result":result},preserve=True)
    plan=insert_row("plans","11月常规场引导员草案",{"name":"11月常规场引导员草案","run_id":run["id"],"venue":"大剧场","days":result["forecast"],"status":"approved","approved_by":"admin@stage.local"},preserve=True)
    insert_row("reports","11月排演需求预演纪要",{"title":"11月排演需求预演纪要","plan_id":plan["id"],"venue":"大剧场","days":plan["days"],"status":"approved"},preserve=True)
    from src.services.schedule import next_occurrence,clock
    insert_row("schedules","每日08:30排演册站内报送",{"name":"每日08:30排演册站内报送","source_report_id":None,"daily_time":"08:30","enabled":True,"next_run":next_occurrence("08:30",clock()),"last_run":None,"last_error":None},preserve=True)
    return {table:len(list_rows(table)) for table in ("users","datasets","scenarios","runs","plans","reports","schedules","delivery_snapshots")}

if __name__=="__main__": print(seed())

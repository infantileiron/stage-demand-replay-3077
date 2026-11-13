"""Leak-free recursive ridge forecasting and held-out residual interval calibration."""
from datetime import date, timedelta
import math
import numpy as np

ALPHAS = (0.1, 1.0, 10.0, 100.0)

def feature(values, day, event, index):
    return [values[-1], values[-7], float(np.mean(values[-7:])), float(day.weekday() >= 5), float(event), index / 365]

def fit(rows, alpha):
    values = [r["attendance"] for r in rows]
    x = np.array([feature(values[:i], date.fromisoformat(rows[i]["date"]), rows[i].get("event",0), i) for i in range(7,len(rows))])
    y = np.asarray(values[7:], dtype=float)
    mean = x.mean(axis=0); scale = x.std(axis=0); scale[scale < 1e-10] = 1
    z = np.column_stack([np.ones(len(x)), (x-mean)/scale])
    penalty = np.eye(z.shape[1]) * alpha; penalty[0,0] = 0
    weights = np.linalg.solve(z.T@z+penalty, z.T@y)
    return mean, scale, weights

def predict(rows, future, alpha):
    mean, scale, weights = fit(rows, alpha)
    values = [float(r["attendance"]) for r in rows]
    capacity = int(rows[-1]["capacity"])
    result = []
    for i, row in enumerate(future):
        x = np.asarray(feature(values, date.fromisoformat(row["date"]), row.get("event",0), len(values)))
        value = float(np.clip(np.r_[1., (x-mean)/scale] @ weights, 0, capacity))
        values.append(value)
        result.append(value)
    return result

def seasonal_naive(rows, length):
    values = [float(r["attendance"]) for r in rows]
    result = []
    for _ in range(length):
        result.append(values[-7]); values.append(values[-7])
    return result

def finite_quantile(errors, coverage=.90):
    if len(errors) < 7: raise ValueError("区间校准至少需要7个残差")
    rank = min(len(errors), math.ceil((len(errors)+1)*coverage))
    return float(np.sort(np.asarray(errors))[rank-1])

def analyze(rows, scenario):
    data = sorted([r for r in rows if r["venue"] == scenario["venue"]], key=lambda r:r["date"])
    if len(data) < 70: raise ValueError("所选厅至少需要70天连续历史")
    dates = [date.fromisoformat(r["date"]) for r in data]
    if len(set(dates)) != len(dates): raise ValueError("历史含重复日期")
    if any(b-a != timedelta(days=1) for a,b in zip(dates, dates[1:])): raise ValueError("历史日期有缺口，请补齐后重新导入")
    if any(not np.isfinite(r["attendance"]) or r["attendance"]<0 or r["attendance"]>r["capacity"] for r in data): raise ValueError("人数或容量无效")
    if len({r["capacity"] for r in data}) != 1: raise ValueError("当前模型要求历史容量一致")
    horizon = scenario["horizon"]
    if horizon not in (7,14): raise ValueError("预测天数仅支持7或14")
    # Three expanding folds for alpha selection. Final two weeks are untouched calibration/holdout.
    calibration_start = len(data)-14
    origins = [calibration_start-42, calibration_start-28, calibration_start-14]
    scores=[]
    for alpha in ALPHAS:
        folds=[]
        for origin in origins:
            predicted=predict(data[:origin], data[origin:origin+14], alpha)
            folds.append(float(np.mean(np.abs(np.asarray(predicted)-[r["attendance"] for r in data[origin:origin+14]]))))
        scores.append({"alpha":alpha,"mae":float(np.mean(folds)),"fold_mae":folds})
    alpha=min(scores,key=lambda item:item["mae"])["alpha"]
    heldout=data[calibration_start:]
    back=predict(data[:calibration_start],heldout,alpha)
    actual=np.array([r["attendance"] for r in heldout])
    residual=np.abs(actual-back); radius=finite_quantile(residual)
    baseline=seasonal_naive(data[:calibration_start],len(heldout))
    future=[]
    for i in range(1,horizon+1):
        day=dates[-1]+timedelta(days=i)
        future.append({"date":day.isoformat(),"event":int(scenario.get("weekend_event",False) and day.weekday()>=5)})
    forecast=predict(data,future,alpha)
    capacity=data[-1]["capacity"]
    predictions=[{"date":row["date"],"event":row["event"],"prediction":round(value,1),
       "lower":round(max(0,value-radius),1),"upper":round(min(capacity,value+radius),1),
       "ushers":max(2,math.ceil(min(capacity,value+radius)/scenario["people_per_usher"]))} for row,value in zip(future,forecast)]
    return {"alpha":alpha,"folds":scores,"mae":round(float(np.mean(residual)),2),
       "baseline_mae":round(float(np.mean(np.abs(actual-baseline))),2),"interval_radius":round(radius,2),
       "nominal_coverage":.90,"history_days":len(data),"venue":scenario["venue"],"capacity":capacity,
       "backtest":[{"date":row["date"],"actual":int(obs),"prediction":round(pred,1),"baseline":round(base,1)} for row,obs,pred,base in zip(heldout,actual,back,baseline)],
       "forecast":predictions,"history":[{"date":r["date"],"attendance":r["attendance"]} for r in data[-42:]],
       "split":{"tuning_last_date":data[calibration_start-1]["date"],"calibration_first_date":heldout[0]["date"],"training_last_date":data[-1]["date"]},
       "limitations":["模拟到场数据，不能替代运营判断", "区间来自最近14天递归残差，非独立同分布或漂移时不保证90%覆盖", "多步共用区间半径，远期不确定性可能低估"]}

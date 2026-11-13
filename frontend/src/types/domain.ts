export interface User { id:number; email:string; name:string; role:'admin'|'analyst'|'viewer' }
export interface Dataset { id:number;name:string;filename:string;row_count:number;venues:string[]; rows?:Attendance[] }
export interface Attendance { date:string;venue:string;attendance:number;capacity:number;event:number }
export interface Scenario { id:number; name:string;dataset_id:number;venue:string;horizon:number;weekend_event:boolean;people_per_usher:number }
export interface ForecastDay { date:string;prediction:number;lower:number;upper:number;ushers:number;event:number }
export interface Result { alpha:number;mae:number;baseline_mae:number;interval_radius:number;nominal_coverage:number;history_days:number;venue:string;capacity:number;forecast:ForecastDay[];backtest:{date:string;actual:number;prediction:number;baseline:number}[];history:{date:string;attendance:number}[];folds:{alpha:number;mae:number;fold_mae:number[]}[];limitations:string[];split:{tuning_last_date:string;calibration_first_date:string;training_last_date:string} }
export interface Run { id:number;scenario_id:number;status:'queued'|'running'|'completed'|'failed';result:Result|null;error:string|null;created_at:string }
export interface Plan { id:number;name:string;run_id:number;venue:string;days:ForecastDay[];status:'draft'|'approved';approved_by:string|null }
export interface Report { id:number;title:string;plan_id:number;venue:string;days:ForecastDay[];status:string }

export interface DeliverySchedule { id:number;name:string;source_report_id:number|null;daily_time:string;enabled:boolean;next_run:string;last_run:string|null;last_error:string|null;deliveries:{id:number;business_date:string;delivered_at:string;row_count:number}[] }

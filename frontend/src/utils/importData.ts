import type {Attendance} from '../types/domain'
// JSON is chosen deliberately: typed structured input avoids ambiguous CSV date/locale coercion.
export async function readDataset(file:File):Promise<Attendance[]>{if(file.size>1500000)throw new Error('文件上限为1.5MB');const rows=JSON.parse(await file.text());if(!Array.isArray(rows))throw new Error('请选择由观测行组成的JSON数组');return rows}

import {request,download} from './client'
import type {Report} from '../types/domain'
export const list=()=>request<Report[]>('/reports')
export const create=(body:unknown)=>request<Report>('/reports',body)

export const exportReport=(id:number)=>download('/reports/'+id+'/download','stage-demand-'+id+'.csv')

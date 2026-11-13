import {request,download} from './client'
import type {Plan} from '../types/domain'
export const list=()=>request<Plan[]>('/plans')
export const create=(body:unknown)=>request<Plan>('/plans',body)

export const approve=(id:number)=>request<Plan>('/plans/'+id+'/approve',{})

import {request,download} from './client'
import type {Run,Verification} from '../types/domain'
export const list=()=>request<Run[]>('/runs')
export const create=(body:unknown)=>request<Run>('/runs',body)

export const get=(id:number)=>request<Run>('/runs/'+id)
export const verify=(id:number,body:unknown)=>request<Verification>('/runs/'+id+'/verify',body)

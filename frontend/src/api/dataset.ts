import {request,download} from './client'
import type {Dataset} from '../types/domain'
export const list=()=>request<Dataset[]>('/datasets')
export const create=(body:unknown)=>request<Dataset>('/datasets',body)

export const get=(id:number)=>request<Dataset>('/datasets/'+id)

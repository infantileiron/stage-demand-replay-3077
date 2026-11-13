import {request,download} from './client'
import type {Scenario} from '../types/domain'
export const list=()=>request<Scenario[]>('/scenarios')
export const create=(body:unknown)=>request<Scenario>('/scenarios',body)

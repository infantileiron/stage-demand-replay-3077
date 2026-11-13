import {ref,computed} from 'vue'
import {request} from '../api/client'
import type {User} from '../types/domain'
export const user=ref<User|null>(null)
export const canWrite=computed(()=>user.value?.role==='admin'||user.value?.role==='analyst')
export const canApprove=computed(()=>user.value?.role==='admin')
export async function login(email:string,password:string){const data=await request<{access_token:string;user:User}>('/auth/login',{email,password});localStorage.setItem('stage-token',data.access_token);user.value=data.user}
export function logout(){localStorage.removeItem('stage-token');user.value=null}
export async function restore(){if(localStorage.getItem('stage-token')){try{user.value=await request<User>('/auth/me')}catch{logout()}}}
window.addEventListener('stage-expired',logout)

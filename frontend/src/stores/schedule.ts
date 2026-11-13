import {ref} from 'vue'
import type {DeliverySchedule} from '../types/domain'
import * as api from '../api/schedule'
export const schedules=ref<DeliverySchedule[]>([])
export async function loadSchedules(){schedules.value=await api.list()}
export {api as scheduleApi}

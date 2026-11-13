import {ref} from 'vue'
import type {Plan} from '../types/domain'
import * as api from '../api/plan'
export const plans=ref<Plan[]>([])
export async function loadPlans(){plans.value=await api.list()}
export {api as planApi}

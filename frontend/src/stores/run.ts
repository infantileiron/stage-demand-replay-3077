import {ref} from 'vue'
import type {Run} from '../types/domain'
import * as api from '../api/run'
export const runs=ref<Run[]>([])
export async function loadRuns(){runs.value=await api.list()}
export {api as runApi}

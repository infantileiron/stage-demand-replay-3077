import {ref} from 'vue'
import type {Report} from '../types/domain'
import * as api from '../api/report'
export const reports=ref<Report[]>([])
export async function loadReports(){reports.value=await api.list()}
export {api as reportApi}

import {ref} from 'vue'
import type {Scenario} from '../types/domain'
import * as api from '../api/scenario'
export const scenarios=ref<Scenario[]>([])
export async function loadScenarios(){scenarios.value=await api.list()}
export {api as scenarioApi}

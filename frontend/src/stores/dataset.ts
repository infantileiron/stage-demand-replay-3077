import {ref} from 'vue'
import type {Dataset} from '../types/domain'
import * as api from '../api/dataset'
export const datasets=ref<Dataset[]>([])
export async function loadDatasets(){datasets.value=await api.list()}
export {api as datasetApi}

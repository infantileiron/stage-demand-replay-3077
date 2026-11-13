import {ref} from 'vue'
export const currentPage=ref(location.hash.slice(1)||'overview')
window.addEventListener('hashchange',()=>currentPage.value=location.hash.slice(1)||'overview')
export const nav=[['overview','01','排演手记'],['datasets','02','历史观测'],['scenarios','03','情景预演'],['results','04','回测与解释'],['plans','05','值班编排'],['schedules','06','报送计划']]
export function navigate(page:string){location.hash=page}

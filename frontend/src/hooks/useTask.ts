import {ref} from 'vue'
export function useTask(){const busy=ref(false),error=ref(''),notice=ref('');async function task(fn:()=>Promise<void>){busy.value=true;error.value='';notice.value='';try{await fn()}catch(e){error.value=e instanceof Error?e.message:String(e)}finally{busy.value=false}};return {busy,error,notice,task}}

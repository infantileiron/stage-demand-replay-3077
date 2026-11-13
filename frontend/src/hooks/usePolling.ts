import {onMounted,onUnmounted} from 'vue'
export function usePolling(fn:()=>Promise<void>,ms=2500){let timer:ReturnType<typeof setInterval>|undefined;onMounted(()=>{timer=setInterval(()=>{fn().catch(()=>{})},ms)});onUnmounted(()=>clearInterval(timer))}

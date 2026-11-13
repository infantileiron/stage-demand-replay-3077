export function token(){return localStorage.getItem('stage-token')||''}
export async function request<T>(path:string,body?:unknown):Promise<T>{
 const response=await fetch('/api'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token()},body:body===undefined?undefined:JSON.stringify(body)})
 if(!response.ok){let message='请求失败，请稍后重试';try{const data=await response.json();message=typeof data.detail==='string'?data.detail:'输入格式不正确，请检查必填项和数值范围'}catch{};if(response.status===401){localStorage.removeItem('stage-token');window.dispatchEvent(new Event('stage-expired'))}throw new Error(message)}
 return response.json()
}
export async function download(path:string,name:string){const r=await fetch('/api'+path,{headers:{Authorization:'Bearer '+token()}});if(!r.ok)throw new Error('下载失败，请重新登录后重试');const url=URL.createObjectURL(await r.blob());const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}

export const number=(value:number|undefined)=>value===undefined?'—':new Intl.NumberFormat('zh-CN',{maximumFractionDigits:1}).format(value)
export const shortDate=(value:string)=>value.slice(5)
export const timestamp=(value:string)=>new Date(value).toLocaleString('zh-CN',{hour12:false})

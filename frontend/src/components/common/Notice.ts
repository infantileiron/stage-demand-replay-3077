import {defineComponent} from 'vue'
export default defineComponent({props:{error:String,notice:String},template:`<div v-if="error" class="notice error" role="alert"><b>暂未完成</b> {{error}} <span>请调整后重试。</span></div><div v-if="notice" class="notice success" role="status">{{notice}}</div>`})

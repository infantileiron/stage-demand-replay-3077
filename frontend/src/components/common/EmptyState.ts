import {defineComponent} from 'vue'
export default defineComponent({props:{title:{type:String,default:'从一条记录开始'},text:String},template:`<div class="empty"><span>／</span><h3>{{title}}</h3><p>{{text}}</p><slot/></div>`})

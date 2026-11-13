import {defineComponent} from 'vue'
import {RUN_STATUS} from '../../constants/enums'
import {timestamp} from '../../utils/format'
export default defineComponent({props:{run:{type:Object,required:true}},setup(){return {RUN_STATUS,timestamp}},template:`<div class="run-strip"><span class="run-no">RUN / {{String(run.id).padStart(3,'0')}}</span><b>{{RUN_STATUS[run.status]}}</b><span>{{timestamp(run.created_at)}}</span><em v-if="run.error">{{run.error}}</em><slot/></div>`})

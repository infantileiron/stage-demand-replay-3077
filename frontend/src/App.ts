import {defineComponent,onMounted,computed} from 'vue'
import {user,restore,logout} from './stores/auth'
import {currentPage,nav} from './router'
import {ROLES} from './constants/enums'
import Login from './pages/Login'
import Overview from './pages/Overview'
import Datasets from './pages/Datasets'
import Scenarios from './pages/Scenarios'
import Results from './pages/Results'
import Plans from './pages/Plans'
import Schedules from './pages/Schedules'
const pages={overview:Overview,datasets:Datasets,scenarios:Scenarios,results:Results,plans:Plans,schedules:Schedules}
export default defineComponent({components:{Login},setup(){onMounted(restore);const page=computed(()=>pages[currentPage.value as keyof typeof pages]||Overview);return {user,logout,currentPage,nav,page,ROLES}},template:`<Login v-if="!user"/><div v-else class="app-shell"><aside class="sidebar"><a class="brand" href="#overview"><span class="brand-symbol">拾</span><span>拾光剧场<small>REHEARSAL NOTES</small></span></a><div class="sidebar-caption">场次需求预演 / 排演册</div><nav><a v-for="[key,no,label] in nav" :href="'#'+key" :class="{active:currentPage===key}"><small>{{no}}</small>{{label}}<span v-if="currentPage===key">↗</span></a></nav><div class="sidebar-foot"><p>研究让准备<br>多一点从容。</p><span>模拟运营数据 / 2026</span></div></aside><div class="workspace"><header class="topbar"><span>拾光 · 运营研究组</span><div><span>{{user.name}} <small>{{ROLES[user.role]}}</small></span><button class="quiet" @click="logout">退出</button></div></header><main class="main-content"><component :is="page"/></main><footer class="page-footer">SHIGUANG THEATRE / PLANNING STUDIES <span>历史是线索，预演保留边界。</span></footer></div></div>`})

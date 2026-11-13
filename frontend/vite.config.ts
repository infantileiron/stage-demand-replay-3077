import { defineConfig } from 'vite'
export default defineConfig({resolve:{alias:{vue:'vue/dist/vue.esm-bundler.js'}},server:{proxy:{'/api':{target:'http://127.0.0.1:19203',rewrite:p=>p.replace(/^\/api/,'')}}}})

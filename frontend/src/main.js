import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)


// 全局错误处理
app.config.errorHandler = (err) => {
  // 忽略 ResizeObserver 循环警告
  if (err.message && err.message.includes('ResizeObserver loop')) {
    return
  }
  // 其他错误正常处理
  console.error(err)
}

app.use(router)
app.use(ElementPlus)

app.mount('#app')
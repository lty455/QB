import { createRouter, createWebHistory } from 'vue-router'

// 简化路由，暂时不需要多个页面
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/entity-recognition',
    name: 'EntityRecognition',
    component: () => import('../views/EntityRecognitionView.vue')
  },
  {
    path: '/visual',
    name: 'Visual',
    component: () => import('../views/VisualView.vue')
  },
  {
    path: '/chat',
    name: 'ChatBox',
    component: () => import('../views/ChatBoxView.vue')
  },

  {
    path: '/about',
    name: 'About',
    component: () => import('../views/AboutView.vue')
  },
  {
  path: '/test',
  name: 'Test',
  component: () => import('@/views/TestEmbed.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
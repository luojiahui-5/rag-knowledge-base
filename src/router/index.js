import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/dashboard',
    component: () => import('../views/MainLayout.vue'),
    redirect: '/dashboard/overview',
    children: [
      {
        path: 'overview',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('../views/KnowledgeBase.vue'),
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('../views/DocumentManagement.vue'),
      },
      {
        path: 'ask',
        name: 'AskAI',
        component: () => import('../views/AskAI.vue'),
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/SystemSettings.vue'),
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 简易登录守卫（演示用，上线后替换为真实 token 校验）
router.beforeEach((to, from, next) => {
  const isLoggedIn = sessionStorage.getItem('auth')
  if (to.path.startsWith('/dashboard') && !isLoggedIn) {
    next('/login')
    return
  }
  // 管理员权限：仅 /dashboard/settings 需要 admin 角色
  if (to.path === '/dashboard/settings') {
    const role = sessionStorage.getItem('role')
    if (role !== 'admin') {
      next('/dashboard/overview')
      return
    }
  }
  next()
})

export default router

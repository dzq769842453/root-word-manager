import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件（稍后创建）
const Login = () => import('../views/Login.vue')
const RootWordList = () => import('../views/RootWordList.vue')
const RootWordApply = () => import('../views/RootWordApply.vue')
const DDLCheck = () => import('../views/DDLCheck.vue')
const RootWordAudit = () => import('../views/RootWordAudit.vue')

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/root-word/list',
    name: 'RootWordList',
    component: RootWordList,
    meta: { requiresAuth: true }
  },
  {
    path: '/root-word/apply',
    name: 'RootWordApply',
    component: RootWordApply,
    meta: { requiresAuth: true }
  },
  {
    path: '/root-word/ddl-check',
    name: 'DDLCheck',
    component: DDLCheck,
    meta: { requiresAuth: true }
  },
  {
    path: '/root-word/audit',
    name: 'RootWordAudit',
    component: RootWordAudit,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // 重定向到登录页面
  {
    path: '/',
    redirect: '/login'
  },
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      // 未登录，跳转到登录页面
      next('/login')
      return
    }
    
    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin) {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        if (user.role !== 'admin') {
          // 不是管理员，跳转到词根列表页面
          next('/root-word/list')
          return
        }
      } else {
        // 未登录，跳转到登录页面
        next('/login')
        return
      }
    }
  }
  next()
})

export default router

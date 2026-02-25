import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../store/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/verify-otp',
    name: 'VerifyOTP',
    component: () => import('../pages/VerifyOTP.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/registration',
    name: 'RegistrationForm',
    component: () => import('../pages/RegistrationForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../pages/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
  const isAuthenticated = authStore.isAuthenticated()
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/verify-otp') && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router

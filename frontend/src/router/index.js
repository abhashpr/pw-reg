import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../store/auth'

const routes = [
  {
    path: '/',
    redirect: '/results'
  },
  {
    path: '/login',
    redirect: '/results'
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
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
    path: '/admin',
    name: 'Admin',
    component: () => import('../pages/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/results',
    name: 'ResultsAdmin',
    component: () => import('../pages/ResultsAdmin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/results',
    name: 'ResultsLookup',
    component: () => import('../pages/ResultsLookup.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/results'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
  const isAuthenticated = authStore.isAuthenticated()
  
    // If user is trying to access an admin-only route while unauthenticated,
    // redirect to the login page and include an admin flag so the login flow
    // can present admin-specific authentication.
    if (to.meta.requiresAdmin && !isAuthenticated) {
      return next({ path: '/admin/login', query: { admin: '1', redirect: to.fullPath } })
    }

    // Handle access to the login page:
    // - Authenticated non-admins should not see `/login` (send to dashboard)
    // - Unauthenticated users are allowed to visit `/login` (so admins can sign in)
    // - A query param `?admin=1` indicates an admin login intent and is allowed
    if (to.path === '/admin/login') {
      if (isAuthenticated && !authStore.isAdmin()) {
        return next('/dashboard')
      }
      return next()
    }

    // Standard auth checks for other routes
    if (to.meta.requiresAuth && !isAuthenticated) {
      return next('/results')
    }

    if (to.meta.requiresAdmin && !authStore.isAdmin()) {
      return next('/dashboard')
    }

    if ((to.path === '/verify-otp') && isAuthenticated) {
      return next('/dashboard')
    }

    return next()
})

export default router

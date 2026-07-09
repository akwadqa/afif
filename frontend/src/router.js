import { createRouter, createWebHistory } from 'vue-router'

function getSessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  const user = cookies.get('user_id')
  return user && user !== 'Guest' ? user : null
}

const routes = [
  {
    path: '/signin',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'Login',
        component: () => import('@/pages/Login.vue'),
        meta: { public: true },
      },
    ],
  },

  {
    path: '/register',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'Register',
        component: () => import('@/pages/Register.vue'),
        meta: { public: true },
      },
    ],
  },

  {
    path: '/forgot-password',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'ResetPassword',
        component: () => import('@/pages/ResetPassword.vue'),
        meta: { public: true },
      },
    ],
  },

  {
    path: '/',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/beneficiary-profile',
      },
      {
        path: 'beneficiary-profile',
        name: 'Home',
        component: () => import('@/pages/Home.vue'),
      },
      {
        path: 'request',
        name: 'Request',
        component: () => import('@/pages/Request.vue'),
      },
      {
        path: 'account',
        name: 'Account',
        component: () => import('@/pages/Account.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = !!getSessionUser()

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login' })
  } else if ((to.name === 'Login' || to.name === 'Register' || to.name === 'ResetPassword') && isLoggedIn) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import HomeView from '../views/HomeView.vue'
import PersonStoreView from '../views/PersonStoreView.vue'
import PhotoDetailView from '../views/PhotoDetailView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { 
        requiresAuth: false,
        title: '首页',
        showNavbar: true
      }
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: PersonStoreView,
      meta: { 
        requiresAuth: true,
        title: '个人仓库',
        showNavbar: true
      }
    },
    {
      path:'/photodetail/:id',
      name:'photodetail',
      component:PhotoDetailView,
      props: true,
      meta: { 
        requiresAuth: false,
        showNavbar: true
      }
    },
    {
      path:'/register',
      name:'register',
      component:RegisterView,
      meta: { 
        requiresAuth: false,
        showNavbar: false
      }
    },
    {
      path:'/login',
      name:'login',
      component:LoginView,
      meta: { 
        requiresAuth: false,
        showNavbar: false
      }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/Profile.vue'),
      meta: { 
        requiresAuth: true,
        title: '个人中心',
        showNavbar: true
      }
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  // 如果目标页面不需要认证，直接放行
  if (!to.meta.requiresAuth) {
    next()
    return
  }

  // 需要认证的页面，检查登录状态
  const userStore = useUserStore()
  await userStore.initialize()

  if (!userStore.isLoggedIn) {
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
    return
  }

  next()
})

export default router

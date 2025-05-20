import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import PersonStoreView from '../views/PersonStoreView.vue'
import PhotoDetailView from '../views/PhotoDetailView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'personstore',
      component: PersonStoreView,
    },
    {
      path:'/photodetail/:id',
      name:'photodetail',
      component:PhotoDetailView,
      props: true
    },
    {
      path:'/register',
      name:'register',
      component:RegisterView,
      meta: { requiresAuth: false }
    },
    {
      path:'/login',
      name:'login',
      component:LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/Profile.vue'),
      meta: { 
        requiresAuth: true,
        title: '个人中心' 
      }
    },
    {
      path: '/gallery',
      name: 'Gallery',
      component: () => import('@/views/PersonStoreView.vue'),
      meta: { 
        requiresAuth: true,
        title: '个人仓库' 
      }
    }
  ],
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  userStore.initialize()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router

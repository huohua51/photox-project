<template>
    <nav class="navbar">
        <div class="nav-container">
            <!-- 网站Logo -->
            <router-link to="/" class="brand">
                <img src="/svg/logo.svg" alt="Logo" class="logo">
                <span>PhotoX</span>
            </router-link>

            <!-- 导航菜单 -->
            <div class="nav-menu">
                <router-link to="/" class="nav-item">首页</router-link>
                <router-link to="/gallery" class="nav-item">个人仓库</router-link>
                <div class="user-controls">
                    <!-- 未登录状态 -->
                    <div v-if="!isLoggedIn" class="auth-buttons">
                        <button @click="openLogin" class="auth-btn login">登录</button>
                        <button @click="openRegister" class="auth-btn register">注册</button>
                    </div>

                    <!-- 已登录状态 -->
                    <div v-else class="user-menu-wrapper" @mouseenter="showMenu = true" @mouseleave="showMenu = false">
                        <div class="user-avatar">
                            <img :src="user.avatar || defaultAvatar" alt="用户头像" @error="handleAvatarError">
                        </div>

                        <!-- 下拉菜单 -->
                        <transition name="slide-fade">
                            <div v-show="showMenu" class="user-menu">
                                <div class="user-info">
                                    <p class="username">{{ user.name }}</p>
                                    <p class="email">{{ user.email }}</p>
                                </div>
                                <div class="menu-items">
                                    <router-link to="/profile" class="menu-item">
                                        <img src="/svg/usericon.svg" class="icon" /> 个人中心
                                    </router-link>
                                    <!-- <router-link to="/settings" class="menu-item">
                                        <settings-icon class="icon" /> 账户设置
                                    </router-link> -->
                                    <router-link to="#" @click="logout" class="menu-item logout">
                                        <img src="/svg/logouticon.svg" class="icon" /> 退出登录
                                    </router-link>
                                </div>
                            </div>
                        </transition>
                    </div>
                </div>
            </div>

            <!-- 用户控制区 -->

        </div>
    </nav>
</template>
  
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/api/axios'
//   import UserIcon from '../../public/svg/usericon.svg'
//   import SettingsIcon from '@/assets/icons/settings.svg'
//   import LogoutIcon from '../../public/svg/logouticon.svg'
//   import defaultAvatar from '../../public/img/userImage.png'

const router = useRouter()
const isLoggedIn = ref(false)
const showMenu = ref(false)
const defaultAvatar = '/img/userImage.png'

// 用户数据
const user = ref({
    name: '',
    email: '',
    avatar: defaultAvatar
})

// 获取用户信息
const fetchUserInfo = async () => {
    try {
        const res = await axios.get('/api/v1/users/me/')
        console.log('获取用户信息响应:', res)
        
        if (res.data && res.data.code === 0 && res.data.data) {
            user.value = {
                name: res.data.data.username,
                email: res.data.data.email,
                avatar: res.data.data.avatar || defaultAvatar
            }
            isLoggedIn.value = true
            console.log('用户信息获取成功:', user.value)
        } else {
            console.error('获取用户信息响应格式错误:', res.data)
            throw new Error('获取用户信息失败')
        }
    } catch (error) {
        console.error('获取用户信息失败:', error)
        isLoggedIn.value = false
        // 如果获取用户信息失败，清除 token
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
    }
}

// 检查登录状态
const checkLoginStatus = () => {
    const token = localStorage.getItem('token')
    console.log('当前 token:', token)
    
    if (token) {
        isLoggedIn.value = true
        fetchUserInfo()
    } else {
        isLoggedIn.value = false
        user.value = {
            name: '',
            email: '',
            avatar: defaultAvatar
        }
    }
}

onMounted(() => {
    checkLoginStatus()
})

// 头像加载失败处理
const handleAvatarError = (e) => {
    e.target.src = defaultAvatar
}

// 打开登录模态框
const openLogin = () => {
    router.push('/login')
}

// 打开注册页面
const openRegister = () => {
    router.push('/register')
}

// 退出登录
const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    isLoggedIn.value = false
    user.value = {
        name: '',
        email: '',
        avatar: defaultAvatar
    }
    router.push('/login')
}
</script>
  
<style scoped>
.navbar {
    background: #1a1a1a;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    top: 0;
    z-index: 1000;
}

.nav-container {
    max-width: 1440px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 10vh;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    color: white;
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: 600;
    margin-left: 20px;
}

.logo {
    height: 40px;
    width: auto;
}

.nav-menu {
    display: flex;
    gap: 2rem;
    margin-right: 3vw;
}

.nav-item {
    color: #e0e0e0;
    text-decoration: none;
    font-size: 1.1rem;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.nav-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.router-link-active {
    color: #176fd4;
    font-weight: 500;
}

.auth-buttons {
    display: flex;
    gap: 1rem;
}

.auth-btn {
    padding: 0.6rem 1.5rem;
    border-radius: 20px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.login {
    background: #176fd4;
    color: white;
}

.register {
    background: transparent;
    border: 2px solid #176fd4;
    color: #176fd4;
}

.user-menu-wrapper {
    position: relative;
}

.user-avatar {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid #176fd4;
}

.user-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.user-menu {
    position: absolute;
    right: 0;
    top: 55px;
    background: #2b2b2b;
    border-radius: 8px;
    width: 240px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    padding: 1rem;
    z-index: 100;
}

.user-info {
    padding-bottom: 1rem;
    border-bottom: 1px solid #404040;
}

.username {
    color: white;
    font-weight: 600;
    margin-bottom: 0.3rem;
}

.email {
    color: #888;
    font-size: 0.9rem;
}

.menu-items {
    padding-top: 0.8rem;
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.8rem;
    color: #e0e0e0;
    text-decoration: none;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.menu-item:hover {
    background: rgba(255, 255, 255, 0.05);
}

.logout {
    color: #ff5252;
}

.icon {
    width: 18px;
    height: 18px;
    fill: currentColor;
}

/* 过渡动画 */
.slide-fade-enter-active {
    transition: all 0.2s ease-out;
}

.slide-fade-leave-active {
    transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateY(-10px);
    opacity: 0;
}

@media (max-width: 768px) {
    .nav-menu {
        display: none;
    }

    .brand span {
        display: none;
    }
}
</style>
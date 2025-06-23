import axios from 'axios'

// 创建 axios 实例
const instance = axios.create({
    baseURL: 'http://127.0.0.1:8000',  // 后端 API 的基础 URL（已改为服务器地址）
    timeout: 5000,  // 请求超时时间
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
instance.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 响应拦截器
instance.interceptors.response.use(
    response => {
        // 直接返回完整的响应数据
        return response
    },
    error => {
        if (error.response) {
            // 处理 401 未授权错误
            if (error.response.status === 401) {
                localStorage.removeItem('token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default instance 
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1', // 使用相对路径，通过代理访问
  timeout: 30000, // 超时时间30秒
})

// 是否正在刷新token
let isRefreshing = false
// 重试队列
let retryRequests = []

// 刷新token的函数
const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem('refresh_token')
    if (!refresh) {
      throw new Error('No refresh token')
    }
    
    const response = await api.post('/users/token/refresh/', {
      refresh: refresh
    })
    
    const { access } = response.data
    localStorage.setItem('token', access)
    return access
  } catch (error) {
    console.error('刷新token失败:', error)
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
    throw error
  }
}

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 如果是 FormData，删除 Content-Type 让浏览器自动设置
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 直接返回响应数据
    return response.data
  },
  async error => {
    console.error('响应错误:', error)
    // 如果是 500 错误，打印更详细的信息
    if (error.response && error.response.status === 500) {
      console.error('服务器错误详情:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      })
    }
    return Promise.reject(error)
  }
)

// 导出API模块
const apiService = {
  // 认证相关
  auth: {
    // 登录
    login: async (username, password) => {
      try {
        const response = await api.post('/users/login/', { username, password })
        return response
      } catch (error) {
        console.error('登录请求失败:', error)
        throw error
      }
    },
    
    // 注册
    register: async (userData) => {
      try {
        const response = await api.post('/users/register/', userData)
        return response
      } catch (error) {
        console.error('注册请求失败:', error)
        throw error
      }
    },
    
    // 获取当前用户信息
    getCurrentUser: async () => {
      try {
        const response = await api.get('/users/me/')
        return response
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },
    
    // 更新用户信息
    updateUser: async (userData) => {
      try {
        const response = await api.put('/users/me/', userData)
        return response
      } catch (error) {
        console.error('更新用户信息失败:', error)
        throw error
      }
    },
    
    // 刷新token
    refreshToken: async () => {
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) {
          throw new Error('No refresh token')
        }
        
        const response = await api.post('/users/token/refresh/', { refresh })
        return response
      } catch (error) {
        console.error('刷新token失败:', error)
        throw error
      }
    }
  },
  
  // 图片相关
  images: {
    // 获取图片列表
    getList: async (params) => {
      try {
        const response = await api.get('/images/', { params })
        return response
      } catch (error) {
        console.error('获取图片列表失败:', error)
        throw error
      }
    },
    
    // 上传图片
    upload: async (formData) => {
      try {
        const response = await api.post('/images/upload/', formData)
        return response
      } catch (error) {
        console.error('上传图片失败:', error)
        throw error
      }
    },
    
    // 获取图片详情
    getDetail: async (id) => {
      try {
        const response = await api.get(`/images/${id}/`)
        return response
      } catch (error) {
        console.error('获取图片详情失败:', error)
        throw error
      }
    }
  },
  
  // 导出原始api实例
  api
}

export default apiService
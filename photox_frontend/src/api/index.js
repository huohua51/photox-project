import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://8.148.71.20:8000/api/v1', // API的基础URL，已加 /v1
  timeout: 30000, // 超时时间30秒
  headers: {
    'Content-Type': 'application/json'
  }
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
    
    const response = await axios.post('http://8.148.71.20:8000/api/v1/users/token/refresh/', {
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
    // 直接返回原始响应数据
    return response.data
  },
  async error => {
    console.error('响应错误:', error)
    const response = error.response
    
    // 处理特定状态码
    if (response) {
      switch (response.status) {
        case 401:
          // 登录接口遇到401时，不自动跳转，防止页面自动刷新死循环
          if (response.config.url.includes('/users/login/')) {
            localStorage.removeItem('token')
            localStorage.removeItem('refresh_token')
            // 只返回错误，不跳转
            return Promise.reject(error)
          }
          // 如果是刷新token的请求失败，直接跳转登录
          if (response.config.url.includes('/token/refresh/')) {
            localStorage.removeItem('token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
            return Promise.reject(error)
          }
          
          // 如果正在刷新token，将请求加入重试队列
          if (isRefreshing) {
            return new Promise(resolve => {
              retryRequests.push(() => {
                resolve(api(response.config))
              })
            })
          }
          
          isRefreshing = true
          
          try {
            // 尝试刷新token
            const newToken = await refreshToken()
            // 更新请求头中的token
            response.config.headers['Authorization'] = `Bearer ${newToken}`
            // 重试队列中的请求
            retryRequests.forEach(callback => callback())
            retryRequests = []
            // 重试当前请求
            return api(response.config)
          } catch (refreshError) {
            retryRequests = []
            return Promise.reject(refreshError)
          } finally {
            isRefreshing = false
          }
          
        case 403:
          console.error('没有权限访问此资源')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器错误')
          break
        default:
          console.error(`未处理的错误状态码: ${response.status}`)
      }
      
      // 返回服务器返回的错误信息
      if (response.data && response.data.message) {
        return Promise.reject(new Error(response.data.message))
      }
    }
    return Promise.reject(error)
  }
)

/**
 * 登录函数 - 使用原生fetch，避免拦截器干扰
 */
const login = async (username, password) => {
  try {
    console.log('开始登录请求...')
    
    const url = 'http://8.148.71.20:8000/api/v1/users/login/'
    console.log(`发送登录请求到: ${url}`)
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })
    
    console.log(`登录响应状态: ${response.status} ${response.statusText}`)
    
    // 读取文本响应
    const responseText = await response.text()
    console.log(`登录响应内容: ${responseText}`)
    
    if (!response.ok) {
      // 尝试解析错误消息
      try {
        const errorData = JSON.parse(responseText)
        if (errorData.detail) {
          throw new Error(errorData.detail)
        } else if (errorData.message) {
          throw new Error(errorData.message)
        } else if (errorData.error) {
          throw new Error(errorData.error)
        } else if (errorData.non_field_errors) {
          throw new Error(errorData.non_field_errors.join(', '))
        }
      } catch (parseError) {
        // 如果解析失败，使用原始错误
        console.error('无法解析错误响应:', parseError)
      }
      throw new Error(`登录失败: ${response.status} ${responseText || response.statusText}`)
    }
    
    try {
      // 尝试解析JSON
      const data = JSON.parse(responseText)
      console.log('解析后的响应:', data)
      
      // 标准化token格式
      let result = {}
      
      // 情况1: {code: 0, message: "登录成功", data: {access, refresh}}
      if (data.code === 0 && data.data && data.data.access && data.data.refresh) {
        result = {
          code: 0,
          message: data.message || '登录成功',
          data: {
            access: data.data.access,
            refresh: data.data.refresh
          }
        }
      }
      // 情况2: {access, refresh} 直接返回token
      else if (data.access && data.refresh) {
        result = {
          code: 0,
          message: '登录成功',
          data: {
            access: data.access,
            refresh: data.refresh
          }
        }
      }
      // 情况3: 其他非标准格式，尝试提取tokens
      else {
        console.warn('非标准登录响应格式:', data)
        // 递归查找access和refresh token
        const findTokens = (obj) => {
          let tokens = { access: null, refresh: null }
          if (!obj || typeof obj !== 'object') return tokens
          
          if (obj.access) tokens.access = obj.access
          if (obj.refresh) tokens.refresh = obj.refresh
          
          // 遍历所有属性
          for (const key in obj) {
            if (obj[key] && typeof obj[key] === 'object') {
              const found = findTokens(obj[key])
              if (found.access) tokens.access = found.access
              if (found.refresh) tokens.refresh = found.refresh
            }
          }
          
          return tokens
        }
        
        const tokens = findTokens(data)
        if (tokens.access && tokens.refresh) {
          result = {
            code: 0,
            message: '登录成功',
            data: {
              access: tokens.access,
              refresh: tokens.refresh
            }
          }
        } else {
          throw new Error('无法从响应中提取token信息')
        }
      }
      
      return result
    } catch (e) {
      console.error('JSON解析失败:', e)
      throw new Error('无法解析服务器响应: ' + e.message)
    }
  } catch (error) {
    console.error('登录请求失败:', error)
    throw error
  }
}

api.login = login

export default api
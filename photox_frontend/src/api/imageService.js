import api from './index'

/**
 * 图片服务API
 * 提供图片上传、获取、修改和删除功能
 */
const imageService = {
  /**
   * 上传单张图片
   * @param {File} imageFile - 要上传的图片文件
   * @param {Object} options - 上传选项
   * @param {string} options.title - 图片标题（可选）
   * @param {Function} options.onProgress - 上传进度回调（可选）
   * @returns {Promise<Object>} 上传成功的图片信息
   */
  uploadImage: async (imageFile, options = {}) => {
    try {
      console.log('开始上传图片...', imageFile.name, imageFile.size, '字节')
      
      // 验证文件是否为图片
      if (!imageFile.type.startsWith('image/')) {
        throw new Error('仅支持图片文件')
      }
      
      // 创建FormData
      const formData = new FormData()
      formData.append('image', imageFile)
      
      if (options.title) {
        formData.append('title', options.title)
        console.log('添加标题:', options.title)
      }
      if (options.category) {
        formData.append('category', options.category)
        console.log('添加分类:', options.category)
      }
      if (options.is_public !== undefined) {
        formData.append('is_public', options.is_public)
        console.log('添加公开状态:', options.is_public)
      }

      // 使用直接URL而不是api实例，避免拦截器影响
      const url = 'http://8.148.71.20:8000/api/v1/images/upload/'
      console.log('上传到URL:', url)
      
      // 获取token并添加到请求头
      const token = localStorage.getItem('token')
      let headers = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
        console.log('已添加授权头')
      } else {
        console.warn('未找到授权令牌')
      }
      
      // 使用原生fetch以最大兼容性上传文件
      console.log('开始发送fetch请求...')
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: headers,
        credentials: 'same-origin'
      })
      
      console.log('fetch响应状态:', response.status, response.statusText)
      
      // 尝试以文本形式读取响应
      const responseText = await response.text()
      console.log('响应内容:', responseText)
      
      if (!response.ok) {
        // 尝试解析错误响应
        try {
          const errorData = JSON.parse(responseText)
          if (errorData.code === 1 && errorData.message) {
            throw new Error(errorData.message)
          }
          if (errorData.error) {
            throw new Error(errorData.error)
          }
        } catch (parseError) {
          // 解析失败，使用原始错误
          console.error('解析错误失败:', parseError)
        }
        throw new Error(`上传失败: ${response.status} ${responseText || response.statusText}`)
      }
      
      // 尝试解析JSON
      let resultData
      try {
        resultData = JSON.parse(responseText)
        console.log('解析后的JSON响应:', resultData)
      } catch (e) {
        console.error('JSON解析失败:', e)
        throw new Error('无法解析服务器响应为JSON')
      }
      
      // 规范化响应格式
      let standardResponse = {}
      
      // 情况1: {code: 0, message: '成功', data: {...}}
      if (resultData.code === 0 && resultData.data) {
        standardResponse = resultData
      }
      // 情况2: 直接是数据对象 {...}
      else if (resultData.id && resultData.image_url) {
        standardResponse = {
          code: 0,
          message: '上传成功',
          data: resultData
        }
      }
      // 其他未知情况
      else {
        console.warn('未知的响应格式:', resultData)
        throw new Error('服务器返回的响应格式不符合预期')
      }
      
      return standardResponse
    } catch (error) {
      console.error('图片上传服务失败 (imageService.js):', error)
      throw error
    }
  },
  
  /**
   * 获取单张图片详情
   * @param {number|string} imageId - 图片ID
   * @returns {Promise<Object>} 图片详情
   */
  getImageDetails: async (imageId) => {
    try {
      return await api.get(`/images/${imageId}/`)
    } catch (error) {
      console.error(`获取图片 ${imageId} 详情失败`, error)
      throw error
    }
  },
  
  /**
   * 修改图片信息
   * @param {number|string} imageId - 图片ID
   * @param {Object} updateData - 要更新的图片信息
   * @param {string} updateData.title - 图片标题
   * @returns {Promise<Object>} 更新后的图片信息
   */
  updateImage: async (imageId, updateData) => {
    try {
      return await api.put(`/images/${imageId}/`, updateData)
    } catch (error) {
      console.error(`修改图片 ${imageId} 信息失败`, error)
      throw error
    }
  },
  
  /**
   * 删除图片
   * @param {number|string} imageId - 要删除的图片ID
   * @returns {Promise<void>}
   */
  deleteImage: async (imageId) => {
    try {
      return await api.delete(`/images/${imageId}/`)
    } catch (error) {
      console.error(`删除图片 ${imageId} 失败`, error)
      throw error
    }
  },
  
  /**
   * 获取当前用户的图片列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码或下一页的URL
   * @param {number} params.pageSize - 每页数量
   * @param {string} params.ordering - 排序方式，如"-created_at"按创建时间倒序
   * @returns {Promise<Object>} 分页的图片列表
   */
  getUserImages: async (params = {}) => {
    try {
      let url = '/images/'
      let config = {}
      
      // 如果提供了完整的下一页URL，直接使用它
      if (typeof params.page === 'string' && params.page.startsWith('http')) {
        url = params.page
      } else {
        // 否则构建查询参数
        config = { params }
      }
      
      const response = await api.get(url, config)
      console.log('API响应:', response)
      
      // 确保返回正确的数据结构
      if (response && response.data) {
        return response.data
      } else if (response && response.results) {
        return response
      } else {
        throw new Error('无效的响应格式')
      }
    } catch (error) {
      console.error('获取用户图片列表失败', error)
      throw error
    }
  }
}

export default imageService 
import apiService from './index'
const { api, images } = apiService

// 工具函数：格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 工具函数：获取图片尺寸
const getImageDimensions = (file) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve(`${img.width}x${img.height}`)
      URL.revokeObjectURL(img.src)
    }
    img.src = URL.createObjectURL(file)
  })
}

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
      console.log('开始上传图片...', {
        fileName: imageFile.name,
        fileSize: imageFile.size,
        fileType: imageFile.type
      })
      
      // 验证文件是否为图片
      if (!imageFile.type.startsWith('image/')) {
        throw new Error('仅支持图片文件')
      }
      
      // 检查是否有token
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      // 创建FormData
      const formData = new FormData()
      formData.append('image', imageFile)
      
      // 添加标题（可选）
      if (options.title) {
        formData.append('title', options.title)
      }
      
      // 添加公开状态（可选，默认为false）
      if (options.is_public !== undefined) {
        formData.append('is_public', options.is_public)
      }

      // 打印FormData内容
      for (let pair of formData.entries()) {
        console.log('FormData内容:', pair[0], pair[1])
      }

      // 使用 api.post 直接上传
      const response = await api.post('/images/upload/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        // 保持原始 FormData 格式，不进行任何转换
        transformRequest: [(data) => data],
        onUploadProgress: (progressEvent) => {
          if (options.onProgress) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            options.onProgress(percentCompleted)
          }
        }
      })
      
      console.log('上传响应:', response)
      
      // 检查响应格式
      if (!response) {
        throw new Error('无效的响应格式')
      }
      
      // 返回标准化的图片数据
      return {
        id: response.id,
        thumbnail: response.image_url,
        url: response.image_url,
        size: formatFileSize(imageFile.size),
        dimensions: await getImageDimensions(imageFile),
        type: imageFile.type.split('/')[1].toUpperCase(),
        createdAt: new Date().toLocaleString()
      }
    } catch (error) {
      console.error('图片上传服务失败:', error)
      if (error.response) {
        console.error('错误响应:', error.response.data)
        console.error('错误状态:', error.response.status)
        console.error('错误头信息:', error.response.headers)
        console.error('请求头信息:', error.config?.headers)
        
        // 处理特定错误
        if (error.response.status === 401) {
          throw new Error('登录已过期，请重新登录')
        } else if (error.response.status === 413) {
          throw new Error('文件太大，请选择小于5MB的图片')
        } else if (error.response.status === 415) {
          throw new Error('不支持的图片格式')
        } else if (error.response.status === 500) {
          const errorMessage = error.response.data?.message || '服务器错误，请稍后重试'
          throw new Error(errorMessage)
        }
      }
      throw error
    }
  },
  
  /**
   * 获取单张图片详情
   * @param {number|string} imageId - 图片ID
   * @returns {Promise<Object>} 图片详情
   */
  getImageDetail: async (imageId) => {
    try {
      const response = await api.get(`/images/${imageId}/`)
      console.log('获取图片详情响应:', response)
      return response
    } catch (error) {
      console.error('获取图片详情失败', error)
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
      console.log('发送删除请求:', imageId)
      await api.delete(`/images/${imageId}/`)
      // 204 状态码表示删除成功，不需要返回任何数据
      return true
    } catch (error) {
      console.error(`删除图片 ${imageId} 失败:`, error)
      if (error.response) {
        console.error('错误响应:', error.response.data)
        console.error('错误状态:', error.response.status)
      }
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
  },
  
  /**
   * 获取图片分类
   * @returns {Promise<Object>} 图片分类列表
   */
  getImageCategories: async () => {
    try {
      const response = await api.images.getCategories()
      console.log('获取分类响应:', response)
      return response
    } catch (error) {
      console.error('获取图片分类失败', error)
      throw error
    }
  }
}

export default imageService 
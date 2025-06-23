<template>
    <div class="detail-container">
      <!-- 左侧图片区域 -->
      <div class="image-section" :class="{ 'expanded': !showInfo }">
        <DetailViewer
          :currentImage="currentImage"
          @previous="goToPrevious"
          @next="goToNext"
          @back="goBack"
          @download="downloadImage"
          @save="saveToAlbum"
          :showNavigation="!route.query.fromHome"
          :showBackButton="!route.query.fromHome"
        />
      </div>
  
      <!-- 右侧信息区域 -->
      <div class="info-section" :class="{ 'collapsed': !showInfo }">
        <div class="info-toggle" @click="toggleInfo">
          <span class="material-icons">{{ showInfo ? '>' : '>' }}</span>
        </div>
        <div class="info-card" v-show="showInfo">
          <h2>图片基本信息</h2>
          <div class="info-content">
            <div class="info-group">
              <div class="info-item">
                <span class="label">标题</span>
                <span class="value">{{ image?.title || '无标题' }}</span>
              </div>
              <div class="info-item">
                <span class="label">分类</span>
                <span class="value category-tag">{{ image?.category || '未分类' }}</span>
              </div>
            </div>

            <div class="info-group">
              <div class="info-item">
                <span class="label">标签</span>
                <div class="tags-container">
                  <span v-for="(tag, index) in formatTags" :key="index" class="tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>

            <div class="info-group">
              <div class="info-item">
                <span class="label">创建时间</span>
                <span class="value">{{ formatDate }}</span>
              </div>
              <div class="info-item">
                <span class="label">是否公开</span>
                <span class="value" :class="{ 'public': image?.is_public }">
                  {{ image?.is_public ? '是' : '否' }}
                </span>
              </div>
            </div>

            <div class="info-group">
              <div class="info-item">
                <span class="label">尺寸</span>
                <span class="value">{{ imageDimensions.width }} x {{ imageDimensions.height }}</span>
              </div>
              <div class="info-item">
                <span class="label">大小</span>
                <span class="value">{{ imageSizeMB }} MB</span>
              </div>
              <div class="info-item">
                <span class="label">格式</span>
                <span class="value format-tag">{{ imageFormat }}</span>
              </div>
            </div>

            <div class="info-group" v-if="image?.colors?.length">
              <div class="info-item full-width">
                <span class="label">颜色信息</span>
                <div class="colors-container">
                  <div v-for="(color, index) in image.colors" :key="index" 
                       class="color-item" 
                       :style="{ backgroundColor: formatColor(color) }"
                       :title="formatColorDisplay(color)">
                    <span class="color-value">{{ formatColorDisplay(color) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>
  
<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '@/api'
import DetailViewer from '@/components/DetailViewer.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const image = ref(null)
const loading = ref(true)
const error = ref(null)

// 当前图片信息
const currentImage = computed(() => {
  if (!image.value) return ''
  return image.value.image_url || ''
})

// 标签值映射
const tagMap = {
  '968': 'cup',
  '549': 'envelope',
  '446': 'binder, ring-binder',
  '794': 'shower curtain',
  '844': 'switch, electric switch, electrical switch'
}

// 格式化标签显示
const formatTags = computed(() => {
  if (!image.value?.tags) return []
  let tags = []
  
  try {
    // 尝试解析标签
    if (typeof image.value.tags === 'string') {
      try {
        // 首先尝试解析JSON
        const parsedTags = JSON.parse(image.value.tags)
        // 处理标签格式
        if (Array.isArray(parsedTags)) {
          tags = parsedTags.flatMap(tag => {
            // 如果标签是字符串且包含冒号，提取冒号后的值
            if (typeof tag === 'string' && tag.includes(':')) {
              const value = tag.split(':')[1].trim()
              // 移除引号，并按逗号分割成多个标签
              return value.replace(/['"]/g, '')
                .split(',')
                .map(t => t.trim())
                .filter(t => t) // 过滤掉空值
            }
            return [tag]
          })
        } else {
          tags = [parsedTags]
        }
      } catch {
        // 如果JSON解析失败，尝试按逗号分隔
        tags = image.value.tags.split(',').map(tag => tag.trim())
      }
    } else if (Array.isArray(image.value.tags)) {
      tags = image.value.tags.flatMap(tag => {
        if (typeof tag === 'string' && tag.includes(':')) {
          const value = tag.split(':')[1].trim()
          return value.replace(/['"]/g, '')
            .split(',')
            .map(t => t.trim())
            .filter(t => t) // 过滤掉空值
        }
        return [tag]
      })
    } else {
      return []
    }
    
    // 过滤掉空值并确保所有标签都是字符串
    return tags.map(tag => String(tag)).filter(tag => tag)
  } catch (error) {
    console.error('标签解析错误:', error)
    return []
  }
})

// 格式化日期显示
const formatDate = computed(() => {
  if (!image.value?.created_at) return '未知'
  return new Date(image.value.created_at).toLocaleString()
})

// 响应式图片信息
const imageDimensions = ref({ width: 0, height: 0 })
const imageSizeMB = ref('未知')
const imageFormat = ref('未知')

// 获取图片详情
const fetchImageDetail = async () => {
  try {
    console.log('开始获取图片详情')
    loading.value = true
    const id = Number(route.params.id)
    console.log('获取图片详情ID:', id)
    
    const response = await apiService.images.getDetail(id)
    console.log('获取图片详情响应:', response)
    console.log('响应数据类型:', typeof response)
    console.log('响应数据结构:', JSON.stringify(response, null, 2))
    
    // 检查响应格式
    if (!response) {
      throw new Error('获取图片信息失败：响应为空')
    }

    // 获取图片详情数据
    const imageData = response.data || response
    console.log('处理后的图片数据:', imageData)
    console.log('图片数据类型:', typeof imageData)
    console.log('图片数据结构:', JSON.stringify(imageData, null, 2))
    
    if (!imageData) {
      throw new Error('获取图片信息失败：数据为空')
    }

    image.value = imageData
    console.log('图片详情更新成功:', image.value)
    console.log('颜色数据:', image.value?.colors)
    console.log('颜色数据类型:', typeof image.value?.colors)
    console.log('颜色数据结构:', JSON.stringify(image.value?.colors, null, 2))
  } catch (err) {
    console.error('获取图片详情失败:', err)
    error.value = err.message || '获取图片信息失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 读取图片尺寸
const loadImageDimensions = (imgSrc) =>
  new Promise((resolve) => {
    const tempImg = new Image()
    tempImg.src = imgSrc
    tempImg.onload = () => {
      resolve({ width: tempImg.naturalWidth, height: tempImg.naturalHeight })
    }
    tempImg.onerror = () => {
      resolve({ width: 0, height: 0 })
    }
  })

// 读取图片大小
async function loadImageSize(imgSrc) {
  try {
    const response = await fetch(imgSrc)
    if (response.ok) {
      const blob = await response.blob()
      const sizeInMB = (blob.size / (1024 * 1024)).toFixed(2)
      return sizeInMB
    }
  } catch (e) {
    console.warn('获取图片大小失败:', e)
  }
  return '未知'
}

// 检测图片格式
function detectImageFormat(imgSrc) {
  const ext = imgSrc.split('.').pop().toUpperCase()
  const commonFormats = ['JPG', 'JPEG', 'PNG', 'GIF', 'WEBP', 'BMP', 'SVG']
  if (commonFormats.includes(ext)) return ext
  return '未知'
}

// 下载图片
const downloadImage = () => {
  if (!currentImage.value) return

  const link = document.createElement('a')
  link.href = currentImage.value

  // 创建有意义的文件名：分类名_标题.jpg
  const fileName = `${image.value?.category || 'untitled'}_${image.value?.title || 'untitled'}.jpg`

  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 转存图片
const saveToAlbum = async () => {
  try {
    if (!image.value?.image_url) {
      alert('图片数据不完整，无法保存');
      return;
    }

    // 检查个人仓库中是否已有此图片
    const myImages = await apiService.images.getList();
    
    // 获取当前图片的原始URL（去除查询参数）
    const currentImageUrl = new URL(image.value.image_url);
    const currentImagePath = currentImageUrl.pathname;
    
    // 检查是否存在相同路径的图片
    const existingImage = myImages.results.find(img => {
      if (!img.image_url) return false;
      try {
        const imgUrl = new URL(img.image_url);
        return imgUrl.pathname === currentImagePath;
      } catch {
        return false;
      }
    });
    
    if (existingImage) {
      alert('该图片已存在于您的个人仓库中');
      return;
    }

    // 1. 下载图片为 blob
    const response = await fetch(image.value.image_url);
    if (!response.ok) {
      throw new Error('下载图片失败');
    }
    const blob = await response.blob();

    // 2. 构造 File 对象
    const fileName = `${image.value?.category || 'untitled'}_${image.value?.title || 'untitled'}.jpg`;
    const file = new File([blob], fileName, { type: blob.type });

    // 3. 构造 FormData
    const formData = new FormData();
    formData.append('image', file);
    formData.append('title', image.value.title || '');
    if (image.value.category) formData.append('category', image.value.category);
    formData.append('is_public', false); // 默认设置为私有

    // 4. 上传到后端
    const uploadResp = await apiService.images.upload(formData);

    if (uploadResp?.data?.id || uploadResp?.data?.data?.id) {
      alert('图片已成功保存到个人仓库！');
    } else {
      throw new Error('上传失败');
    }
  } catch (err) {
    console.error('保存到个人仓库失败:', err);
    if (err.message === '下载图片失败') {
      alert('下载图片失败，请检查网络连接');
    } else if (err.message === '上传失败') {
      alert('上传失败，请稍后重试');
    } else {
      alert('保存失败，请检查网络或登录状态');
    }
  }
};

// 格式化颜色值
const formatColor = (color) => {
  // 如果已经是有效的颜色值，直接返回
  if (/^#([0-9A-F]{3}){1,2}$/i.test(color) || 
      /^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$/i.test(color) ||
      /^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$/i.test(color)) {
    return color
  }
  
  // 如果是数字数组格式 [r, g, b]
  if (Array.isArray(color) && color.length >= 3) {
    return `rgb(${color[0]}, ${color[1]}, ${color[2]})`
  }
  
  // 如果是对象格式 {r: 255, g: 255, b: 255}
  if (typeof color === 'object' && color !== null) {
    if ('r' in color && 'g' in color && 'b' in color) {
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    }
  }
  
  // 默认返回黑色
  return '#000000'
}

// 格式化颜色显示值
const formatColorDisplay = (color) => {
  const formattedColor = formatColor(color)
  if (formattedColor.startsWith('rgb')) {
    // 将 rgb 转换为 hex
    const rgb = formattedColor.match(/\d+/g)
    if (rgb && rgb.length >= 3) {
      const hex = '#' + rgb.map(x => {
        const hex = parseInt(x).toString(16)
        return hex.length === 1 ? '0' + hex : hex
      }).join('')
      return hex.toUpperCase()
    }
  }
  return formattedColor.toUpperCase()
}

// 监听图片变化
watch(
  currentImage,
  async (newSrc) => {
    if (!newSrc) return
    imageDimensions.value = await loadImageDimensions(newSrc)
    // 使用后端返回的图片大小数据
    if (image.value?.size) {
      imageSizeMB.value = (image.value.size / (1024 * 1024)).toFixed(2)
    } else {
      imageSizeMB.value = await loadImageSize(newSrc)
    }
    imageFormat.value = detectImageFormat(newSrc)
  },
  { immediate: true }
)

// 导航功能
const goBack = () => {
  if (route.query.fromHome) {
    window.close();
  } else if (route.query.fromGallery) {
    router.push('/gallery');
  } else {
    router.back();
  }
};

// 切换到上一张图片
const goToPrevious = async () => {
  try {
    console.log('开始获取上一张图片')
    const id = Number(route.params.id)
    console.log('当前图片ID:', id)
    
    // 获取图片列表，按创建时间倒序排列
    const response = await apiService.images.getList({
      ordering: '-created_at'
    })
    console.log('获取图片列表响应:', response)
    
    // 检查响应格式
    if (!response) {
      console.error('获取图片列表失败：响应为空')
      return
    }

    // 获取图片列表数据
    const images = response.results || response
    console.log('图片列表:', images)
    
    if (!Array.isArray(images)) {
      console.error('获取图片列表失败：数据格式错误')
      return
    }

    const currentIndex = images.findIndex(img => img.id === id)
    console.log('当前图片索引:', currentIndex)
    
    if (currentIndex === -1) {
      console.error('未找到当前图片')
      return
    }
    
    if (currentIndex > 0) {
      const previousImage = images[currentIndex - 1]
      console.log('上一张图片:', previousImage)
      
      try {
        // 更新路由参数
        await router.replace({ 
          path: `/photodetail/${previousImage.id}`,
          query: route.query
        })
        console.log('路由更新成功')
        
        // 重新获取图片详情
        await fetchImageDetail()
        console.log('图片详情更新完成')
      } catch (error) {
        console.error('更新图片失败:', error)
      }
    } else {
      console.log('已经是第一张图片')
    }
  } catch (error) {
    console.error('获取上一张图片失败:', error)
  }
}

// 切换到下一张图片
const goToNext = async () => {
  try {
    console.log('开始获取下一张图片')
    const id = Number(route.params.id)
    console.log('当前图片ID:', id)
    
    // 获取图片列表，按创建时间倒序排列
    const response = await apiService.images.getList({
      ordering: '-created_at'
    })
    console.log('获取图片列表响应:', response)
    
    // 检查响应格式
    if (!response) {
      console.error('获取图片列表失败：响应为空')
      return
    }

    // 获取图片列表数据
    const images = response.results || response
    console.log('图片列表:', images)
    
    if (!Array.isArray(images)) {
      console.error('获取图片列表失败：数据格式错误')
      return
    }

    const currentIndex = images.findIndex(img => img.id === id)
    console.log('当前图片索引:', currentIndex)
    
    if (currentIndex === -1) {
      console.error('未找到当前图片')
      return
    }
    
    if (currentIndex < images.length - 1) {
      const nextImage = images[currentIndex + 1]
      console.log('下一张图片:', nextImage)
      
      try {
        // 更新路由参数
        await router.replace({ 
          path: `/photodetail/${nextImage.id}`,
          query: route.query
        })
        console.log('路由更新成功')
        
        // 重新获取图片详情
        await fetchImageDetail()
        console.log('图片详情更新完成')
      } catch (error) {
        console.error('更新图片失败:', error)
      }
    } else {
      console.log('已经是最后一张图片')
    }
  } catch (error) {
    console.error('获取下一张图片失败:', error)
  }
}

// 键盘导航支持
const handleKeyDown = (e) => {
  if (e.key === 'Escape') goBack()
  if (e.key === 'ArrowLeft') goToPrevious()
  if (e.key === 'ArrowRight') goToNext()
}

// 添加信息面板状态控制
const showInfo = ref(true)

const toggleInfo = () => {
  showInfo.value = !showInfo.value
}

onMounted(() => {
  fetchImageDetail()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>
  
<style scoped>
.photo-detail {
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}

.detail-header {
  background-color: var(--secondary-color);
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.photo-title {
  color: var(--text-color);
}

.photo-description {
  color: var(--text-color);
  opacity: 0.8;
}

.photo-meta {
  color: var(--text-color);
  opacity: 0.7;
}

.photo-actions button {
  color: var(--text-color);
  background: none;
  border: none;
  transition: color 0.3s;
}

.photo-actions button:hover {
  color: var(--primary-color);
}

.comment-section {
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.comment-input {
  background-color: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}

.comment-input:focus {
  border-color: var(--primary-color);
  outline: none;
}

.comment-list {
  color: var(--text-color);
}

.comment-item {
  border-bottom: 1px solid var(--border-color);
  transition: border-color 0.3s;
}

.comment-author {
  color: var(--text-color);
  font-weight: 500;
}

.comment-content {
  color: var(--text-color);
  opacity: 0.9;
}

.comment-time {
  color: var(--text-color);
  opacity: 0.7;
}

.detail-container {
    display: flex;
    min-height: 100vh;
    padding: 20px;
    background-color: var(--bg-color);
    color: var(--text-color);
    gap: 20px;
    transition: background-color 0.3s, color 0.3s;
}

.image-section {
  flex: 1;
  transition: all 0.3s ease;
  position: relative;
}

.image-section.expanded {
  flex: 1.2;
}

.info-section {
  width: 30vw;
  background-color: var(--secondary-color);
  border-left: 1px solid var(--border-color);
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
  border-top-left-radius: 20px;
  border-bottom-left-radius: 20px;
  color: var(--text-color);
}

.info-section.collapsed {
  width: 40px;
}

.info-section.collapsed::before {
  content: '图片基本信息';
  position: absolute;
  left: 0;
  top: 30px;
  width: 40px;
  writing-mode: vertical-lr;
  text-orientation: upright;
  color: #1e90ff;
  font-size: 1.4em;
  font-weight: bold;
  letter-spacing: 2px;
  padding: 10px 0;
  white-space: nowrap;
  text-align: center;
  z-index: 1;
}

.info-toggle {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 60px;
  background-color: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 0 4px 4px 0;
  z-index: 2;
  transition: all 0.3s ease;
  color: var(--text-color);
}

.info-toggle:hover {
  background-color: var(--primary-color);
}

.info-toggle .material-icons {
  color: var(--text-color);
  font-size: 20px;
  transition: transform 0.3s ease;
}

.info-section.collapsed .info-toggle .material-icons {
  transform: rotate(180deg);
}

.info-card {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  margin-left: 20px;
  width: calc(100% - 40px);
  color: var(--text-color);
}

.info-card h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: var(--primary-color);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 12px;
  transition: color 0.3s, border-color 0.3s;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  background-color: var(--bg-color);
  border-radius: 8px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.info-item.full-width {
  width: 100%;
}

.label {
  color: var(--text-color);
  opacity: 0.7;
  width: 80px;
  flex-shrink: 0;
  font-size: 14px;
  transition: color 0.3s;
}

.value {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.5;
  transition: color 0.3s;
}

.category-tag {
  background-color: rgba(23, 111, 212, 0.08);
  color: var(--text-color);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.3s ease;
  border: 1px solid rgba(23, 111, 212, 0.2);
}

.format-tag {
  background-color: rgba(82, 196, 26, 0.08);
  color: var(--text-color);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.3s ease;
  border: 1px solid rgba(82, 196, 26, 0.2);
}

.public {
  color: var(--success-color);
  transition: color 0.3s;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background-color: rgba(23, 111, 212, 0.08);
  color: var(--text-color);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid rgba(23, 111, 212, 0.2);
}

.tag:hover {
  background-color: rgba(23, 111, 212, 0.12);
  transform: translateY(-1px);
  color: var(--text-color);
  border-color: rgba(23, 111, 212, 0.3);
}

.colors-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.color-item {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  cursor: pointer;
}

.color-item:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.color-value {
  background-color: var(--bg-color);
  opacity: 0.8;
  color: var(--text-color);
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 10px;
  opacity: 0;
  transition: opacity 0.2s, color 0.3s;
}

.color-item:hover .color-value {
  opacity: 1;
}

@media (max-width: 768px) {
  .detail-container {
    flex-direction: column;
  }

  .image-section {
    padding-right: 0;
    margin-bottom: 20px;
  }

  .info-section {
    width: 100%;
  }
}
</style>
<template>
  <div class="uploader">
    <!-- 上传触发区域 -->
    <div class="upload-trigger" @click="triggerFileInput" @dragover.prevent="onDragOver" @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop" :class="{ 'drag-hover': isDragHovering }">
      <slot name="trigger">
        <div class="default-trigger">
          <UploadIcon />
        </div>
      </slot>
    </div>

    <!-- 隐藏的input -->
    <input ref="fileInput" type="file" multiple accept="image/*" @change="handleFileInput" style="display: none">

    <!-- 上传对话框 -->
    <transition name="fade">
      <div v-if="showDialog" class="upload-dialog">
        <div class="dialog-content">
          <h3>上传设置 ({{ files.length }}个文件)</h3>

          <div class="category-section">
            <select v-model="selectedCategory" @change="handleCategorySelect">
              <option value="">选择现有分类</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
            <div class="or-divider">或</div>
            <input v-model="newCategory" placeholder="输入新分类" @input="handleNewCategoryInput">
          </div>

          <!-- <div class="progress-section">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
              <span class="progress-text">{{ Math.round(progress) }}%</span>
            </div>
          </div> -->

          <div class="dialog-actions">
            <button @click="cancelUpload">取消</button>
            <button @click="startUpload" :disabled="isUploading || (!selectedCategory && !newCategory)">
              {{ isUploading ? '上传中...' : '开始上传' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>
  
<script setup>
import { ref, computed } from 'vue'
import UploadIcon from './UploadIcon.vue'
import axios from 'axios'
import imageService from '../api/imageService'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  maxSize: {
    type: Number,
    default: 5 // 单位MB
  },
  token: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'upload-start',
  'upload-progress',
  'upload-success',
  'upload-error',
  'category-created'
])

const fileInput = ref(null)
const showDialog = ref(false)
const files = ref([])
const selectedCategory = ref('')
const newCategory = ref('')
const progress = ref(0)
const isUploading = ref(false)
const isDragHovering = ref(false)

// 拖入时高亮提示
const onDragOver = () => {
  isDragHovering.value = true
}

// 拖离时移除高亮
const onDragLeave = () => {
  isDragHovering.value = false
}

// 拖拽释放时处理文件
const onDrop = async (e) => {
  isDragHovering.value = false
  const droppedFiles = Array.from(e.dataTransfer.files)
  handleFiles(droppedFiles)
}
// 计算最终分类
const finalCategory = computed(() => {
  return newCategory.value || selectedCategory.value
})

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}

// 处理文件选择
const handleFileInput = (e) => {
  const inputFiles = Array.from(e.target.files)
  handleFiles(inputFiles)
}
// 抽离为通用文件处理方法
const handleFiles = async (rawFiles) => {
  if (!rawFiles.length) return

  const validFiles = []
  for (const file of rawFiles) {
    if (file.size > props.maxSize * 1024 * 1024) {
      emit('upload-error', {
        file,
        error: `文件大小超过${props.maxSize}MB限制`
      })
      continue
    }
    if (!file.type.startsWith('image/')) {
      emit('upload-error', {
        file,
        error: '仅支持图片文件'
      })
      continue
    }
    validFiles.push(file)
  }

  if (validFiles.length) {
    files.value = validFiles
    showDialog.value = true
  }
}

// 开始上传
const startUpload = async () => {
  if (!finalCategory.value) return

  isUploading.value = true
  progress.value = 0
  emit('upload-start', {
    category: finalCategory.value,
    files: files.value
  })

  try {
    const step = 100 / files.value.length
    const results = []

    // 处理新分类
    if (newCategory.value && !props.categories.includes(newCategory.value)) {
      console.log('创建新分类:', newCategory.value)
      emit('category-created', newCategory.value)
    }

    for (const file of files.value) {
      // 使用imageService上传图片
      const result = await uploadImageToServer(file)
      results.push(result)
      progress.value += step
      emit('upload-progress', {
        file,
        progress: progress.value,
        result
      })
    }

    emit('upload-success', results)
  } catch (error) {
    emit('upload-error', error)
  } finally {
    resetState()
  }
}

// 上传图片到服务器API
const uploadImageToServer = async (file) => {
    try {
        console.log('开始上传到服务器...', file.name)
        
        // 使用imageService上传图片，并监控上传进度
        const response = await imageService.uploadImage(file, {
            title: file.name || `Image_${Date.now()}`,
            category: finalCategory.value,
            onProgress: (percent) => {
                console.log(`文件 ${file.name} 上传进度: ${percent}%`)
            }
        })
        
        console.log('上传响应:', response)
        
        // 从响应中提取数据
        let imageData = null
        
        // 处理不同格式的响应
        if (response && response.code === 0 && response.data) {
            // 标准格式: {code:0, message:"success", data:{...}}
            imageData = response.data
        } else if (response && response.data && response.data.id) {
            // 直接返回数据对象: {data:{...}}
            imageData = response.data
        } else if (response && response.id) {
            // 直接返回数据: {...}
            imageData = response
        } else {
            console.error('无法识别的响应格式:', response)
            throw new Error('上传响应格式错误')
        }
        
        // 至少应该有id和image_url
        if (!imageData || !imageData.id || !imageData.image_url) {
            console.error('上传响应缺少必要字段:', imageData)
            throw new Error('上传响应缺少必要字段')
        }
        
        console.log('处理后的图片数据:', imageData)
        
        // 返回标准化的图片数据
        return {
            id: imageData.id,
            thumbnail: imageData.image_url,
            url: imageData.image_url,
            tags: typeof imageData.tags === 'string' ? JSON.parse(imageData.tags) : (imageData.tags || []),
            category: imageData.category || finalCategory.value,
            size: formatFileSize(file.size),
            dimensions: await getImageDimensions(file),
            type: file.type.split('/')[1].toUpperCase(),
            createdAt: new Date().toLocaleString()
        }
    } catch (error) {
        console.error('上传出错:', error)
        throw error
    }
}

// 处理单个文件 (作为备用方法，当API不可用时使用)
const processFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const dimensions = await getImageDimensions(file)
        resolve({
          id: Date.now(),
          thumbnail: e.target.result,
          url: e.target.result,
          tags: [],
          category: finalCategory.value,
          size: formatFileSize(file.size),
          dimensions,
          type: file.type.split('/')[1].toUpperCase(),
          createdAt: new Date().toLocaleString()
        })
      } catch (error) {
        reject(error)
      }
    }
    reader.readAsDataURL(file)
  })
}

// 获取图片尺寸
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

// 重置状态
const resetState = () => {
  isUploading.value = false
  showDialog.value = false
  files.value = []
  selectedCategory.value = ''
  newCategory.value = ''
  progress.value = 0
  fileInput.value.value = ''
}

// 取消上传
const cancelUpload = () => {
  resetState()
  emit('upload-error', '用户取消上传')
}

// 文件大小格式化
const formatFileSize = (bytes) => {
  const units = ['B', 'KB', 'MB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 监听新分类输入
const handleNewCategoryInput = (event) => {
  newCategory.value = event.target.value
  selectedCategory.value = '' // 清空已选分类
  console.log('新分类输入:', newCategory.value)
}

// 监听分类选择
const handleCategorySelect = (event) => {
  selectedCategory.value = event.target.value
  newCategory.value = '' // 清空新分类输入
  console.log('选择分类:', selectedCategory.value)
}
</script>
  
<style scoped>
/* 上传对话框样式 */
.upload-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: #2b2b2b;
  padding: 2rem;
  border-radius: 12px;
  width: 400px;
  color: white;
}

.category-select {
  display: flex;
  gap: 10px;
  align-items: center;
  margin: 1rem 0;

  select,
  input {
    flex: 1;
    padding: 8px;
    background: #404040;
    border: 1px solid #555;
    color: white;
    border-radius: 4px;
  }
}

.progress-bar {
  height: 20px;
  background: #333;
  border-radius: 10px;
  margin: 1rem 0;
  position: relative;
  overflow: hidden;

  .progress {
    height: 100%;
    background: #4CAF50;
    transition: width 0.3s ease;
  }

  span {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 0.8em;
  }
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;

  button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.3s;

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    &:last-child {
      background: #4CAF50;
      color: white;
    }
  }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>
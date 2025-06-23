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

          <div class="upload-options">
            <!-- 图片名称输入 -->
            <div class="option-group">
              <label>图片名称</label>
              <input v-model="imageTitle" placeholder="输入图片名称" class="input-field">
            </div>

            <!-- 是否公开选项 -->
            <div class="option-group">
              <label>是否公开</label>
              <div class="toggle-switch">
                <input type="checkbox" v-model="isPublic" id="public-toggle">
                <label for="public-toggle" class="toggle-label"></label>
                <span class="toggle-text">{{ isPublic ? '公开' : '私有' }}</span>
              </div>
            </div>
          </div>

          <!-- <div class="progress-section">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
              <span class="progress-text">{{ Math.round(progress) }}%</span>
            </div>
          </div> -->

          <div class="dialog-actions">
            <button @click="cancelUpload" class="cancel-btn">取消</button>
            <button @click="startUpload" :disabled="isUploading" class="upload-btn">
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
const imageTitle = ref('')
const isPublic = ref(false)
const isUploading = ref(false)
const isDragHovering = ref(false)
const progress = ref(0)

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
    // 设置默认图片名称为第一个文件的名称
    imageTitle.value = validFiles[0].name
    showDialog.value = true
  }
}

// 开始上传
const startUpload = async () => {
  isUploading.value = true
  progress.value = 0
  emit('upload-start', {
    files: files.value
  })

  try {
    const step = 100 / files.value.length
    const results = []

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
        console.log('开始上传到服务器...', {
            fileName: file.name,
            fileSize: file.size,
            fileType: file.type
        })
        
        // 使用 imageService 上传图片
        const response = await imageService.uploadImage(file, {
            title: imageTitle.value || file.name,
            is_public: isPublic.value,
            onProgress: (percent) => {
                console.log(`上传进度: ${percent}%`)
            }
        })
        
        console.log('上传成功:', response)
        return response
    } catch (error) {
        console.error('上传失败:', {
            error: error,
            response: error.response,
            status: error.response?.status,
            data: error.response?.data
        })
        
        // 如果是网络错误或服务器错误，尝试重试
        if (error.response && (error.response.status === 500 || error.response.status === 502)) {
            console.log('服务器错误，尝试重试...')
            // 等待1秒后重试
            await new Promise(resolve => setTimeout(resolve, 1000))
            return uploadImageToServer(file)
        }
        throw error
    }
}

// 重置状态
const resetState = () => {
    isUploading.value = false
    progress.value = 0
    files.value = []
    showDialog.value = false
    imageTitle.value = ''
    isPublic.value = false
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
.uploader {
  width: 100%;
  height: 200px;
  position: relative;
  transition: all 0.3s ease;
}

.upload-trigger {
  width: 100%;
  height: 100%;
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: var(--secondary-color);
}

.upload-trigger:hover {
  border-color: var(--primary-color);
  background-color: var(--bg-color);
}

.upload-trigger.drag-hover {
  border-color: var(--primary-color);
  background-color: var(--bg-color);
  transform: scale(0.98);
}

.default-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
  color: var(--text-color);
  transition: color 0.3s;
}

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
  backdrop-filter: blur(4px);
}

.dialog-content {
  background: var(--secondary-color);
  padding: 2rem;
  border-radius: 12px;
  width: 400px;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.dialog-content h3 {
  margin: 0 0 1.5rem;
  color: var(--text-color);
  transition: color 0.3s;
}

.upload-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option-group label {
  color: var(--text-color);
  font-size: 0.9em;
  transition: color 0.3s;
}

.input-field {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary-color);
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-label {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  background-color: var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-label:after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: white;
  top: 2px;
  left: 2px;
  transition: all 0.3s ease;
}

input[type="checkbox"] {
  display: none;
}

input[type="checkbox"]:checked + .toggle-label {
  background-color: var(--primary-color);
}

input[type="checkbox"]:checked + .toggle-label:after {
  transform: translateX(20px);
}

.toggle-text {
  color: var(--text-color);
  font-size: 0.9em;
  transition: color 0.3s;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.cancel-btn, .upload-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.cancel-btn:hover {
  background-color: var(--bg-color);
}

.upload-btn {
  background-color: var(--primary-color);
  color: white;
}

.upload-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
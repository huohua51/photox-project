<template>
  <div class="detail-viewer">
    <!-- 返回按钮 -->
    <button v-if="showBackButton" class="back-button" @click="$emit('back')">
      <img src="/svg/return.svg" alt="" style="height: 5vh;">
    </button>

    <!-- 顶部控制栏 -->
    <div class="top-controls">
      <!-- 缩放控制 -->
      <div class="zoom-controls">
        <button class="zoom-button" @click="zoomOut">
          <span class="material-icons">-</span>
        </button>
        <input 
          type="range" 
          v-model="zoomLevel" 
          min="50" 
          max="300" 
          step="10"
          class="zoom-slider"
          @input="handleZoom"
        />
        <span class="zoom-percentage">{{ zoomLevel }}%</span>
        <button class="zoom-button" @click="zoomIn">
          <span class="material-icons">+</span>
        </button>
        <button class="zoom-button reset" @click="resetZoom" title="重置缩放">
          <span class="material-icons"><img src="/svg/restart.svg" alt="" style="height: 1rem;"></span>
        </button>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button class="action-button" @click="onDownload">
          <span class="material-icons">下载</span>
          <img src="/svg/download.svg" alt="" style="height: 1rem;">
        </button>
        <button class="action-button" @click="onSave">
          <span class="material-icons">保存</span>
          <img src="/svg/save.svg" alt="" style="height: 1rem;">

        </button>
      </div>
    </div>

    <!-- 图片容器 -->
    <div class="image-container">
      <div class="image-wrapper" 
           :style="{ transform: `scale(${zoomLevel / 100}) translate(${translateX}px, ${translateY}px)` }"
           @mousedown="startDrag"
           @mousemove="onDrag"
           @mouseup="stopDrag"
           @mouseleave="stopDrag"
           @wheel.prevent="handleWheel">
        <img
          v-if="currentImage"
          :src="currentImage"
          :alt="'图片详情'"
          class="detail-image"
        />
        <div v-else class="no-image">
          <span class="material-icons">image_not_supported</span>
          <p>图片加载失败</p>
        </div>
      </div>
    </div>

    <!-- 导航按钮 -->
    <div v-if="showNavigation" class="navigation-buttons">
      <button class="nav-button prev" @click="onPrevious">
        <img src="/svg/left.svg" alt="" style="height: 6vh;">
      </button>
      <button class="nav-button next" @click="onNext">
        <img src="/svg/right.svg" alt="" style="height: 6vh;">
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  currentImage: {
    type: String,
    required: true
  },
  showNavigation: {
    type: Boolean,
    default: true
  },
  showBackButton: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['previous', 'next', 'back', 'download', 'save'])

// 缩放相关
const zoomLevel = ref(100)
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)
const translateX = ref(0)
const translateY = ref(0)

const zoomIn = () => {
  if (zoomLevel.value < 300) {
    zoomLevel.value = Math.min(300, zoomLevel.value + 10)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 50) {
    zoomLevel.value = Math.max(50, zoomLevel.value - 10)
  }
}

const handleZoom = (event) => {
  // 确保值在有效范围内
  const value = parseInt(event.target.value)
  zoomLevel.value = Math.min(300, Math.max(50, value))
  // 重置拖动位置
  translateX.value = 0
  translateY.value = 0
}

// 拖动相关
const startDrag = (e) => {
  if (zoomLevel.value <= 100) return
  if (e.button !== 0) return // 只响应鼠标左键
  
  isDragging.value = true
  startX.value = e.clientX
  startY.value = e.clientY
}

const onDrag = (e) => {
  if (!isDragging.value || zoomLevel.value <= 100) return

  // 计算鼠标移动的距离
  const deltaX = e.clientX - startX.value
  const deltaY = e.clientY - startY.value

  // 获取图片容器的尺寸
  const container = e.currentTarget.parentElement
  const containerRect = container.getBoundingClientRect()
  const imageRect = e.currentTarget.getBoundingClientRect()

  // 计算缩放后的图片尺寸
  const scaledWidth = imageRect.width
  const scaledHeight = imageRect.height

  // 计算可移动的范围
  const maxX = Math.max(0, (scaledWidth - containerRect.width) / 2)
  const maxY = Math.max(0, (scaledHeight - containerRect.height) / 2)

  // 更新位置
  translateX.value = Math.max(-maxX, Math.min(maxX, translateX.value + deltaX))
  translateY.value = Math.max(-maxY, Math.min(maxY, translateY.value + deltaY))

  // 更新起始点
  startX.value = e.clientX
  startY.value = e.clientY
}

const stopDrag = () => {
  isDragging.value = false
}

const onPrevious = () => {
  console.log('Previous button clicked')
  resetImageState()
  emit('previous')
}

const onNext = () => {
  console.log('Next button clicked')
  resetImageState()
  emit('next')
}

const onBack = () => emit('back')
const onDownload = () => emit('download')
const onSave = () => emit('save')

// 滚轮缩放处理
const handleWheel = (e) => {
  // 获取鼠标在图片上的位置
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // 根据滚轮方向调整缩放级别
  if (e.deltaY < 0) {
    // 向上滚动，放大
    if (zoomLevel.value < 300) {
      zoomLevel.value = Math.min(300, zoomLevel.value + 10)
    }
  } else {
    // 向下滚动，缩小
    if (zoomLevel.value > 50) {
      zoomLevel.value = Math.max(50, zoomLevel.value - 10)
    }
  }
}

// 重置缩放
const resetZoom = () => {
  zoomLevel.value = 100
  translateX.value = 0
  translateY.value = 0
}

// 重置图片状态
const resetImageState = () => {
  zoomLevel.value = 100
  translateX.value = 0
  translateY.value = 0
  isDragging.value = false
}
</script>

<style scoped>
.detail-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.back-button {
  position: absolute;
  top: 0;
  left: 0;
  background: rgba(0, 0, 0, 0);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: background-color 0.3s;
  z-index: 10;
  img{
    transition: 0.2s;
  }
}

.back-button:hover img{
  scale: 1.2;
}

.top-controls {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 20px;
  z-index: 10;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.5);
  padding: 8px 16px;
  border-radius: 20px;
}

.zoom-button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  .material-icons{
    font-size: 1.4rem;
  }
}

.zoom-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.zoom-slider {
  width: 150px;
  height: 4px;
  -webkit-appearance: none;
  background: #666;
  border-radius: 2px;
  outline: none;
}

.zoom-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
}

.zoom-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.zoom-percentage {
  color: white;
  font-size: 0.9rem;
  min-width: 45px;
  text-align: center;
}

.image-container {
  width: 70%;
  height: 70vh;
  margin: 0 auto;
  position: relative;
  background: linear-gradient(45deg, #2a2a2a, #3a3a3a);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.image-section.expanded .image-container {
  width: 85%;
  height: 80vh;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
  transform-origin: center center;
  position: relative;
  cursor: move;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
  user-select: none;
  cursor: move;
}

.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 1.2em;
}

.no-image .material-icons {
  font-size: 48px;
}

.navigation-buttons {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
  transform: translateY(-50%);
  pointer-events: none;
}

.nav-button {
  background: rgba(0, 0, 0, 0);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: background-color 0.3s;
  pointer-events: auto;
  img{
    transition: 0.2s;

  }
}

.nav-button:hover img{
  scale: 1.2;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-button {
  background: rgba(0, 0, 0, 0.436);
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: white;
  transition: all 0.3s ease;
}

.action-button:hover {
  background: rgba(0, 0, 0, 0.7);
}

.action-button .material-icons {
  font-size: 1.1rem;
  font-weight: bold;
}

.zoom-button.reset {
  margin-left: 8px;
  padding: 4px;
  border-radius: 50%;
}

.zoom-button.reset:hover {
  background: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .back-button {
    top: 10px;
    left: 10px;
  }

  .nav-button {
    width: 32px;
    height: 32px;
  }

  .action-buttons {
    bottom: 10px;
  }

  .action-button {
    padding: 6px 12px;
  }
}
</style> 
<template>
  <div class="image-menu-container">
    <div class="menu-icon" @click.stop="toggleMenu">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="1"></circle>
        <circle cx="12" cy="5" r="1"></circle>
        <circle cx="12" cy="19" r="1"></circle>
      </svg>
    </div>
    
    <!-- 下拉菜单 -->
    <div v-if="showMenu" class="dropdown-menu" @click.stop>
      <div class="menu-item" @click="confirmDelete">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
        <span>删除图片</span>
      </div>
    </div>
    
    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="confirm-dialog" @click.stop>
      <div class="dialog-content">
        <h3>确认删除</h3>
        <p>您确定要删除这张图片吗？此操作无法撤销。</p>
        <div class="dialog-actions">
          <button @click="cancelDelete" class="cancel-btn">取消</button>
          <button @click="deleteImage" class="delete-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref,onMounted,onUnmounted } from 'vue'
import imageService from '../api/imageService'

const props = defineProps({
  imageId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['image-deleted'])

const showMenu = ref(false)
const showConfirmDialog = ref(false)

// 打开/关闭菜单
const toggleMenu = () => {
  showMenu.value = !showMenu.value
  if (showConfirmDialog.value) {
    showConfirmDialog.value = false
  }
}

// 显示确认对话框
const confirmDelete = () => {
  showConfirmDialog.value = true
  showMenu.value = false
}

// 取消删除
const cancelDelete = () => {
  showConfirmDialog.value = false
}

// 删除图片
const deleteImage = async () => {
  try {
    // 调用API删除图片
    // 注释掉的代码为实际API调用，目前使用模拟成功
    // await imageService.deleteImage(props.imageId)
    
    console.log(`删除图片: ${props.imageId}`)
    
    // 通知父组件图片已删除
    emit('image-deleted', props.imageId)
    
    // 关闭确认对话框
    showConfirmDialog.value = false
  } catch (error) {
    console.error('删除图片失败:', error)
    // 这里可以添加错误处理逻辑
  }
}

// 点击文档其他地方关闭菜单
const handleClickOutside = (e) => {
  if (showMenu.value || showConfirmDialog.value) {
    showMenu.value = false
    showConfirmDialog.value = false
  }
}

// 添加和移除全局点击事件监听器
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.image-menu-container {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  opacity: 0; /* 默认隐藏 */
  transition: opacity 0.3s ease;
}

/* 图片项悬停时显示菜单图标 */
.image-item:hover .image-menu-container {
  opacity: 1;
}

.menu-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.menu-icon:hover {
  background-color: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.dropdown-menu {
  position: absolute;
  top: 44px;
  right: 0;
  width: 160px;
  background-color: #2b2b2b;
  border-radius: 10px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
  z-index: 100;
  border: 1px solid #3a3a3a;
  animation: fadeInMenu 0.2s ease;
  overflow: hidden;
}

@keyframes fadeInMenu {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background-color: #3a3a3a;
}

.menu-item:first-child {
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.menu-item:last-child {
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
}

.menu-item svg {
  flex-shrink: 0;
  color: #ff4d4f;
}

.confirm-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.dialog-content {
  background-color: #2b2b2b;
  width: 90%;
  max-width: 400px;
  border-radius: 16px;
  padding: 24px;
  color: white;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
  border: 1px solid #3a3a3a;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.dialog-content h3 {
  margin-top: 0;
  color: #ff4d4f;
  font-size: 1.5em;
  margin-bottom: 16px;
}

.dialog-content p {
  line-height: 1.6;
  margin-bottom: 20px;
  color: #ddd;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.dialog-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 1em;
}

.cancel-btn {
  background-color: #4b4b4b;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a5a5a;
  transform: translateY(-2px);
}

.delete-btn {
  background-color: #ff4d4f;
  color: white;
}

.delete-btn:hover {
  background-color: #ff6668;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.4);
}

.delete-btn:active, .cancel-btn:active {
  transform: translateY(0);
}
</style> 
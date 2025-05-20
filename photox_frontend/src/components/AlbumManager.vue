<template>
    <div class="album-manager">
        <!-- 编辑模式按钮 -->
        <div class="edit-button" @click="toggleEditMode">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <span>{{ isEditMode ? '完成' : '编辑相册' }}</span>
        </div>

        <!-- 编辑模式下的相册列表 -->
        <div v-if="isEditMode" class="album-list">
            <div v-for="category in categories" :key="category" class="album-item">
                <span>{{ category }}</span>
                <!-- 不允许删除"全部"分类 -->
                <button v-if="category !== '全部'" class="delete-button" @click="confirmDelete(category)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
        </div>

        <!-- 确认删除对话框 -->
        <div v-if="showConfirmDialog" class="confirm-dialog">
            <div class="dialog-content">
                <h3>确认删除</h3>
                <p>您确定要删除 "{{ albumToDelete }}" 相册吗？此操作无法撤销，相册中的图片将被移到"全部"类别中。</p>
                <div class="dialog-actions">
                    <button @click="cancelDelete" class="cancel-btn">取消</button>
                    <button @click="deleteAlbum" class="delete-btn">删除</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import albumService from '../api/albumService'

const props = defineProps({
    categories: {
        type: Array,
        required: true
    }
})

const emit = defineEmits(['album-deleted'])

const isEditMode = ref(false)
const showConfirmDialog = ref(false)
const albumToDelete = ref('')

// 切换编辑模式
const toggleEditMode = () => {
    isEditMode.value = !isEditMode.value
}

// 确认删除对话框
const confirmDelete = (album) => {
    albumToDelete.value = album
    showConfirmDialog.value = true
}

// 取消删除
const cancelDelete = () => {
    showConfirmDialog.value = false
    albumToDelete.value = ''
}

// 删除相册
const deleteAlbum = async () => {
    try {
        // 这里应该调用API删除相册
        // 注释掉的代码是实际应该执行的API调用
        // const albumId = getAlbumIdByName(albumToDelete.value)
        // await albumService.deleteAlbum(albumId)

        console.log(`删除相册: ${albumToDelete.value}`)

        // 通知父组件已删除相册
        emit('album-deleted', albumToDelete.value)

        // 关闭确认对话框
        showConfirmDialog.value = false
        albumToDelete.value = ''
    } catch (error) {
        console.error('删除相册失败:', error)
        // 这里可以添加错误处理逻辑
    }
}

// 辅助函数：根据相册名称获取相册ID（实际应用中可能需要调整）
const getAlbumIdByName = (albumName) => {
    // 这里应该有一个从相册名称到ID的映射
    // 在实际应用中，这可能需要从后端获取或维护一个映射表
    return albumName // 示例中简单返回相册名称作为ID
}
</script>

<style scoped>
.album-manager {
    margin-top: 10px;
    position: relative;
}

.edit-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background-color: #176fd4;
    color: white;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95em;
    width: fit-content;
    margin-bottom: 15px;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.edit-button:hover {
    background-color: #1c84ef;
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

.album-list {
    background-color: #2b2b2b;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 15px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 1px solid #3a3a3a;
    transition: all 0.3s ease;
}

.album-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px;
    border-bottom: 1px solid #3a3a3a;
    color: #e8e8e8;
    transition: background-color 0.2s;
}

.album-item:hover {
    background-color: #333;
}

.album-item:last-child {
    border-bottom: none;
}

.delete-button {
    background: none;
    border: none;
    color: #ff4d4f;
    cursor: pointer;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.delete-button:hover {
    background-color: rgba(255, 77, 79, 0.15);
    transform: scale(1.1);
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
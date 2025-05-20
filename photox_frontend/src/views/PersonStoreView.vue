<template>
  <Header/>
  <div class="container">
    <div class="sidebar-box">
      <Sidebar class="sidebar" :categories="dynamicCategories" :selectedCategory="selectedCategory" @select-category="selectCategory" />
      <AlbumManager 
        :categories="dynamicCategories"
        @album-deleted="handleAlbumDeleted"
        class="album-manager"
      />
      <!-- From Uiverse.io by csemszepp -->
      <Uploader
        :categories="dynamicCategories"
        @upload-success="handleUploadSuccess"
        @category-created="addNewCategory"
      >
        <!-- 自定义触发区域 -->
        <!-- <template #trigger>
          <div class="custom-upload-trigger">
            <Uploader />
          </div>
        </template> -->
      </Uploader>
    </div>


    <div class="main">
      <!-- <input class="searchBox"
        v-model="searchKeyword" 
        placeholder="输入标签搜索..."
      /> -->

      <div class="input-wrapper-box">
        <button class="back-btn" :disabled="!isSearchActive" @click="resetSearch">
          <img src="/svg/backicon.svg" class="backsvg">

        </button>
        <!-- From Uiverse.io by vinodjangid07 -->
        <div class="input-wrapper">

          <img src="/svg/searchicon.svg" class="icon">
          <input type="text" name="text" class="input" placeholder="输入标签搜索..." v-model="searchKeyword" />
          <button class="Subscribe-btn" @click="performSearch">
            <svg xmlns="http://www.w3.org/2000/svg" width="30" height="10" viewBox="0 0 38 15" class="arrow">
              <path
                d="M10 7.519l-.939-.344h0l.939.344zm14.386-1.205l-.981-.192.981.192zm1.276 5.509l.537.843.148-.094.107-.139-.792-.611zm4.819-4.304l-.385-.923h0l.385.923zm7.227.707a1 1 0 0 0 0-1.414L31.343.448a1 1 0 0 0-1.414 0 1 1 0 0 0 0 1.414l5.657 5.657-5.657 5.657a1 1 0 0 0 1.414 1.414l6.364-6.364zM1 7.519l.554.833.029-.019.094-.061.361-.23 1.277-.77c1.054-.609 2.397-1.32 3.629-1.787.617-.234 1.17-.392 1.623-.455.477-.066.707-.008.788.034.025.013.031.021.039.034a.56.56 0 0 1 .058.235c.029.327-.047.906-.39 1.842l1.878.689c.383-1.044.571-1.949.505-2.705-.072-.815-.45-1.493-1.16-1.865-.627-.329-1.358-.332-1.993-.244-.659.092-1.367.305-2.056.566-1.381.523-2.833 1.297-3.921 1.925l-1.341.808-.385.245-.104.068-.028.018c-.011.007-.011.007.543.84zm8.061-.344c-.198.54-.328 1.038-.36 1.484-.032.441.024.94.325 1.364.319.45.786.64 1.21.697.403.054.824-.001 1.21-.09.775-.179 1.694-.566 2.633-1.014l3.023-1.554c2.115-1.122 4.107-2.168 5.476-2.524.329-.086.573-.117.742-.115s.195.038.161.014c-.15-.105.085-.139-.076.685l1.963.384c.192-.98.152-2.083-.74-2.707-.405-.283-.868-.37-1.28-.376s-.849.069-1.274.179c-1.65.43-3.888 1.621-5.909 2.693l-2.948 1.517c-.92.439-1.673.743-2.221.87-.276.064-.429.065-.492.057-.043-.006.066.003.155.127.07.099.024.131.038-.063.014-.187.078-.49.243-.94l-1.878-.689zm14.343-1.053c-.361 1.844-.474 3.185-.413 4.161.059.95.294 1.72.811 2.215.567.544 1.242.546 1.664.459a2.34 2.34 0 0 0 .502-.167l.15-.076.049-.028.018-.011c.013-.008.013-.008-.524-.852l-.536-.844.019-.012c-.038.018-.064.027-.084.032-.037.008.053-.013.125.056.021.02-.151-.135-.198-.895-.046-.734.034-1.887.38-3.652l-1.963-.384zm2.257 5.701l.791.611.024-.031.08-.101.311-.377 1.093-1.213c.922-.954 2.005-1.894 2.904-2.27l-.771-1.846c-1.31.547-2.637 1.758-3.572 2.725l-1.184 1.314-.341.414-.093.117-.025.032c-.01.013-.01.013.781.624zm5.204-3.381c.989-.413 1.791-.42 2.697-.307.871.108 2.083.385 3.437.385v-2c-1.197 0-2.041-.226-3.19-.369-1.114-.139-2.297-.146-3.715.447l.771 1.846z" fill="white">
              </path>
            </svg>搜索
          </button>
        </div>
      </div>



      <div class="image-grid">
        <transition-group name="image-fade" tag="div" class="image-grid-inner">
          <div v-for="image in filteredImages" :key="image.id" class="image-item" @click.stop="selectImage(image)">
            <img :src="image.thumbnail" />
            <ImageItemMenu 
              :imageId="image.id"
              @image-deleted="handleImageDelete"
            />
            <div class="meta">
              <span>{{ Array.isArray(image.tags) ? image.tags.join(', ') : image.tags || '' }}</span>
              <span>{{ image.size }}</span>
            </div>
          </div>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import Uploader from '@/components/Uploader.vue'
import Header from "../components/Header.vue"
import ImageItemMenu from '../components/ImageItemMenu.vue'
import AlbumManager from '../components/AlbumManager.vue'
import imageService from '../api/imageService'


// 模拟数据
const images = ref([])
const loading = ref(false)
const error = ref(null)

// 维护一个全局的分类集合
const allCategories = ref(['全部'])

// 动态分类列表（实际用于 Sidebar 和 Uploader）
const dynamicCategories = allCategories

// 从图片列表中提取所有分类
const extractCategories = (imageList) => {
    const categories = new Set(['全部'])
    imageList.forEach(image => {
        if (image.category) {
            categories.add(image.category)
        }
    })
    return Array.from(categories)
}

// 获取图片列表
const fetchImages = async () => {
    loading.value = true
    error.value = null
    try {
        const response = await imageService.getUserImages()
        console.log('获取图片列表响应数据:', response)
        
        // 检查响应格式
        if (!response) {
            throw new Error('获取图片列表失败：响应为空')
        }
        
        // 处理分页数据
        const imageList = response.results || response
        if (!Array.isArray(imageList)) {
            console.error('图片列表格式错误:', imageList)
            throw new Error('获取图片列表失败：数据格式错误')
        }
        
        // 转换图片数据
        images.value = imageList.map(image => {
            console.log('处理图片数据:', image)
            return {
                id: image.id,
                thumbnail: image.image_url,
                url: image.image_url,
                tags: typeof image.tags === 'string' ? JSON.parse(image.tags) : (image.tags || []),
                category: image.category || '未分类',
                size: formatFileSize(image.file_size),
                dimensions: `${image.width || 0}x${image.height || 0}`,
                type: image.file_type || '未知',
                createdAt: new Date(image.created_at).toLocaleString()
            }
        })
        console.log('处理后的图片列表:', images.value)
        
        // 合并所有新建过的分类和图片中提取的分类
        const extracted = extractCategories(images.value)
        allCategories.value = Array.from(new Set([...allCategories.value, ...extracted]))
        // dynamicCategories.value = allCategories.value // dynamicCategories 直接用 allCategories
        
        // 保存分页信息
        if (response.count !== undefined) {
            totalImages.value = response.count
            nextPageUrl.value = response.next
            previousPageUrl.value = response.previous
        }
        // 不再赋值 filteredImages
    } catch (err) {
        console.error('获取图片列表失败:', err)
        error.value = err.message || '获取图片列表失败，请稍后重试'
        images.value = [] // 清空图片列表
        // 不再赋值 filteredImages
    } finally {
        loading.value = false
    }
}

// 添加分页相关的状态
const totalImages = ref(0)
const nextPageUrl = ref(null)
const previousPageUrl = ref(null)

// 加载更多图片
const loadMoreImages = async () => {
    if (!nextPageUrl.value || loading.value) return
    
    try {
        loading.value = true
        const response = await imageService.getUserImages({ page: nextPageUrl.value })
        
        if (response && response.results && Array.isArray(response.results)) {
            const newImages = response.results.map(image => ({
                id: image.id,
                thumbnail: image.image_url,
                url: image.image_url,
                tags: typeof image.tags === 'string' ? JSON.parse(image.tags) : (image.tags || []),
                category: image.category || '未分类',
                size: formatFileSize(image.file_size),
                dimensions: `${image.width || 0}x${image.height || 0}`,
                type: image.file_type || '未知',
                createdAt: new Date(image.created_at).toLocaleString()
            }))
            
            images.value = [...images.value, ...newImages]
            nextPageUrl.value = response.next
            previousPageUrl.value = response.previous
        }
    } catch (err) {
        console.error('加载更多图片失败:', err)
        error.value = '加载更多图片失败，请稍后重试'
    } finally {
        loading.value = false
    }
}

// 在组件挂载时获取图片列表
onMounted(() => {
    fetchImages()
})

// 文件大小格式化
const formatFileSize = (bytes) => {
    if (!bytes) return '0 B'
    const units = ['B', 'KB', 'MB']
    let size = bytes
    let unitIndex = 0
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`
}

// const categories = ['全部', 'nature', 'people', 'art']
const selectedCategory = ref('全部')
const searchKeyword = ref('')
const isSearchActive = ref(false)

// 计算属性处理过滤逻辑
const filteredImages = computed(() => {
    console.log('过滤图片列表:', {
        selectedCategory: selectedCategory.value,
        searchKeyword: searchKeyword.value,
        totalImages: images.value.length
    })
    
    return images.value.filter(img => {
        const matchesCategory = selectedCategory.value === '全部' || img.category === selectedCategory.value
        const matchesTag = !searchKeyword.value || img.tags.some(tag => tag.includes(searchKeyword.value))
        return matchesCategory && matchesTag
    })
})

function performSearch() {
  isSearchActive.value = true
}

function resetSearch() {
  searchKeyword.value = ''
  isSearchActive.value = false
}

const router = useRouter()
const viewDetail = (id) => {
  router.push(`/photodetail/${id}`)
}

const selectCategory = (category) => {
  selectedCategory.value = category
  performSearch()
}


const handleUploadSuccess = async (uploadedImages) => {
    console.log('上传成功，重新获取图片列表')
    await fetchImages()
}

const addNewCategory = (newCategory) => {
  const category = newCategory.toString().trim()
  if (!category) return
    
    console.log('添加新分类:', category)
  
  // 避免重复
    if (!allCategories.value.includes(category)) {
        allCategories.value.push(category)
        console.log('更新后的分类列表:', allCategories.value)
  }
  // 自动选中新分类
  selectedCategory.value = category
    console.log('当前选中的分类:', selectedCategory.value)
    // 更新过滤后的图片列表
  performSearch()
}

const selectedImage = ref(null)

// 选择图片来显示菜单
const selectImage = (image) => {
  selectedImage.value = image
}

// 处理图片删除
const handleImageDelete = async (imageId) => {
  try {
        await imageService.deleteImage(imageId)
    console.log(`删除图片：${imageId}`)
    
        // 重新获取图片列表
        await fetchImages()
  } catch (error) {
    console.error('删除图片失败:', error)
        error.value = '删除图片失败，请稍后重试'
  }
}

// 处理相册删除
const handleAlbumDeleted = (albumName) => {
  // 从分类列表中移除该相册
  const index = dynamicCategories.value.findIndex(cat => cat === albumName)
  if (index !== -1) {
    dynamicCategories.value.splice(index, 1)
  }
  
  // 如果当前选中的就是被删除的相册，则切换到"全部"分类
  if (selectedCategory.value === albumName) {
    selectedCategory.value = '全部'
  }
  
  // 重新获取图片列表以更新分类
  fetchImages()
}
</script>

<style scoped>
.container {
  display: flex;
  height: 90vh;
  overflow: hidden;
  width: 100%;
  background-color: rgb(38, 38, 38);
}

.sidebar-box {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #3a3a3a;
  padding: 16px;
  width: 240px;
  background-color: #262626;
  
  .sidebar {
    flex: 1;
    margin-bottom: 20px;
  }
  
  .album-manager {
    margin-bottom: 20px;
  }

  /* From Uiverse.io by csemszepp */
  .custum-file-upload {
    height: 25vh;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: space-between;
    gap: 20px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    border: 2px solid #3a3a3a;
    border-radius: 8px;
    background-color: rgb(38, 38, 38);
    transition: all 0.3s ease;
  }

  .custum-file-upload:hover {
    border-color: #176fd4;
    background-color: #303030;
  }

  .custum-file-upload .icon {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .custum-file-upload .icon svg {
    height: 80px;
    fill: #e8e8e8;
  }

  .custum-file-upload .text {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .custum-file-upload .text span {
    font-weight: 400;
    color: #e8e8e8;
  }

  .custum-file-upload input {
    display: none;
  }
}

.main {
  overflow-y: auto;
  flex: 1;
  padding: 20px 24px;
  scrollbar-width: thin;
  scrollbar-color: #555 #333;
}

.main::-webkit-scrollbar {
  width: 8px;
}

.main::-webkit-scrollbar-track {
  background: #333;
}

.main::-webkit-scrollbar-thumb {
  background-color: #555;
  border-radius: 4px;
}

.image-grid {
  width: 100%;
  padding: 10px 0;
}

.image-grid-inner {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  grid-gap: 24px;
}

.image-item {
  border: 1px solid #3a3a3a;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
  background-color: #2b2b2b;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.image-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  border-color: #176fd4;
}

.image-item img {
  width: 100%;
  height: 240px;
  object-fit: cover;
  transition: all 0.5s ease;
}

.image-item:hover img {
  transform: scale(1.05);
}

.meta {
  padding: 12px 16px;
  font-size: 0.9em;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  background-color: #2b2b2b;
  color: #e8e8e8;
  border-top: 1px solid #3a3a3a;
}

.searchBox {
  margin-top: 10px;
  margin-bottom: 10px;
  height: 25px;
}

.input-wrapper-box {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 24px;

  .back-btn {
    margin-right: 12px;
    padding: 8px 14px;
    background-color: #333;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    color: #e8e8e8;
    transition: background-color 0.2s;
  }

  .back-btn:hover:not(:disabled) {
    background-color: #444;
  }

  .back-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .backsvg {
    height: 20px;
    margin-right: 8px;
  }

  .input-wrapper {
    width: fit-content;
    height: 48px;
    border-radius: 24px;
    padding: 5px;
    box-sizing: content-box;
    display: flex;
    align-items: center;
    background-color: #333;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }
  
  .input-wrapper:focus-within {
    box-shadow: 0 2px 15px rgba(23, 111, 212, 0.3);
  }

  .icon {
    width: 30px;
    fill: rgb(255, 255, 255);
    margin-left: 12px;
    transition: all 0.3s;
  }

  .input {
    width: 200px;
    height: 100%;
    border: none;
    outline: none;
    padding-left: 15px;
    background-color: transparent;
    color: white;
    font-size: 1em;
  }

  .input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0px 1000px #313131 inset;
    -webkit-text-fill-color: #ffffff;
  }

  .Subscribe-btn {
    height: 80%;
    padding: 0 20px;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    background-color: #176fd4;
    color: white;
    font-weight: 500;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    transition: all 0.3s;
    margin-right: 6px;
  }

  .arrow {
    position: absolute;
    margin-right: 150px;
    transition: all 0.3s;
  }

  .input-wrapper:active .icon {
    transform: scale(1.3);
  }

  .Subscribe-btn:hover {
    background-color: #2180ea;
  }

  .Subscribe-btn:hover .arrow {
    margin-right: 0;
    animation: jello-vertical 0.9s both;
    transform-origin: right;
  }

  @keyframes jello-vertical {
    0% {
      transform: scale3d(1, 1, 1);
    }

    30% {
      transform: scale3d(0.75, 1.25, 1);
    }

    40% {
      transform: scale3d(1.25, 0.75, 1);
    }

    50% {
      transform: scale3d(0.85, 1.15, 1);
    }

    65% {
      transform: scale3d(1.05, 0.95, 1);
    }

    75% {
      transform: scale3d(0.95, 1.05, 1);
    }

    100% {
      transform: scale3d(1, 1, 1);
    }
  }

  .Subscribe-btn:active {
    transform: scale(0.95);
  }
}

/* 添加淡入淡出动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }
  
  .sidebar-box {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #3a3a3a;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
}

/* 图片项过渡动画 */
.image-fade-move {
  transition: transform 0.5s ease;
}

.image-fade-enter-active {
  transition: all 0.5s ease;
}

.image-fade-leave-active {
  transition: all 0.3s ease;
  position: absolute;
}

.image-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.image-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
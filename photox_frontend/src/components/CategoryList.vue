<template>
  <div class="category-container" v-show="!props.isExpanded || isExpanded">
    <div class="category-header">
      <button v-if="isExpanded" class="back-btn" @click="collapseCategory">
        <img src="/svg/backicon.svg" class="backsvg">
        返回
      </button>
      <h2 class="category-title">{{ category.name }}</h2>
    </div>

    <div class="image-grid">
      <div
        v-for="(img, idx) in displayImages"
        :key="idx"
        class="image-item"
        @click="navigateToDetail(img)"
      >
        <img :src="img.img" :alt="`${category.name} - ${idx + 1}`" />
      </div>
    </div>

    <!-- 首页显示更多按钮 -->
    <div v-if="!isExpanded && category.images.length > 4" class="view-more">
      <button class="view-more-btn" @click="expandCategory">
        查看更多
      </button>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="isExpanded && totalImages > 0">
      <button 
        class="pagination-btn" 
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
      <button 
        class="pagination-btn" 
        :disabled="currentPage >= totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../api'

const props = defineProps({
  category: {
    type: Object,
    required: true
  },
  categoryIndex: {
    type: Number,
    required: true
  },
  getOriginalCategoryIndex: {
    type: Function,
    required: true
  },
  getOriginalImageIndex: {
    type: Function,
    required: true
  },
  isExpanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['expand', 'collapse'])

const router = useRouter()
const images = ref([])
const loading = ref(false)
const error = ref(null)
const isExpanded = ref(false)

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(12) // 每页显示12张图片
const totalImages = ref(0)
const totalPages = computed(() => Math.ceil(totalImages.value / pageSize.value))

// 获取图片列表
const fetchImages = async () => {
  if (!isExpanded.value) return
  
  loading.value = true
  error.value = null
  try {
    const response = await apiService.images.getList({
      category: props.category.name,
      is_public: true,
      page: currentPage.value,
      page_size: pageSize.value
    })

    if (!response) {
      throw new Error('获取图片列表失败：响应为空')
    }

    const imageList = response.results || response
    if (!Array.isArray(imageList)) {
      throw new Error('获取图片列表失败：数据格式错误')
    }

    // 过滤出当前分类的图片
    const categoryImages = imageList.filter(image => 
      image.category === props.category.name
    )

    images.value = categoryImages.map(image => ({
      id: image.id,
      img: image.image_url,
      colors: image.colors || []
    }))
    totalImages.value = categoryImages.length
  } catch (err) {
    console.error('获取图片列表失败:', err)
    error.value = err.message || '获取图片列表失败，请稍后重试'
    images.value = []
  } finally {
    loading.value = false
  }
}

// 计算要显示的图片
const displayImages = computed(() => {
  if (!isExpanded.value) {
    // 首页只显示4张图片
    return props.category.images.slice(0, 4)
  }
  return images.value
})

// 展开分类
const expandCategory = async () => {
  isExpanded.value = true
  currentPage.value = 1
  emit('expand', props.category.name)
  await fetchImages()
}

// 收起分类
const collapseCategory = () => {
  isExpanded.value = false
  currentPage.value = 1
  images.value = []
  emit('collapse')
}

// 切换页面
const changePage = async (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  await fetchImages()
  // 滚动到顶部
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// 监听分类变化
watch(() => props.category.name, () => {
  isExpanded.value = false
  currentPage.value = 1
  if (isExpanded.value) {
    fetchImages()
  }
})

// 监听展开状态变化
watch(() => props.isExpanded, (newValue) => {
  isExpanded.value = newValue
  if (newValue) {
    expandCategory()
  } else {
    collapseCategory()
  }
}, { immediate: true })

// 导航到详情页
const navigateToDetail = (img) => {
  if (img.id) {
    window.open(`/photodetail/${img.id}?fromHome=true`, '_blank')
  } else {
    console.error('图片缺少ID:', img)
  }
}

// 初始加载
onMounted(() => {
  if (isExpanded.value) {
    fetchImages()
  }
})
</script>

<style scoped>
.category-container {
  margin-bottom: 40px;
}

.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background-color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  color: var(--text-color);
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

.backsvg {
  height: 20px;
  margin-right: 8px;
  filter: brightness(0.6);
  transition: filter 0.3s ease;
}

.back-btn:hover .backsvg {
  filter: brightness(1);
}

.category-title {
  margin: 0;
  font-size: 24px;
  color: var(--text-color);
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 10px;
  transition: color 0.3s ease, border-color 0.3s ease;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 10px;
  transition: all 0.3s ease;
}

.image-item {
  position: relative;
  padding-bottom: 100%;
  cursor: pointer;
  overflow: hidden;
  border-radius: 8px;
  transition: transform 0.3s ease;
  background-color: var(--secondary-color);
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 0.3s ease;
}

.image-item:hover img {
  filter: brightness(1.1);
}

@media (max-width: 768px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
  }
  
  .category-title {
    font-size: 20px;
  }
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 16px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--secondary-color);
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-color);
  font-size: 14px;
}

/* 查看更多按钮样式 */
.view-more {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.view-more-btn {
  padding: 8px 24px;
  border: 1px solid var(--primary-color);
  border-radius: 20px;
  background-color: transparent;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.view-more-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

/* 展开时的网格样式 */
.category-container.expanded .image-grid {
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
}
</style> 
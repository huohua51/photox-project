<template>
  <div class="app-container">
    <!-- 搜索框 -->
    <div class="search-box">
      <div class="search-input-wrapper">
        <input
          type="text"
          v-model="searchKeyword"
          placeholder="搜索图片..."
          @input="handleSearch"
          class="search-input"
        />
        <button 
          v-if="searchKeyword" 
          @click="clearSearch" 
          class="clear-button"
          title="清除搜索"
        >
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 无结果提示 -->
    <div v-if="showNoResults" class="no-results">
      <p>没有找到与 "{{ searchKeyword }}" 相关的图片</p>
      <button @click="clearSearch" class="reset-button">清除搜索</button>
    </div>

    <!-- 分类组件 -->
    <div class="categories" v-else>
      <CategoryList
        v-for="category in displayCategories"
        :key="category.name"
        :category="category"
        :categoryIndex="getOriginalCategoryIndex(category.name)"
        :getOriginalCategoryIndex="getOriginalCategoryIndex"
        :getOriginalImageIndex="getOriginalImageIndex"
        :isExpanded="expandedCategory === category.name"
        @expand="handleCategoryExpand"
        @collapse="handleCategoryCollapse"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import CategoryList from '@/components/CategoryList.vue'
import api from '@/api'

// 响应式数据
const categories = ref([])
const originalCategories = ref([])
const searchKeyword = ref("")
const expandedCategory = ref(null)

// 计算要显示的分类
const displayCategories = computed(() => {
  if (expandedCategory.value) {
    return filteredCategories.value.filter(cat => cat.name === expandedCategory.value)
  }
  return filteredCategories.value
})

// 无结果提示
const showNoResults = computed(() => searchKeyword.value.trim() && filteredCategories.value.length === 0)

// 获取原始分类中的分类索引
const getOriginalCategoryIndex = (categoryName) => {
  return originalCategories.value.findIndex(cat => cat.name === categoryName)
}

// 获取原始分类中的图片索引
const getOriginalImageIndex = (categoryName, imgUrl) => {
  const originalCategory = originalCategories.value.find(cat => cat.name === categoryName)
  if (!originalCategory) return 0
  return originalCategory.images.findIndex(img => img === imgUrl)
}

// 搜索过滤逻辑
const filteredCategories = computed(() => {
  if (!searchKeyword.value.trim()) return categories.value

  const keyword = searchKeyword.value.trim().toLowerCase()
  return categories.value
    .map((cat) => {
      const filteredImgs = cat.images.filter(img => {
        // 检查图片对象的属性
        if (typeof img === 'string') {
          return img.toLowerCase().includes(keyword)
        } else if (img && typeof img === 'object') {
          // 检查图片对象的各个属性
          return (
            (img.title && img.title.toLowerCase().includes(keyword)) ||
            (img.tags && img.tags.some(tag => tag.toLowerCase().includes(keyword))) ||
            (img.category && img.category.toLowerCase().includes(keyword))
          )
        }
        return false
      })
      if (filteredImgs.length) return { ...cat, images: filteredImgs }
      if (cat.name.toLowerCase().includes(keyword)) return cat
      return null
    })
    .filter(Boolean)
})

// 清除搜索
const clearSearch = () => {
  searchKeyword.value = ""
}

// 获取公开图片和类别信息
const fetchPublicImages = async () => {
  try {
    console.log('获取公开图片的请求参数:', { is_public: true })
    const response = await api.images.getList({ 
      is_public: true,
      page_size: 100  // 增加每页显示数量
    })
    const data = response.data || response
    
    // 按分类组织图片
    const categoriesMap = new Map()
    data.results.forEach(image => {
      const category = image.category || '未分类'
      if (!categoriesMap.has(category)) {
        categoriesMap.set(category, {
          name: category,
          images: []
        })
      }
      categoriesMap.get(category).images.push({
        id: image.id,
        img: image.image_url,
        colors: image.colors || []
      })
    })
    
    // 转换为数组
    const categoriesArray = Array.from(categoriesMap.values())
    originalCategories.value = categoriesArray
    categories.value = [...categoriesArray]
  } catch (error) {
    console.error("获取公开图片失败:", error)
  }
}

// 处理分类展开
const handleCategoryExpand = (categoryName) => {
  expandedCategory.value = categoryName
  // 清除搜索关键词
  searchKeyword.value = ""
}

// 处理分类收起
const handleCategoryCollapse = () => {
  expandedCategory.value = null
}

// 初始化加载数据
onMounted(() => {
  fetchPublicImages()
})
</script>

<style scoped>
.app-container {
  margin: 0 auto;
  padding: 20px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
}

.search-box {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  width: 100%;
}

.search-input-wrapper {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 8px 15px;
  font-size: 16px;
  border: 2px solid var(--border-color);
  border-radius: 5px;
  background-color: var(--secondary-color);
  color: var(--text-color);
  transition: border-color 0.3s, background-color 0.3s, color 0.3s;
}

.search-input:focus {
  border-color: var(--primary-color);
  outline: none;
}

.clear-button {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-color);
  opacity: 0.7;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s, opacity 0.3s;
}

.clear-button:hover {
  opacity: 1;
}

.clear-button:active {
  transform: translateY(-50%) scale(0.95);
}

.no-results {
  text-align: center;
  color: var(--text-color);
  opacity: 0.7;
}

.reset-button {
  padding: 8px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.reset-button:hover {
  background-color: var(--primary-color);
  opacity: 0.9;
}
</style> 
<template>
    <div v-if="image" class="detail-container">
        <img :src="image.url" class="detail-image" />
        <div class="info">
            <p>标签：{{ image.tags.join(', ') }}</p>
            <p>分类：{{ image.category }}</p>
            <p>尺寸：{{ image.dimensions }}</p>
            <p>大小：{{ image.size }}</p>
            <p>类型：{{ image.type }}</p>
            <p>创建时间：{{ image.createdAt }}</p>
        </div>
    </div>
</template>
  
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const image = ref(null)

// 根据ID获取图片详细信息（实际应调用API）
onMounted(() => {
    const id = Number(route.params.id)
    // 这里可以替换为真实API调用
    image.value = {
        id: 1,
        url: '/img/QQ图片20231213202410.jpg',
        tags: ['风景', '旅行'],
        category: 'nature',
        dimensions: '1920x1080',
        size: '2.4MB',
        type: 'JPEG',
        createdAt: '2023-01-15'
    }
})

  //真实api调用
//   const route = useRoute()
// const image = ref(null)
// const loading = ref(true)
// const error = ref(null)

// onMounted(async () => {
//   try {
//     const response = await imageApi.getImageDetail(route.params.id)
//     image.value = response.data
//   } catch (err) {
//     error.value = '获取图片信息失败，请稍后重试'
//     console.error('API Error:', err)
//   } finally {
//     loading.value = false
//   }
// })
</script>
  
<style scoped>
.detail-container {
    display: flex;
    padding: 30px;
    gap: 30px;
}

.detail-image {
    max-width: 60%;
    max-height: 80vh;
    object-fit: contain;
}

.info {
    flex: 1;
    padding: 20px;
}
</style>
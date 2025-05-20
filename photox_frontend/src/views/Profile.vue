<template>
  <div class="profile-container">
    <h2>个人信息</h2>
    <div v-if="user">
      <p><strong>用户名：</strong>{{ user.username }}</p>
      <p><strong>邮箱：</strong>{{ user.email }}</p>
    </div>
    <div v-else>
      <p>未登录，请先登录。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const user = ref(null)

onMounted(async () => {
  try {
    const res = await axios.get('/api/user/profile')
    user.value = res.data
  } catch (e) {
    user.value = null
  }
})
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
</style> 
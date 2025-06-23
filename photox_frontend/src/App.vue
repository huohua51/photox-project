<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import Header from "./components/Header.vue"
import { computed } from 'vue'
import { useThemeStore } from './stores/theme'

const route = useRoute()
const themeStore = useThemeStore()

const showNavbar = computed(() => {
  // 首页始终显示导航栏
  if (route.name === 'home') return true
  // 图片详情页面根据 fromHome 参数决定是否显示导航栏
  if (route.name === 'photodetail' && route.query.fromHome) return false
  // 其他页面根据 meta 配置显示
  return route.meta.showNavbar
})
</script>

<template>
  <div class="body" :class="{ 'with-navbar': showNavbar, 'dark': themeStore.isDarkMode }">
    <Header v-if="showNavbar"/>
    <RouterView />
  </div>
</template>

<style>
:root {
  --bg-color: #ffffff;
  --text-color: #333333;
  --primary-color: #1e90ff;
  --secondary-color: #f5f5f5;
  --border-color: #e0e0e0;
}

:root.dark {
  --bg-color: rgb(38, 38, 38);
  --text-color: #e0e0e0;
  --primary-color: #1e90ff;
  --secondary-color: #333333;
  --border-color: #555555;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}
</style>

<style scoped>
.body {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  overflow-x: hidden;
  /* 禁止水平滚动条 */
  font-size: 1vw;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}


</style>

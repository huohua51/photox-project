<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
// import Header from "./components/Header.vue"

</script>

<template>
  <div class="body">
    <!-- <Header/> -->
    <RouterView />
  </div>
</template>

<style scoped>
.body {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  overflow-x: hidden;
  /* 禁止水平滚动条 */
  font-size: 1vw;
  color: aliceblue;
  background-color: rgb(38, 38, 38);
}
</style>

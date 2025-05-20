<template>
  <div class="sidebar">
    <div 
      v-for="category in categories" 
      :key="category"
      :class="{ 'active': selectedCategory === category }"
      @click="$emit('select-category', category)"
    >
      {{ category }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  categories: Array,
  selectedCategory: String
})
defineEmits(['select-category'])
</script>

<style scoped>
.sidebar {
  width: 100%;
  padding: 0;
}

.sidebar div {
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 6px;
  color: #e8e8e8;
  transition: all 0.2s ease;
  font-weight: 500;
}

.sidebar div:hover {
  background: rgba(23, 111, 212, 0.15);
  color: white;
}

.sidebar div.active {
  background: #176fd4;
  color: white;
  box-shadow: 0 2px 8px rgba(23, 111, 212, 0.3);
}
</style>
<template>
  <div class="info-panel">
    <h2 class="panel-title">图片信息</h2>
    
    <!-- 分类信息 -->
    <div class="info-section">
      <h3>分类</h3>
      <p>{{ currentCategoryName }}</p>
    </div>

    <!-- 位置信息 -->
    <div class="info-section">
      <h3>位置</h3>
      <p>{{ currentPosition }} / {{ totalImages }}</p>
    </div>

    <!-- 图片尺寸 -->
    <div class="info-section">
      <h3>尺寸</h3>
      <p>{{ imageDimensions.width }} x {{ imageDimensions.height }} 像素</p>
    </div>

    <!-- 文件大小 -->
    <div class="info-section">
      <h3>文件大小</h3>
      <p>{{ imageSizeMB }} MB</p>
    </div>

    <!-- 文件格式 -->
    <div class="info-section">
      <h3>格式</h3>
      <p>{{ imageFormat }}</p>
    </div>

    <!-- 主要颜色 -->
    <div class="info-section">
      <h3>主要颜色</h3>
      <div class="color-palette">
        <div
          v-for="(color, index) in dominantColors"
          :key="index"
          class="color-swatch"
          :style="{ backgroundColor: color }"
          :title="color"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentPosition: {
    type: Number,
    required: true
  },
  totalImages: {
    type: Number,
    required: true
  },
  dominantColors: {
    type: Array,
    default: () => []
  },
  currentCategoryName: {
    type: String,
    required: true
  },
  imageDimensions: {
    type: Object,
    required: true
  },
  imageSizeMB: {
    type: String,
    required: true
  },
  imageFormat: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.info-panel {
  flex: 0 0 30%;
  padding: 20px;
  background-color: #2a2a2a;
  border-radius: 8px;
  color: #fff;
}

.panel-title {
  font-size: 24px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #1e90ff;
}

.info-section {
  margin-bottom: 20px;
}

.info-section h3 {
  font-size: 16px;
  color: #1e90ff;
  margin-bottom: 8px;
}

.info-section p {
  font-size: 14px;
  color: #ccc;
  margin: 0;
}

.color-palette {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.color-swatch {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.color-swatch:hover {
  transform: scale(1.1);
}

@media (max-width: 768px) {
  .info-panel {
    padding: 15px;
  }

  .panel-title {
    font-size: 20px;
  }

  .info-section h3 {
    font-size: 14px;
  }

  .info-section p {
    font-size: 12px;
  }

  .color-swatch {
    width: 25px;
    height: 25px;
  }
}
</style> 
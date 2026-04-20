<template>
  <div class="test-embed-page">
    <!-- 1. 外层容器：设置 overflow: hidden 像一个相框 -->
    <div class="iframe-clipper">
      <iframe
        src="http://localhost:9621/webui/#/documents"
        frameborder="0"
        class="full-iframe"
      ></iframe>
    </div>
  </div>
</template>

<style scoped>
.test-embed-page {
  width: 100%;
  height: calc(100vh - 60px);
}

.iframe-clipper {
  width: 100%;
  height: 100%;
  overflow: hidden; /* 关键：剪掉超出部分 */
  position: relative;
}

.full-iframe {
  width: 100%;
  /* 关键：把高度设置得比容器高，然后向上移动，把 header 推到视野之外 */
  height: calc(100% + 37px);
  margin-top: -37px; /* 这里的 44px 对应 h-11 的高度 */

  /* 如果还有横向边距，也可以微调 */
  border: none;
}
</style>
<script setup lang="ts">
</script>
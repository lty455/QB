<script setup>
import { ref } from 'vue'
const iframeRef = ref(null)

const onIframeLoad = () => {
  try {
    const iframe = iframeRef.value
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document

    const style = document.createElement('style')
    style.textContent = `
      .ant-tabs-nav, div[role="tablist"], .tabs-header {
        display: none !important;
      }
      .ant-tabs-content-holder {
        height: 100% !important;
      }
    `
    iframeDoc.head.appendChild(style)

    const win = iframe.contentWindow
    const _push = win.history.pushState
    win.history.pushState = (...args) => {
      _push.apply(win.history, args)
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  } catch (e) {}
}
</script>

<template>
  <div class="test-embed-page">
    <iframe
      ref="iframeRef"
      src="http://localhost:9621/webui/#/retrieval"
      frameborder="0"
      class="full-iframe"
      @load="onIframeLoad"
    ></iframe>
  </div>
</template>

<style scoped>
.test-embed-page {
  width: 100%;
  height: calc(100vh - 60px);
}
.full-iframe {
  width: 100%;
  height: 100%;
}
</style>
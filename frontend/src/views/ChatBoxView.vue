<template>
  <div class="chat-container">
    <!-- 聊天窗口主体 -->
    <div class="chat-window">
      <!-- 顶部标题栏 -->
      <div class="chat-header">
        <div class="header-avatar">🤖</div>
        <div class="header-info">
          <h2 class="chat-title">智能聊天助手</h2>
          <span class="chat-status">🟢 在线</span>
        </div>
      </div>

      <!-- 聊天记录区域 -->
      <div class="chat-history" ref="chatHistoryRef">
        <!-- 空状态提示 -->
        <div v-if="messages.length === 0" class="empty-tip">
          <div class="empty-icon">👋</div>
          <p>你好！我是你的专属情报分析助手，有什么可以帮你的吗？</p>
        </div>

        <!-- 聊天消息列表 (加入过渡动画) -->
        <transition-group name="msg-fade" tag="div" class="message-list">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message-wrapper"
            :class="msg.role === 'user' ? 'is-user' : 'is-ai'"
          >
            <!-- 头像 -->
            <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>

            <!-- 气泡 -->
            <div class="message-bubble">
              {{ msg.content }}
            </div>
          </div>

          <!-- 加载状态 (拟物化打字动画) -->
          <div v-if="isLoading" key="loading" class="message-wrapper is-ai">
            <div class="avatar">🤖</div>
            <div class="message-bubble typing-bubble">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </transition-group>
      </div>

      <!-- 输入框区域 -->
      <div class="input-area">
        <div class="input-box">
          <input
            type="text"
            v-model="inputMessage"
            @keyup.enter="sendMessage"
            placeholder="输入你的问题，按回车发送..."
            :disabled="isLoading"
            class="chat-input"
          />
          <button
            @click="sendMessage"
            :disabled="isLoading || !inputMessage.trim()"
            class="send-btn"
            :class="{ 'is-active': inputMessage.trim() && !isLoading }"
          >
            <!-- 发送图标 (SVG) -->
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'

// ===================== 核心配置（保持你的原样） =====================
const API_BASE_URL = 'http://localhost:8000'
const CHAT_API_URL = `${API_BASE_URL}/v1/chat/completions`
const MODEL_NAME = 'qwen-8b'
// ====================================================================

const inputMessage = ref('')
const isLoading = ref(false)
const messages = ref([])
const chatHistoryRef = ref(null) // 用于精确控制滚动

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMsg = {
    role: 'user',
    content: inputMessage.value
  }
  messages.value.push(userMsg)

  inputMessage.value = ''
  isLoading.value = true
  await scrollToBottom() // 用户发送后立刻滚动到底部

  try {
    const requestBody = {
      model: MODEL_NAME,
      messages:[...messages.value],
      temperature: 0.7,
      max_tokens: 2048,
      stream: false
    }

    const response = await axios.post(CHAT_API_URL, requestBody, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 30000
    })

    if (response.data && response.data.choices && response.data.choices.length > 0) {
      const assistantMsg = {
        role: 'assistant',
        content: response.data.choices[0].message.content
      }
      messages.value.push(assistantMsg)
    } else {
      throw new Error('模型返回格式异常')
    }
  } catch (error) {
    let errorMsg = '抱歉，请求失败，请检查：'
    if (error.code === 'ECONNREFUSED') {
      errorMsg += '1. 隧道是否正常运行 2. 后端端口是否映射到本地8000'
    } else if (error.response) {
      errorMsg += `后端返回错误：${error.response.status} - ${JSON.stringify(error.response.data)}`
    } else if (error.message) {
      errorMsg += error.message
    } else {
      errorMsg += '未知错误'
    }

    console.error('聊天请求失败：', error)
    messages.value.push({ role: 'assistant', content: errorMsg })
  } finally {
    isLoading.value = false
    await scrollToBottom() // AI回复后滚动到底部
  }
}

// 优化后的滚动到底部方法 (使用 nextTick 确保 DOM 更新后再滚动)
const scrollToBottom = async () => {
  await nextTick()
  if (chatHistoryRef.value) {
    chatHistoryRef.value.scrollTo({
      top: chatHistoryRef.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}
</script>

<style scoped>
/* ========== 军事科技主题变量 ========== */
:root {
  --bg-deep: #0a0e17;
  --bg-panel: #111827;
  --bg-panel-hover: #1e293b;
  --primary: #00f0ff;
  --primary-dim: rgba(0, 240, 255, 0.12);
  --success: #00ff41;
  --warning: #ff9900;
  --danger: #ff3366;
  --info: #7c3aed;
  --text-main: #e2e8f0;
  --text-dim: #94a3b8;
  --border-glow: 0 0 12px rgba(0, 240, 255, 0.4);
  --transition: all 0.25s ease;
}

/* ========== 全局背景与居中容器 ========== */
.chat-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background:
    linear-gradient(145deg, rgba(10, 14, 23, 0.98), rgba(7, 10, 18, 1)),
    radial-gradient(circle at 30% 70%, rgba(124, 58, 237, 0.08), transparent 45%),
    radial-gradient(circle at 70% 30%, rgba(0, 240, 255, 0.05), transparent 45%);
  padding: 20px;
  box-sizing: border-box;
  font-family: 'Segoe UI', system-ui, sans-serif;
  color: var(--text-main);
}

/* ========== 聊天窗口主体卡片 ========== */
.chat-window {
  width: 95%;
  max-width: 1400px;
  height: 90vh;
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.98), rgba(11, 16, 29, 0.99));
  border: 1px solid rgba(0, 240, 255, 0.25);
  border-radius: 6px;
  box-shadow: var(--border-glow), 0 20px 60px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(10px);
  position: relative;
}

.chat-window::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  animation: scanline 3s linear infinite;
  opacity: 0.7;
}

@keyframes scanline {
  0% { transform: translateX(-100%); opacity: 0; }
  10% { opacity: 0.8; }
  90% { opacity: 0.8; }
  100% { transform: translateX(100%); opacity: 0; }
}

/* ========== 顶部标题栏 ========== */
.chat-header {
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.12), rgba(124, 58, 237, 0.08));
  border-bottom: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 10;
}

.header-avatar {
  font-size: 26px;
  background: rgba(0, 240, 255, 0.15);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 2px solid var(--primary);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
  animation: pulse-avatar 3s infinite;
}

@keyframes pulse-avatar {
  0%, 100% { box-shadow: 0 0 15px rgba(0, 240, 255, 0.4); }
  50% { box-shadow: 0 0 25px rgba(0, 240, 255, 0.7); }
}

.chat-title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--primary);
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}

.chat-status {
  font-size: 11px;
  color: var(--success);
  opacity: 1;
  display: block;
  margin-top: 3px;
  font-family: 'Fira Code', monospace;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.chat-status::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--success);
  border-radius: 50%;
  margin-right: 6px;
  animation: blink 2s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ========== 聊天记录区域 ========== */
.chat-history {
  flex: 1;
  padding: 20px 24px;
  background: rgba(10, 14, 23, 0.6);
  overflow-y: auto;
  scroll-behavior: smooth;
  position: relative;
}

/* 深色滚动条 */
.chat-history::-webkit-scrollbar {
  width: 6px;
}
.chat-history::-webkit-scrollbar-track {
  background: rgba(10, 14, 23, 0.5);
}
.chat-history::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--primary), #7c3aed);
  border-radius: 3px;
  border: 1px solid rgba(0, 240, 255, 0.3);
}
.chat-history::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
}

/* 消息列表容器 */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 消息外层 Wrapper */
.message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 75%;
  animation: msg-slide-in 0.3s ease-out;
}

@keyframes msg-slide-in {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 用户和 AI 的布局区分 */
.is-ai {
  align-self: flex-start;
}
.is-user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

/* 头像样式 */
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  border: 2px solid;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.is-ai .avatar {
  background: rgba(0, 240, 255, 0.12);
  border-color: var(--primary);
  color: var(--primary);
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
}

.is-user .avatar {
  background: rgba(124, 58, 237, 0.15);
  border-color: #a78bfa;
  color: #a78bfa;
  box-shadow: 0 0 12px rgba(124, 58, 237, 0.3);
}

/* 气泡通用样式 */
.message-bubble {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 1px solid;
  font-family: 'Fira Code', 'Consolas', monospace;
}

/* AI 气泡 - 深色背景 + 青色边框 */
.is-ai .message-bubble {
  background: rgba(17, 24, 39, 0.9) !important;
  color: var(--text-main) !important;
  border-color: rgba(0, 240, 255, 0.3) !important;
  border-top-left-radius: 3px;
}

.is-ai .message-bubble:hover {
  border-color: var(--primary) !important;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.2) !important;
}

/* 用户气泡 - 深色背景 + 紫色边框 */
.is-user .message-bubble {
  background: rgba(30, 27, 45, 0.95) !important;
  color: var(--text-main) !important;
  border-color: rgba(124, 58, 237, 0.4) !important;
  border-top-right-radius: 3px;
}

.is-user .message-bubble:hover {
  border-color: #a78bfa !important;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.2) !important;
}

/* ========== 空状态提示 ========== */
.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-dim);
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: wave 2s infinite;
  transform-origin: 70% 70%;
  filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.4));
}

@keyframes wave {
  0% { transform: rotate(0deg); }
  10% { transform: rotate(14deg); }
  20% { transform: rotate(-8deg); }
  30% { transform: rotate(14deg); }
  40% { transform: rotate(-4deg); }
  50% { transform: rotate(10deg); }
  60% { transform: rotate(0deg); }
  100% { transform: rotate(0deg); }
}

.empty-tip p {
  color: var(--text-dim);
  font-size: 14px;
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.5px;
}

/* ========== 输入框区域 ========== */
.input-area {
  padding: 14px 24px 20px;
  background: rgba(11, 16, 29, 0.95);
  border-top: 1px solid rgba(0, 240, 255, 0.2);
}

.input-box {
  display: flex;
  align-items: center;
  background: rgba(17, 24, 39, 0.9);
  border-radius: 6px;
  padding: 4px 4px 4px 18px;
  border: 1px solid rgba(0, 240, 255, 0.3);
  transition: var(--transition);
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
}

.input-box:focus-within {
  border-color: var(--primary) !important;
  background: rgba(17, 24, 39, 0.95);
  box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.2), inset 0 0 15px rgba(0, 240, 255, 0.1);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: var(--text-main) !important;
  padding: 10px 0;
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.3px;
}

.chat-input::placeholder {
  color: var(--text-dim);
  opacity: 0.7;
}

.chat-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  width: 38px;
  height: 38px;
  border-radius: 4px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(17, 24, 39, 0.8);
  color: var(--text-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: not-allowed;
  transition: var(--transition);
  flex-shrink: 0;
}

.send-btn svg {
  width: 18px;
  height: 18px;
  margin-left: -1px;
  transition: var(--transition);
}

/* 发送按钮激活状态 */
.send-btn.is-active {
  border-color: var(--primary);
  background: rgba(0, 240, 255, 0.15);
  color: var(--primary);
  cursor: pointer;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
}

.send-btn.is-active:hover {
  background: var(--primary);
  color: #0a0e17;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.6);
  transform: translateY(-1px);
}

.send-btn.is-active:hover svg {
  transform: translateX(2px);
}

.send-btn.is-active:active {
  transform: scale(0.98);
}

.send-btn:disabled svg {
  opacity: 0.4;
}

/* ========== 动画部分 ========== */

/* 消息出现过渡动画 */
.msg-fade-enter-active,
.msg-fade-leave-active {
  transition: all 0.35s ease;
}
.msg-fade-enter-from {
  opacity: 0;
  transform: translateY(15px);
}
.msg-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 打字机等待动画 - 适配深色 */
.typing-bubble {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 18px !important;
  background: rgba(17, 24, 39, 0.9) !important;
  border-color: rgba(0, 240, 255, 0.3) !important;
}

.dot {
  width: 5px;
  height: 5px;
  background-color: var(--primary);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; box-shadow: 0 0 12px rgba(0, 240, 255, 0.8); }
}

/* ========== 等宽字体全局适配 ========== */
.message-bubble, .chat-input, .chat-status, .empty-tip p {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
}

/* ========== 响应式适配 ========== */
@media (max-width: 768px) {
  .chat-window {
    width: 100%;
    height: 100vh;
    border-radius: 0;
    border: none;
  }

  .message-wrapper {
    max-width: 90%;
  }

  .chat-header {
    padding: 14px 18px;
  }

  .chat-history {
    padding: 16px 18px;
  }

  .input-area {
    padding: 12px 18px 16px;
  }
}
</style>
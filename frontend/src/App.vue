<template>
  <div id="app">
    <!-- ========== 左侧战术装饰面板 ========== -->
    <aside class="side-panel left-panel" aria-hidden="true">
      <div class="panel-content">
        <div class="panel-title">SYS STATUS</div>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-label">CPU</span>
            <div class="status-bar"><div class="status-fill" style="width: 68%"></div></div>
            <span class="status-value">68%</span>
          </div>
          <div class="circular-progress">
            <svg width="60" height="60">
              <circle class="bg" cx="30" cy="30" r="25"></circle>
              <circle class="progress" cx="30" cy="30" r="25"></circle>
            </svg>
          </div>
          <div class="status-item">
            <span class="status-label">MEM</span>
            <div class="status-bar"><div class="status-fill" style="width: 42%"></div></div>
            <span class="status-value">42%</span>
          </div>
          <div class="status-item">
            <span class="status-label">NET</span>
            <div class="status-bar"><div class="status-fill" style="width: 91%"></div></div>
            <span class="status-value">91%</span>
          </div>
        </div>
        <div class="time-display">{{ currentTime }}</div>
        <div class="signal-indicator">
          <span class="signal-dot"></span>
          <span class="signal-dot"></span>
          <span class="signal-dot"></span>
          <span class="signal-dot"></span>
          <span class="signal-text">SIGNAL: STRONG</span>
        </div>
      </div>
    </aside>

<!--    &lt;!&ndash; ========== 右侧战术装饰面板 ========== &ndash;&gt;-->
<!--    <aside class="side-panel right-panel" aria-hidden="true">-->
<!--      <div class="panel-content">-->
<!--        <div class="panel-title">DATA STREAM</div>-->
<!--        <div class="data-flow">-->
<!--          <div class="flow-line" v-for="i in 6" :key="i" :style="{ animationDelay: `${i * 0.3}s` }"></div>-->
<!--        </div>-->
<!--        <div class="data-labels">-->
<!--          <div class="data-label">-->
<!--            <span class="data-label-name">NODES</span>-->
<!--            <span class="data-label-value">247</span>-->
<!--          </div>-->
<!--          <div class="data-label">-->
<!--            <span class="data-label-name">EDGES</span>-->
<!--            <span class="data-label-value">1,834</span>-->
<!--          </div>-->
<!--          <div class="data-label">-->
<!--            <span class="data-label-name">QUERIES</span>-->
<!--            <span class="data-label-value">52/s</span>-->
<!--          </div>-->
<!--        </div>-->
<!--        <div class="coord-display">-->
<!--          <div class="coord-row"><span>LAT:</span><span class="coord-value">34.7821°N</span></div>-->
<!--          <div class="coord-row"><span>LNG:</span><span class="coord-value">113.6254°E</span></div>-->
<!--          <div class="coord-row"><span>ALT:</span><span class="coord-value">0028m</span></div>-->
<!--        </div>-->
<!--        <div class="radar-scan">-->
<!--          <div class="radar-ring"></div>-->
<!--          <div class="radar-ring"></div>-->
<!--          <div class="radar-ring"></div>-->
<!--          <div class="radar-dot"></div>-->
<!--        </div>-->
<!--      </div>-->
<!--    </aside>-->

    <nav class="navbar">
        <!-- 流光装饰线 -->
      <div class="nav-glow-line"></div>

      <!-- 流动光点 -->
      <div class="nav-light-particles"></div>

      <!-- 网格背景 -->
      <div class="nav-grid"></div>

      <!-- 脉冲光晕 -->
      <div class="nav-pulse"></div>

      <div class="nav-brand">
        <h1>🌐 多源情报扫描平台</h1>
        <span class="nav-subtitle">多源情报数据源扫描与管理系统</span>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">网站列表</router-link>
<!--        <router-link to="/entity-recognition" class="nav-link">实体识别展示</router-link>-->
        <router-link to="/visual" class="nav-link">可视化</router-link>
        <router-link to="/chat" class="nav-link">智能聊天</router-link>
        <router-link to="/test" class="nav-link">文档状态</router-link>
        <router-link to="/about" class="nav-link">关于</router-link>
<!--        <a href="https://icy-dogs-arrive.loca.lt/" target="_blank" class="nav-link">test</a>-->

<!--        # 1. 文档管理（默认首页）-->
<!--http://localhost:9621/webui/#/documents-->

<!--# 2. 知识图谱可视化-->
<!--http://localhost:9621/webui/#/knowledge-graph-->

<!--# 3. 检索测试 / 问答-->
<!--http://localhost:9621/webui/#/retrieval-->
      </div>
    </nav>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="footer">
      <p>© 2026 多源情报扫描平台 | 后端API: http://localhost:5000</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      currentTime: ''
    }
  },
  mounted() {
    this.updateTime()
    this.timer = setInterval(() => {
      this.updateTime()
    }, 1000)
  },
  beforeUnmount() {
    // 清理定时器，避免内存泄漏
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.currentTime = now.toLocaleTimeString('en-GB', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
    }
  }
}
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('hideHeader') === 'true') {
  // 动态给 body 加个 class 隐藏 header
  document.documentElement.classList.add('hide-my-header');
}
</script>

<style>
/* ========== 全局重置 & 基础变量 ========== */
:root {
  --bg-deep: #0a0e17;
  --bg-panel: #111827;
  --bg-panel-hover: #1e293b;
  --primary: #00f0ff;
  --primary-dim: rgba(0, 240, 255, 0.15);
  --secondary: #7c3aed;
  --warning: #ff9900;
  --danger: #ff3366;
  --text-main: #37daf4;
  --text-dim: #94a3b8;
  --border-glow: 0 0 10px rgba(0, 240, 255, 0.5);
  --transition: all 0.25s ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background-color: var(--bg-deep);
  color: var(--text-main);
  line-height: 1.6;
  /* 军事网格背景 + 扫描线效果 */
  background-image:
    linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px),
    radial-gradient(ellipse at top, rgba(124, 58, 237, 0.08), transparent 70%);
  background-size: 40px 40px, 40px 40px, 100% 100%;
  background-attachment: fixed;
}

/* 等宽字体用于数据/终端感 */
code, .mono, .nav-subtitle, .footer p {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ========== 导航栏 - 战术终端风格 ========== */
.navbar {
  background: linear-gradient(135deg, rgba(10, 14, 23, 0.95) 0%, rgba(18, 24, 39, 0.95) 100%);
  border-bottom: 1px solid var(--primary);
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.4);
  padding: 12px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  backdrop-filter: blur(10px);
  /* 切角装饰 */
  clip-path: polygon(0 0, 100% 0, 100% 85%, 98% 100%, 0 100%);
}

.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  animation: scanline 3s linear infinite;
}

@keyframes scanline {
  0% { transform: translateY(-100%); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(1000%); opacity: 0; }
}

.nav-brand h1 {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: var(--primary);
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.6);
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-subtitle {
  font-size: 12px;
  color: var(--text-dim);
  letter-spacing: 1px;
  text-transform: uppercase;
  opacity: 0.85;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  color: var(--text-main);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 2px;
  position: relative;
  transition: var(--transition);
  letter-spacing: 0.3px;
  /* 切角按钮效果 */
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
}

.nav-link::before {
  content: '';
  position: absolute;
  inset: 0;
  border: 1px solid transparent;
  border-radius: 2px;
  transition: var(--transition);
  pointer-events: none;
}

.nav-link:hover {
  color: var(--primary);
  background: var(--primary-dim);
  border-color: rgba(0, 240, 255, 0.4);
  text-shadow: 0 0 6px rgba(0, 240, 255, 0.5);
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  color: var(--bg-deep);
  background: var(--primary);
  font-weight: 600;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.7);
}

.nav-link.router-link-active::before {
  border-color: var(--primary);
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  /* 内容区面板感 */
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.6), rgba(11, 16, 29, 0.8));
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 4px;
  margin-top: 16px;
  margin-bottom: 16px;
  box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.3);
  position: relative;
}

.main-content::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  opacity: 0.6;
}

/* ========== 页脚 - 状态栏风格 ========== */
.footer {
  background: rgba(10, 14, 23, 0.9);
  padding: 12px 20px;
  text-align: center;
  border-top: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--text-dim);
  font-size: 12px;
  margin-top: auto;
  backdrop-filter: blur(5px);
  position: relative;
}

.footer::before {
  content: '● SYSTEM ONLINE';
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #00ff41;
  font-size: 10px;
  letter-spacing: 2px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.footer p {
  letter-spacing: 0.5px;
}

.footer a {
  color: var(--primary);
  text-decoration: none;
  transition: var(--transition);
}

.footer a:hover {
  text-shadow: 0 0 8px var(--primary);
}

/* ========== 滚动条定制 ========== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-deep);
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--secondary), var(--primary));
  border-radius: 4px;
  border: 2px solid var(--bg-deep);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
}

/* ========== 响应式适配 ========== */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 16px;
    padding: 16px 20px;
    clip-path: none;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .nav-brand h1 {
    font-size: 20px;
  }

  .main-content {
    padding: 16px;
    margin: 12px;
  }
}
/* ========== 两侧战术装饰面板 - 优化版 ========== */
.side-panel {
  position: fixed;
  top: 105px;
  bottom: 70px;
  width: 80px;  /* 增加默认宽度 */
  background: linear-gradient(180deg, rgba(11, 16, 29, 0.9), rgba(17, 24, 39, 0.95));
  border: 1px solid rgba(0, 240, 255, 0.25);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  z-index: 5;
  backdrop-filter: blur(8px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.15);
}

.side-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  animation: scanline 3s linear infinite;
}

.side-panel:hover {
  width: 240px;  /* 展开更宽 */
  border-color: var(--primary);
  box-shadow: 0 0 30px rgba(0, 240, 255, 0.4), inset 0 0 20px rgba(0, 240, 255, 0.1);
}

.left-panel {
  left: 20px;
  border-right: none;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.right-panel {
  right: 20px;
  border-left: none;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.panel-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  opacity: 0.85;
  transition: opacity 0.3s;
  height: 100%;
  overflow-y: auto;
}

.side-panel:hover .panel-content {
  opacity: 1;
}

.panel-title {
  font-size: 12px;  /* 增大标题 */
  color: var(--primary);
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  text-align: center;
  padding: 10px 0;
  border-bottom: 2px solid rgba(0, 240, 255, 0.4);
  font-family: 'Fira Code', monospace;
  white-space: nowrap;
  background: rgba(0, 240, 255, 0.08);
  border-radius: 4px;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* ========== 左侧面板增强 ========== */

/* 系统状态网格 */
.status-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  font-family: 'Fira Code', monospace;
  white-space: nowrap;
  padding: 8px;
  background: rgba(0, 240, 255, 0.05);
  border-radius: 4px;
  border: 1px solid rgba(0, 240, 255, 0.15);
  transition: all 0.3s;
}

.status-item:hover {
  background: rgba(0, 240, 255, 0.1);
  border-color: rgba(0, 240, 255, 0.3);
  transform: translateX(4px);
}

.status-label {
  color: var(--primary);
  width: 35px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.status-bar {
  flex: 1;
  height: 6px;  /* 增加进度条高度 */
  background: rgba(0, 240, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.status-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 3px;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
  transition: width 0.5s ease;
  position: relative;
  overflow: hidden;
}

.status-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.status-value {
  color: var(--text-main);
  width: 35px;
  text-align: right;
  font-weight: 600;
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}

/* 时间显示增强 */
.time-display {
  font-size: 18px;  /* 大幅增大 */
  color: var(--primary);
  text-align: center;
  font-family: 'Fira Code', monospace;
  font-weight: 700;
  padding: 14px 10px;
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(124, 58, 237, 0.15));
  border-radius: 6px;
  border: 2px solid rgba(0, 240, 255, 0.5);
  white-space: nowrap;
  text-shadow: 0 0 15px rgba(0, 240, 255, 0.8), 0 0 30px rgba(0, 240, 255, 0.4);
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.4), inset 0 0 15px rgba(0, 240, 255, 0.2);
  letter-spacing: 2px;
  margin: 8px 0;
  position: relative;
  overflow: hidden;
}

.time-display::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  animation: time-sweep 3s infinite;
}

@keyframes time-sweep {
  0% { left: -100%; }
  100% { left: 100%; }
}

.side-panel:hover .time-display {
  font-size: 22px;  /* 悬停时更大 */
  padding: 16px 12px;
}

/* 信号指示器增强 */
.signal-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
  padding: 10px;
  background: rgba(0, 255, 65, 0.08);
  border-radius: 4px;
  border: 1px solid rgba(0, 255, 65, 0.3);
}

.signal-dot {
  width: 5px;
  height: 16px;
  background: var(--success);
  border-radius: 2px;
  animation: signal-pulse 1.5s infinite ease-in-out;
  box-shadow: 0 0 10px var(--success);
}

.signal-dot:nth-child(2) { animation-delay: 0.2s; height: 20px; }
.signal-dot:nth-child(3) { animation-delay: 0.4s; height: 24px; }
.signal-dot:nth-child(4) { animation-delay: 0.6s; height: 28px; }

@keyframes signal-pulse {
  0%, 100% { opacity: 1; transform: scaleY(1); }
  50% { opacity: 0.6; transform: scaleY(0.9); }
}

.signal-text {
  font-size: 11px;
  color: var(--success);
  font-family: 'Fira Code', monospace;
  white-space: nowrap;
  font-weight: 600;
  text-shadow: 0 0 8px rgba(0, 255, 65, 0.4);
}

/* 装饰性进度环 */
.circular-progress {
  width: 60px;
  height: 60px;
  margin: 10px auto;
  position: relative;
}

.circular-progress svg {
  transform: rotate(-90deg);
}

.circular-progress circle {
  fill: none;
  stroke-width: 4;
}

.circular-progress .bg {
  stroke: rgba(0, 240, 255, 0.1);
}

.circular-progress .progress {
  stroke: var(--primary);
  stroke-linecap: round;
  stroke-dasharray: 157;
  stroke-dashoffset: 47;
  animation: progress-draw 2s ease-out;
  filter: drop-shadow(0 0 8px var(--primary));
}

@keyframes progress-draw {
  from { stroke-dashoffset: 157; }
}

/* ========== 右侧面板增强 ========== */

/* 数据流增强 */
.data-flow {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 0;
  position: relative;
}

.data-flow::before {
  content: '▶';
  position: absolute;
  left: -2px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--primary);
  font-size: 10px;
  animation: blink 1s infinite;
}

.flow-line {
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
  border-radius: 2px;
  animation: flow-slide 2.5s linear infinite;
  opacity: 0.8;
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}

.flow-line:nth-child(2) { animation-delay: 0.5s; }
.flow-line:nth-child(3) { animation-delay: 1s; }
.flow-line:nth-child(4) { animation-delay: 1.5s; }
.flow-line:nth-child(5) { animation-delay: 2s; }
.flow-line:nth-child(6) { animation-delay: 0.8s; }

@keyframes flow-slide {
  0% { transform: translateX(-150%); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateX(400%); opacity: 0; }
}

/* 坐标显示增强 */
.coord-display {
  font-size: 11px;
  font-family: 'Fira Code', monospace;
  color: var(--text-dim);
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(0, 240, 255, 0.05);
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 4px;
}

.coord-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  white-space: nowrap;
  padding: 6px 0;
  border-bottom: 1px dashed rgba(0, 240, 255, 0.15);
}

.coord-row:last-child {
  border-bottom: none;
}

.coord-row span:first-child {
  color: var(--primary);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.coord-value {
  color: var(--text-main);
  font-weight: 600;
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

/* 雷达扫描增强 */
.radar-scan {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 10px auto;
  background: radial-gradient(circle, rgba(0, 240, 255, 0.1), transparent 70%);
  border-radius: 50%;
  border: 2px solid rgba(0, 240, 255, 0.3);
  overflow: hidden;
}

.radar-ring {
  position: absolute;
  border: 1px solid rgba(0, 240, 255, 0.4);
  border-radius: 50%;
  animation: radar-expand 3s linear infinite;
}

.radar-ring:nth-child(1) { width: 100%; height: 100%; animation-delay: 0s; }
.radar-ring:nth-child(2) { width: 66%; height: 66%; top: 17%; left: 17%; animation-delay: 1s; }
.radar-ring:nth-child(3) { width: 33%; height: 33%; top: 33%; left: 33%; animation-delay: 2s; }

@keyframes radar-expand {
  0% { transform: scale(0.3); opacity: 0.8; }
  100% { transform: scale(1); opacity: 0; }
}

.radar-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 15px var(--primary), 0 0 30px var(--primary);
  animation: radar-pulse 2s infinite;
}

@keyframes radar-pulse {
  0%, 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.2); }
}

/* 扫描线效果 */
.radar-scan::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 50%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary));
  transform-origin: left center;
  animation: radar-sweep 3s linear infinite;
  box-shadow: 0 0 10px var(--primary);
}

@keyframes radar-sweep {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 数据标签 */
.data-labels {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 10px;
  font-family: 'Fira Code', monospace;
}

.data-label {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  background: rgba(124, 58, 237, 0.1);
  border-radius: 3px;
  border-left: 3px solid var(--secondary);
}

.data-label-name {
  color: var(--text-dim);
}

.data-label-value {
  color: var(--primary);
  font-weight: 600;
}

/* 滚动条美化 */
.panel-content::-webkit-scrollbar {
  width: 4px;
}

.panel-content::-webkit-scrollbar-track {
  background: transparent;
}

.panel-content::-webkit-scrollbar-thumb {
  background: rgba(0, 240, 255, 0.3);
  border-radius: 2px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
}

/* ========== 响应式调整 ========== */
@media (max-width: 1400px) {
  .side-panel {
    width: 60px;
  }

  .side-panel:hover {
    width: 200px;
  }
}

@media (max-width: 1200px) {
  .side-panel {
    display: none;
  }
}
/* ========== 导航栏中间装饰区域 ========== */
.navbar::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 35%;
  right: 38%;
  height: 2px;
  background: linear-gradient(90deg,
    transparent,
    rgba(0, 240, 255, 0.2),
    rgba(124, 58, 237, 0.3),
    rgba(0, 240, 255, 0.2),
    transparent
  );
  transform: translateY(-50%);
  animation: nav-glow 3s ease-in-out infinite;
  pointer-events: none;
}

/* 流光装饰线 */
.navbar .nav-glow-line {
  position: absolute;
  top: 50%;
  left: 28%;    /* 调整：从 35% 改为 28%，向左延伸 */
  right: 32%;   /* 调整：从 38% 改为 32%，向右延伸 */
  height: 2px;
  background: linear-gradient(90deg,
    transparent,
    var(--primary),
    var(--secondary),
    var(--primary),
    transparent
  );
  transform: translateY(-50%);
  opacity: 0.7;
  box-shadow: 0 0 20px var(--primary), 0 0 40px var(--secondary);
  animation: nav-scanline 4s linear infinite;
  pointer-events: none;
}

/* 流动光点 */
.navbar .nav-light-particles {
  position: absolute;
  top: 50%;
  left: 28%;    /* 与流光线条保持一致 */
  right: 32%;
  height: 3px;
  transform: translateY(-50%);
  overflow: hidden;
  pointer-events: none;
}

/* 网格背景 */
.navbar .nav-grid {
  position: absolute;
  top: 50%;
  left: 28%;    /* 与流光线条保持一致 */
  right: 32%;
  height: 40px;
  transform: translateY(-50%);
  background-image:
    linear-gradient(90deg, rgba(0, 240, 255, 0.1) 1px, transparent 1px),
    linear-gradient(rgba(0, 240, 255, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  opacity: 0.3;
  animation: nav-grid-move 10s linear infinite;
  pointer-events: none;
}

/* 脉冲光晕 */
.navbar .nav-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;   /* 增加宽度，从 200px 改为 300px */
  height: 25px;   /* 增加高度，从 20px 改为 25px */
  background: radial-gradient(ellipse, rgba(0, 240, 255, 0.25), transparent 70%);
  border-radius: 50%;
  animation: nav-pulse-glow 2.5s ease-in-out infinite;
  pointer-events: none;
}

/* 背景光晕（覆盖更大区域） */
.navbar::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 25%;    /* 最宽范围 */
  right: 29%;
  height: 60px;
  background: radial-gradient(ellipse, rgba(0, 240, 255, 0.08), transparent 70%);
  transform: translateY(-50%);
  pointer-events: none;
  filter: blur(20px);
}
</style>
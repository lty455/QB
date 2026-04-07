<template>
  <div class="visual">
    <h1>关于可视化模块</h1>

    <el-card>
      <h2>模块概述</h2>
      <p>这是知识图谱平台的核心展示模块，支持大规模图数据的交互式可视化、分析与探索，兼容百万级节点的高效渲染。</p>

      <h3>核心功能</h3>
      <ul>
        <li>📈 知识图谱交互式渲染</li>
        <li>🔍 节点/关系精准搜索与筛选</li>
        <li>🖱️ 拖拽/缩放/旋转视图操作</li>
        <li>🎨 多主题样式自定义（颜色/大小/形状）</li>
        <li>📤 可视化结果导出（PNG/SVG/JSON）</li>
      </ul>

      <h3>技术栈</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card>
            <h4>可视化核心</h4>
            <p>Vis.js / D3.js</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <h4>前端框架</h4>
            <p>Vue 3 + Element Plus</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <h4>性能优化</h4>
            <p>Web Worker / 分块加载</p>
          </el-card>
        </el-col>
      </el-row>

      <h3>使用说明</h3>
      <ol>
        <li>确保已加载知识图谱数据（点击"加载图谱"按钮）</li>
        <li>使用左侧筛选栏选择要展示的节点/关系类型</li>
        <li>鼠标滚轮缩放视图，拖拽画布移动视角</li>
        <li>点击节点可展开关联关系，右键节点查看详情</li>
        <li>点击右上角"导出"按钮可保存当前可视化结果</li>
      </ol>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'VisualizationView'
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

/* ========== 整体布局 ========== */
.visual {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background:
    linear-gradient(145deg, rgba(10, 14, 23, 0.95), rgba(7, 10, 18, 0.98)),
    radial-gradient(circle at 30% 70%, rgba(124, 58, 237, 0.06), transparent 40%),
    radial-gradient(circle at 70% 30%, rgba(0, 240, 255, 0.04), transparent 40%);
  color: var(--text-main);
  min-height: calc(100vh - 120px);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ========== 标题样式 ========== */
h1 {
  color: var(--primary);
  margin-bottom: 28px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
  position: relative;
  display: inline-block;
}

h1::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  animation: scanline 2.5s linear infinite;
}

@keyframes scanline {
  0% { transform: scaleX(0); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: scaleX(1); opacity: 0; }
}

h2 {
  color: var(--primary);
  margin: 20px 0 15px;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.3px;
  border-left: 3px solid var(--primary);
  padding-left: 12px;
}

h3 {
  color: var(--text-main);
  margin: 25px 0 15px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

h4 {
  color: var(--success);
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
}

/* ========== Element Card 深度定制 ========== */
:deep(.el-card) {
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(11, 16, 29, 0.98)) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.3) !important;
  transition: var(--transition) !important;
  backdrop-filter: blur(8px);
}

:deep(.el-card:hover) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.5), 0 8px 30px rgba(0, 0, 0, 0.4) !important;
  transform: translateY(-2px);
}

:deep(.el-card__body) {
  padding: 18px !important;
}

/* 主卡片特殊处理 */
:deep(.visual > .el-card) {
  border-left: 3px solid var(--primary) !important;
}

/* ========== 段落/列表样式 ========== */
p {
  color: var(--text-dim);
  line-height: 1.7;
  font-size: 14px;
  margin-bottom: 16px;
}

ul, ol {
  margin-left: 20px;
  margin-bottom: 20px;
  color: var(--text-main);
}

li {
  margin-bottom: 10px;
  line-height: 1.6;
  font-size: 14px;
  color: var(--text-dim);
  position: relative;
  padding-left: 4px;
}

ul li::before {
  content: '▹';
  color: var(--primary);
  position: absolute;
  left: -16px;
  font-family: 'Fira Code', monospace;
}

ol {
  counter-reset: item;
  list-style: none;
  margin-left: 0;
}

ol li {
  counter-increment: item;
  padding-left: 24px;
}

ol li::before {
  content: counter(item);
  position: absolute;
  left: 0;
  width: 18px;
  height: 18px;
  background: rgba(0, 240, 255, 0.15);
  border: 1px solid var(--primary);
  border-radius: 3px;
  color: var(--primary);
  font-size: 11px;
  font-weight: 600;
  font-family: 'Fira Code', monospace;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ========== 技术栈卡片网格 ========== */
.el-row {
  margin-bottom: 20px;
}

:deep(.el-col .el-card) {
  border: 1px solid rgba(124, 58, 237, 0.3) !important;
}

:deep(.el-col .el-card h4) {
  color: #a78bfa !important;
  margin-bottom: 8px !important;
  font-size: 13px !important;
}

:deep(.el-col .el-card p) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
  margin: 0 !important;
}

/* ========== 等宽字体适配 ========== */
code, pre, .mono, p, li, h4 + p {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
}

/* ========== 滚动条定制 ========== */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(10, 14, 23, 0.5);
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--primary), #7c3aed);
  border-radius: 3px;
  border: 1px solid rgba(0, 240, 255, 0.3);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
}

/* ========== 响应式适配 ========== */
@media (max-width: 768px) {
  .visual {
    padding: 16px;
  }

  h1 {
    font-size: 20px;
  }

  :deep(.el-col) {
    margin-bottom: 12px;
  }
}
</style>
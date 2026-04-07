<template>
  <div class="entity-recognition-container">
    <!-- 左侧文件加载区域 -->
    <div class="left-panel">
      <div class="panel-title">📁 文件加载</div>

      <!-- 层级状态提示 -->
      <div class="level-indicator">
        当前层级：{{ currentLevel === 1 ? '文件选择层' : '实体扫描层' }}
      </div>

      <!-- 空文件夹提示 -->
      <div v-if="fileList.length === 0 && currentLevel === 1" class="empty-folder-tip">
        📁 未检测到任何 JSON 文件<br/>
        请检查 QingBao/sorted_intelligence 文件夹
      </div>

      <!-- 文件列表/实体列表 -->
      <div v-else class="file-list">
        <div
          v-for="(item, index) in displayList"
          :key="index"
          class="list-item"
          :class="{ active: selectedItem === item }"
          @click="selectItem(item)"
        >
          {{ item }}
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="button-group">
        <button
          class="operate-btn backward-btn"
          @click="handleBackward"
          :disabled="fileList.length === 0 && currentLevel === 1"
        >
          {{ currentLevel === 1 ? '扫描文件' : '扫描实体' }}
        </button>
        <button
          class="operate-btn upward-btn"
          :disabled="currentLevel === 1"
          @click="handleUpward"
        >
          {{ currentLevel === 1 ? '返回（不可用）' : '返回上一层' }}
        </button>
      </div>
    </div>

    <!-- 右侧展示区域 -->
    <div class="right-panel">
      <!-- 实体识别结果展示 -->
      <div class="entity-result-section">
        <div class="section-title">🔍 实体识别结果</div>
        <div class="entity-table-container">
          <table v-if="entityResults.length > 0" class="entity-table">
            <thead>
              <tr>
                <th>实体名</th>
                <th>属性1</th>
                <th>属性2</th>
                <th>属性3</th>
                <th>属性4</th>
                <th>属性5</th>
                <th>属性6</th>
                <th>属性7</th>
                <th>属性8</th>
                <th>属性9</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(entity, index) in entityResults" :key="index">
                <td>{{ entity.name }}</td>
                <td>{{ entity.attr1 || '-' }}</td>
                <td>{{ entity.attr2 || '-' }}</td>
                <td>{{ entity.attr3 || '-' }}</td>
                <td>{{ entity.attr4 || '-' }}</td>
                <td>{{ entity.attr5 || '-' }}</td>
                <td>{{ entity.attr6 || '-' }}</td>
                <td>{{ entity.attr7 || '-' }}</td>
                <td>{{ entity.attr8 || '-' }}</td>
                <td>{{ entity.attr9 || '-' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty-tip">
            <template v-if="fileList.length === 0 && currentLevel === 1">
              未检测到文件，请检查文件夹
            </template>
            <template v-else-if="currentLevel === 1">
              请选择文件并点击"扫描文件"
            </template>
            <template v-else>
              暂无实体识别结果
            </template>
          </div>
        </div>
      </div>

      <!-- 实体关系展示 -->
      <div class="relation-result-section">
        <div class="section-title">🧩 实体关系结果</div>
        <div class="relation-table-container">
          <table v-if="relationResults.length > 0" class="relation-table">
            <thead>
              <tr>
                <th>实体1</th>
                <th>关系</th>
                <th>实体2</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(relation, index) in relationResults" :key="index">
                <td>{{ relation.entity1 }}</td>
                <td>{{ relation.relation }}</td>
                <td>{{ relation.entity2 }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty-tip">
            <template v-if="fileList.length === 0 && currentLevel === 1">
              未检测到文件，请检查文件夹
            </template>
            <template v-else-if="currentLevel === 1">
              请选择文件并点击"扫描文件"
            </template>
            <template v-else>
              暂无实体关系结果
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// ===================== 配置 =====================
const API_BASE_URL = 'http://localhost:5000'

// ===================== 状态管理 =====================
const currentLevel = ref(1)
const fileList = ref([])
const displayList = ref([])
const selectedItem = ref('')
const entityResults = ref([])
const relationResults = ref([])

// ===================== 初始化 =====================
onMounted(async () => {
  await scanFilesFromBackend()
})

// ===================== 核心方法 =====================
const scanFilesFromBackend = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/files`)
    fileList.value = res.data.files || []
    displayList.value = [...fileList.value]
    selectedItem.value = displayList.value[0] || ''
  } catch (err) {
    console.error('扫描文件失败:', err)
    alert('扫描文件失败，请检查后端服务是否启动')
  }
}

const loadFileFromBackend = async (filename) => {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/files/${filename}`)
    return res.data.data
  } catch (err) {
    console.error('加载文件失败:', err)
    alert(`加载文件 ${filename} 失败`)
    return null
  }
}

// ===================== 事件处理 =====================
const selectItem = (item) => {
  selectedItem.value = item
}

const handleBackward = async () => {
  if (currentLevel.value === 1) {
    if (!selectedItem.value) {
      alert('请先选择一个文件！')
      return
    }
    entityResults.value = []
    relationResults.value = []
    const fileData = await loadFileFromBackend(selectedItem.value)
    if (!fileData) return
    const mockEntities = generateMockEntities(fileData)
    const mockRelations = generateMockRelations(mockEntities)
    entityResults.value = mockEntities
    relationResults.value = mockRelations
    displayList.value = mockEntities.map(e => e.name)
    selectedItem.value = displayList.value[0] || ''
    currentLevel.value = 2
  } else {
    alert(`已选中实体：${selectedItem.value}，待实现扫描逻辑`)
  }
}

const handleUpward = () => {
  displayList.value = [...fileList.value]
  selectedItem.value = displayList.value[0] || ''
  currentLevel.value = 1
}

// ===================== 模拟数据 =====================
const generateMockEntities = (fileData) => {
  return fileData.slice(0, 10).map((item, i) => ({
    name: item.file_path || `实体${i+1}`,
    attr1: item.score || '-',
    attr2: '军事/政治',
    attr3: '高优先级',
    attr4: '-',
    attr5: '-',
    attr6: '-',
    attr7: '-',
    attr8: '-',
    attr9: '-'
  }))
}

const generateMockRelations = (entities) => {
  const relations = []
  for (let i = 0; i < Math.min(5, entities.length); i++) {
    relations.push({
      entity1: entities[i].name,
      relation: ['关联', '包含', '对抗', '合作', '从属'][Math.floor(Math.random() * 5)],
      entity2: entities[(i+1)%entities.length].name
    })
  }
  return relations
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
.entity-recognition-container {
  display: flex;
  width: 100%;
  height: 90vh;
  padding: 20px;
  box-sizing: border-box;
  gap: 20px;
  background:
    linear-gradient(145deg, rgba(10, 14, 23, 0.95), rgba(7, 10, 18, 0.98)),
    radial-gradient(circle at 30% 70%, rgba(124, 58, 237, 0.06), transparent 40%),
    radial-gradient(circle at 70% 30%, rgba(0, 240, 255, 0.04), transparent 40%);
  color: var(--text-main);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ========== 左侧面板 ========== */
.left-panel {
  width: 320px;
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(11, 16, 29, 0.98));
  border: 1px solid rgba(0, 240, 255, 0.25);
  border-radius: 4px;
  padding: 18px;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(8px);
  position: relative;
}

.left-panel::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  opacity: 0.7;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 14px;
  color: var(--primary);
  letter-spacing: 0.5px;
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
  display: flex;
  align-items: center;
  gap: 6px;
}

.level-indicator {
  font-size: 12px;
  color: var(--text-dim);
  margin-bottom: 12px;
  padding: 8px 12px;
  background: rgba(0, 240, 255, 0.08);
  border: 1px solid rgba(0, 240, 255, 0.3);
  border-radius: 3px;
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.5px;
}

.empty-folder-tip {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
  color: var(--danger);
  font-size: 13px;
  background: rgba(255, 51, 102, 0.08);
  border: 1px dashed rgba(255, 51, 102, 0.4);
  border-radius: 4px;
  margin-bottom: 16px;
  font-family: 'Fira Code', monospace;
}

.file-list {
  flex: 1;
  overflow-y: auto;
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 4px;
  margin-bottom: 16px;
  background: rgba(10, 14, 23, 0.6);
}

.list-item {
  padding: 11px 14px;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 240, 255, 0.1);
  font-size: 13px;
  color: var(--text-main);
  transition: var(--transition);
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.3px;
}

.list-item:hover {
  background: rgba(0, 240, 255, 0.12);
  color: var(--primary);
  padding-left: 18px;
}

.list-item.active {
  background: rgba(0, 240, 255, 0.2);
  color: var(--primary);
  font-weight: 600;
  border-left: 3px solid var(--primary);
  padding-left: 13px;
  box-shadow: inset 0 0 10px rgba(0, 240, 255, 0.2);
}

.button-group {
  display: flex;
  gap: 10px;
}

.operate-btn {
  flex: 1;
  padding: 11px 0;
  border: 1px solid;
  border-radius: 3px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.5px;
  background: rgba(17, 24, 39, 0.8);
}

.backward-btn {
  border-color: rgba(0, 240, 255, 0.5);
  color: var(--primary);
}

.backward-btn:hover:not(:disabled) {
  background: var(--primary);
  color: #0a0e17;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.6);
  transform: translateY(-1px);
}

.backward-btn:disabled {
  border-color: rgba(148, 163, 184, 0.3);
  color: var(--text-dim);
  cursor: not-allowed;
  opacity: 0.5;
}

.upward-btn {
  border-color: rgba(124, 58, 237, 0.5);
  color: #a78bfa;
}

.upward-btn:hover:not(:disabled) {
  background: #7c3aed;
  color: white;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.6);
  transform: translateY(-1px);
}

.upward-btn:disabled {
  border-color: rgba(148, 163, 184, 0.3);
  color: var(--text-dim);
  cursor: not-allowed;
  opacity: 0.5;
}

/* ========== 右侧面板 ========== */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.entity-result-section, .relation-result-section {
  flex: 1;
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(11, 16, 29, 0.98));
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 4px;
  padding: 18px;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(8px);
  position: relative;
}

.entity-result-section::before,
.relation-result-section::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  opacity: 0.6;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 14px;
  color: var(--primary);
  letter-spacing: 0.3px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.entity-table-container, .relation-table-container {
  flex: 1;
  overflow-y: auto;
  border-radius: 4px;
}

/* ========== 表格 - 深色核心修复 ========== */
.entity-table, .relation-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  background: #0b1120 !important;  /* 🔥 关键：表格整体深色 */
}

.entity-table th, .relation-table th {
  background: rgba(0, 240, 255, 0.15) !important;  /* 🔥 表头深色带青色 */
  padding: 11px 10px;
  text-align: left;
  border: 1px solid rgba(0, 240, 255, 0.25) !important;
  font-weight: 600;
  color: var(--primary) !important;
  font-family: 'Fira Code', monospace;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 11px;
}

.entity-table td, .relation-table td {
  padding: 10px 10px;
  border: 1px solid rgba(0, 240, 255, 0.12) !important;
  background: #0b1120 !important;  /* 🔥 单元格强制深色 */
  color: #e2e8f0 !important;  /* 🔥 文字浅色 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
}

.entity-table tr:hover, .relation-table tr:hover {
  background: rgba(0, 240, 255, 0.12) !important;  /* 🔥 悬停微亮 */
  box-shadow: inset 0 0 0 1px rgba(0, 240, 255, 0.3);
}

/* 斑马纹（如果有） */
.entity-table tr:nth-child(even), .relation-table tr:nth-child(even) {
  background: rgba(11, 16, 29, 0.9) !important;
}

.empty-tip {
  text-align: center;
  color: var(--text-dim);
  font-size: 13px;
  margin-top: 40px;
  font-family: 'Fira Code', monospace;
  padding: 20px;
  background: rgba(17, 24, 39, 0.5);
  border: 1px dashed rgba(0, 240, 255, 0.2);
  border-radius: 4px;
}

/* ========== 滚动条定制 ========== */
.file-list::-webkit-scrollbar,
.entity-table-container::-webkit-scrollbar,
.relation-table-container::-webkit-scrollbar {
  width: 6px;
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
@media (max-width: 1024px) {
  .entity-recognition-container {
    flex-direction: column;
    height: auto;
  }

  .left-panel {
    width: 100%;
    max-height: 300px;
  }

  .right-panel {
    min-height: 400px;
  }
}
</style>
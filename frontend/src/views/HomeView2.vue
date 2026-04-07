<template>
  <div class="home">
    <h1>网站数据源管理系统</h1>
    <p>管理500+个网站数据源，支持自动分类和智能爬取</p>
    
    <!-- 操作按钮区域 -->
    <div class="action-buttons">
      <el-button type="primary" @click="loadWebsites" :loading="loading">
        🔄 刷新数据
      </el-button>
      
      <el-button type="success" @click="startBatchCrawl" :disabled="selectedWebsites.length === 0">
        🕷️ 批量爬取 ({{ selectedWebsites.length }}个)
      </el-button>
      
      <el-button type="warning" @click="showCategoryCrawl = true">
        📂 按分类爬取
      </el-button>
      
      <el-button type="info" @click="showUpload = true">
        📤 上传网站列表
      </el-button>
      
      <el-input
        v-model="searchText"
        placeholder="搜索网站..."
        clearable
        style="width: 300px; margin-left: auto;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>
    
    <!-- 数据统计 -->
    <div v-if="stats.total > 0" class="stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-icon total">🌐</div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.total }}</div>
                <div class="stat-label">总网站数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-icon completed">✅</div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.by_status['已完成'] || 0 }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-icon crawling">🕷️</div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.by_status['抓取中'] || 0 }}</div>
                <div class="stat-label">抓取中</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-icon pending">⏳</div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.by_status['待抓取'] || 0 }}</div>
                <div class="stat-label">待抓取</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 分类统计 -->
    <div v-if="Object.keys(stats.by_category || {}).length > 0" class="category-stats">
      <el-card>
        <template #header>
          <span>📊 分类分布</span>
        </template>
        <div class="category-tags">
          <el-tag 
            v-for="(count, category) in stats.by_category" 
            :key="category"
            :type="getCategoryTagType(category)"
            size="large"
            class="category-tag"
            @click="filterByCategory(category)"
          >
            {{ category }} ({{ count }})
          </el-tag>
        </div>
      </el-card>
    </div>
 <!-- 爬虫状态卡片 -->
 <!-- 爬虫状态卡片 -->
  <el-card v-if="crawlStats" class="crawl-status-card">
    <template #header>
      <div class="status-header">
        <span>📊 爬虫统计 (持久化)</span>
        <el-button 
          type="text" 
          @click="loadCrawlStatus"
          :loading="loadingCrawlStatus"
          size="small"
        >
          🔄 刷新
        </el-button>
      </div>
    </template>
    
    <div class="crawl-stats">
      <div class="crawl-stat-item">
        <div class="crawl-stat-label">总网站数</div>
        <div class="crawl-stat-value">{{ crawlStats.total_websites }}</div>
      </div>
      
      <div class="crawl-stat-item">
        <div class="crawl-stat-label">待抓取</div>
        <div class="crawl-stat-value" style="color: #909399;">
          {{ crawlStats.pending }}
        </div>
      </div>
      
      <div class="crawl-stat-item">
        <div class="crawl-stat-label">抓取中</div>
        <div class="crawl-stat-value" style="color: #E6A23C;">
          {{ crawlStats.processing }}
        </div>
      </div>
      
      <div class="crawl-stat-item">
        <div class="crawl-stat-label">已完成</div>
        <div class="crawl-stat-value" style="color: #67C23A;">
          {{ crawlStats.completed }}
        </div>
      </div>
      
      <div class="crawl-stat-item">
        <div class="crawl-stat-label">失败</div>
        <div class="crawl-stat-value" style="color: #F56C6C;">
          {{ crawlStats.failed }}
        </div>
      </div>
    </div>
    
    <!-- 进度条 -->
    <div class="progress-section">
      <div class="progress-label">
        完成率: {{ crawlStats.completion_rate }}%
      </div>
      <el-progress 
        :percentage="crawlStats.completion_rate" 
        :color="getProgressColor(crawlStats.completion_rate)"
        :show-text="false"
      />
    </div>
    
    <!-- 队列状态 -->
    <div class="queue-status">
      <el-tag type="info">队列任务: {{ crawlStatus?.queue_size || 0 }}</el-tag>
      <el-tag type="success">活跃线程: {{ crawlStatus?.active_workers || 0 }}/{{ crawlStatus?.total_workers || 0 }}</el-tag>
    </div>
  </el-card>
  
    <!-- 网站列表 -->
    <div v-if="websites.length > 0" class="website-list">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>📋 网站列表 ({{ filteredWebsites.length }} 个)</span>
            <div class="header-actions">
              <el-select 
                v-model="selectedCategory" 
                placeholder="按分类筛选" 
                clearable
                style="width: 150px; margin-right: 10px;"
              >
                <el-option
                  v-for="category in uniqueCategories"
                  :key="category"
                  :label="category"
                  :value="category"
                />
              </el-select>
              
              <el-select 
                v-model="selectedStatus" 
                placeholder="按状态筛选" 
                clearable
                style="width: 150px;"
              >
                <el-option label="待抓取" value="待抓取" />
                <el-option label="抓取中" value="抓取中" />
                <el-option label="已完成" value="已完成" />
                <el-option label="失败" value="失败" />
              </el-select>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedWebsites" 
          style="width: 100%"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column prop="id" label="ID" width="80" align="center" />
          
          <el-table-column prop="url" label="网址" min-width="200">
            <template #default="{ row }">
              <div class="website-url">
                <a :href="row.url" target="_blank" class="url-link">
                  {{ row.url }}
                </a>
                <div class="domain">{{ extractDomain(row.url) }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="category" label="分类" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getCategoryTagType(row.category)" size="small">
                {{ row.category }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="last_crawl" label="最后抓取" width="180">
            <template #default="{ row }">
              {{ formatDate(row.last_crawl) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button 
                size="small" 
                type="primary" 
                @click="viewWebsite(row)"
                :disabled="row.status === '抓取中'"
              >
                查看
              </el-button>
              
              <el-button 
                size="small" 
                type="success"
                @click="crawlWebsite(row)"
                :loading="row.status === '抓取中'"
                :disabled="row.status === '抓取中'"
              >
                {{ row.status === '抓取中' ? '爬取中...' : '爬取' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="filteredWebsites.length"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
    
    <!-- 无数据提示 -->
    <div v-else-if="!loading" class="empty-state">
      <el-empty description="暂无网站数据">
        <el-button type="primary" @click="loadWebsites">
          加载数据
        </el-button>
      </el-empty>
    </div>
    
    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUpload"
      title="上传网站列表文件"
      width="500px"
    >
      <div class="upload-instructions">
        <p><strong>文件格式：</strong></p>
        <pre>网址 | 分类（可选）</pre>
        <p><strong>示例：</strong></p>
        <pre>https://news.sina.com.cn | 新闻
https://www.csdn.net | 技术
https://github.com</pre>
        <p><em>如果不指定分类，系统会根据域名自动猜测</em></p>
      </div>
      
      <el-upload
        class="upload-demo"
        drag
        :action="uploadUrl"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            仅支持 .txt 文件，每行一个网站
          </div>
        </template>
      </el-upload>
    </el-dialog>
    
    <!-- 按分类爬取对话框 -->
    <el-dialog
      v-model="showCategoryCrawl"
      title="按分类批量爬取"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="选择分类">
          <el-select v-model="selectedCrawlCategory" placeholder="请选择分类">
            <el-option
              v-for="category in uniqueCategories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="网站状态">
          <el-checkbox-group v-model="selectedCrawlStatus">
            <el-checkbox label="待抓取" />
            <el-checkbox label="失败" />
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="预计数量">
          <el-tag type="info">
            {{ getCategoryCrawlCount() }} 个网站
          </el-tag>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCategoryCrawl = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="startCategoryCrawl"
            :disabled="!selectedCrawlCategory"
          >
            开始爬取
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  UploadFilled
} from '@element-plus/icons-vue'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://localhost:5000/api'

// 数据响应式变量
const websites = ref([])
const loading = ref(false)
const searchText = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const selectedWebsites = ref([])



const crawlStatus = ref(null)
const crawlStats = ref(null)
const loadingCrawlStatus = ref(false)

// 对话框控制
const showUpload = ref(false)
const showCategoryCrawl = ref(false)
const selectedCrawlCategory = ref('')
const selectedCrawlStatus = ref(['待抓取', '失败'])

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 统计信息
const stats = ref({
  total: 0,
  by_category: {},
  by_status: {}
})

// 工具函数
const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67C23A'
  if (percentage >= 50) return '#E6A23C'
  return '#F56C6C'
}

// 加载爬虫状态
const loadCrawlStatus = async () => {
  loadingCrawlStatus.value = true
  try {
    // 加载爬虫统计（持久化数据）
    const response = await axios.get(`${API_BASE}/crawl/status`)
    if (response.data.success) {
      crawlStatus.value = response.data.data
      crawlStats.value = response.data.data.crawl_statistics
      
      console.log('📊 爬虫统计:', crawlStats.value)
    }
  } catch (error) {
    console.error('加载爬虫状态失败:', error)
  } finally {
    loadingCrawlStatus.value = false
  }
}


// 计算属性
const uniqueCategories = computed(() => {
  return [...new Set(websites.value.map(w => w.category))].sort()
})

const filteredWebsites = computed(() => {
  let filtered = websites.value
  
  // 搜索过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(w => 
      w.url.toLowerCase().includes(search)
    )
  }
  
  // 分类过滤
  if (selectedCategory.value) {
    filtered = filtered.filter(w => w.category === selectedCategory.value)
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(w => w.status === selectedStatus.value)
  }
  
  return filtered
})

const paginatedWebsites = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredWebsites.value.slice(start, end)
})

// 上传URL
const uploadUrl = computed(() => `${API_BASE}/websites/upload`)

// 加载数据
const loadWebsites = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/websites`)
    if (response.data.success) {
      websites.value = response.data.data.websites
      stats.value = response.data.data.stats
      
      // 自动选中所有"待抓取"的网站
      selectedWebsites.value = websites.value.filter(w => w.status === '待抓取')
      
      ElMessage.success(`成功加载 ${response.data.data.pagination.total} 个网站`)
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('无法连接到后端服务')
  } finally {
    loading.value = false
  }
    // 加载爬虫状态
  loadCrawlStatus()
}

// 查看网站
const viewWebsite = (website) => {
  window.open(website.url, '_blank')
}

// 爬取单个网站
const crawlWebsite = async (website) => {
  try {
    const response = await axios.post(`${API_BASE}/websites/${website.id}/crawl`)
    if (response.data.success) {
      ElMessage.success('已开始爬取，请稍后查看结果')
      
      // 等待2秒后刷新数据
      setTimeout(() => {
        loadWebsites()
      }, 2000)
    }
  } catch (error) {
    console.error('开始爬取失败:', error)
    ElMessage.error('爬取失败')
  }
    setTimeout(() => {
    loadCrawlStatus()
    loadWebsites()
  }, 3000)
}

// 批量爬取
const startBatchCrawl = async () => {
  if (selectedWebsites.value.length === 0) {
    ElMessage.warning('请先选择要爬取的网站')
    return
  }
  
  try {
    const websiteIds = selectedWebsites.value.map(w => w.id)
    const response = await axios.post(`${API_BASE}/websites/batch/crawl`, {
      website_ids: websiteIds
    })
    
    if (response.data.success) {
      ElMessage.success(`已开始批量爬取 ${response.data.count} 个网站`)
      
      // 等待2秒后刷新数据
      setTimeout(() => {
        loadWebsites()
      }, 2000)
    }
  } catch (error) {
    console.error('批量爬取失败:', error)
    ElMessage.error('批量爬取失败')
  }
}

// 按分类爬取
const getCategoryCrawlCount = () => {
  if (!selectedCrawlCategory.value) return 0
  
  return websites.value.filter(w => {
    const categoryMatch = w.category === selectedCrawlCategory.value
    const statusMatch = selectedCrawlStatus.value.includes(w.status)
    return categoryMatch && statusMatch
  }).length
}

const startCategoryCrawl = async () => {
  const count = getCategoryCrawlCount()
  if (count === 0) {
    ElMessage.warning('该分类下没有符合条件的网站')
    return
  }
  
  try {
    const response = await axios.post(`${API_BASE}/websites/batch/crawl`, {
      category: selectedCrawlCategory.value
    })
    
    if (response.data.success) {
      ElMessage.success(`已开始爬取 ${response.data.count} 个网站`)
      showCategoryCrawl.value = false
      
      // 等待2秒后刷新数据
      setTimeout(() => {
        loadWebsites()
      }, 2000)
    }
  } catch (error) {
    console.error('按分类爬取失败:', error)
    ElMessage.error('爬取失败')
  }
}

// 文件上传处理
const beforeUpload = (file) => {
  const isTxt = file.type === 'text/plain' || file.name.endsWith('.txt')
  if (!isTxt) {
    ElMessage.error('只能上传txt文件')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  if (response.data.success) {
    ElMessage.success(response.data.message)
    showUpload.value = false
    loadWebsites()
  } else {
    ElMessage.error(response.data.error || '上传失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败')
}

// 工具函数
const extractDomain = (url) => {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '从未抓取'
  
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getCategoryTagType = (category) => {
  const types = {
    '新闻': 'danger',
    '技术': 'primary',
    '社区': 'success',
    '视频': 'warning',
    '搜索': 'info'
  }
  return types[category] || 'info'
}

const getStatusTagType = (status) => {
  const types = {
    '待抓取': 'info',
    '抓取中': 'warning',
    '已完成': 'success',
    '失败': 'danger'
  }
  return types[status] || 'info'
}

const filterByCategory = (category) => {
  selectedCategory.value = category
}

// 事件处理
const handleSelectionChange = (selection) => {
  selectedWebsites.value = selection
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 监听筛选条件变化
watch([selectedCategory, selectedStatus], () => {
  currentPage.value = 1
})

// 组件挂载时加载数据
onMounted(() => {
  loadWebsites()
  loadCrawlStatus()
})
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
  --text-main: #37daf4;
  --text-dim: #94a3b8;
  --border-glow: 0 0 12px rgba(0, 240, 255, 0.4);
  --transition: all 0.25s ease;
}

/* ========== 基础排版 ========== */
.home {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background:
    linear-gradient(145deg, rgba(17, 24, 39, 0.5), rgba(10, 14, 23, 0.7)),
    radial-gradient(circle at 20% 80%, rgba(124, 58, 237, 0.08), transparent 40%),
    radial-gradient(circle at 80% 20%, rgba(0, 240, 255, 0.06), transparent 40%);
  border-radius: 6px;
  min-height: calc(100vh - 120px);
  color: var(--text-main);
}

h1 {
  color: var(--primary);
  margin-bottom: 8px;
  font-size: 26px;
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

h1 + p {
  color: var(--text-dim);
  margin-bottom: 28px;
  font-size: 14px;
  letter-spacing: 1px;
  font-family: 'Fira Code', 'Consolas', monospace;
  text-transform: uppercase;
}

/* ========== 操作按钮区域 ========== */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
  align-items: center;
  flex-wrap: wrap;
  padding: 16px;
  background: rgba(17, 24, 39, 0.8);
  border: 1px solid rgba(0, 240, 255, 0.25);
  border-radius: 4px;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3);
  position: relative;
}

.action-buttons::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  opacity: 0.7;
}

:deep(.action-buttons .el-button) {
  border-radius: 3px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 10px 18px !important;
  border-width: 1px !important;
  transition: var(--transition) !important;
}

:deep(.action-buttons .el-button--primary) {
  background: rgba(0, 240, 255, 0.15) !important;
  border-color: rgba(0, 240, 255, 0.5) !important;
  color: var(--primary) !important;
}

:deep(.action-buttons .el-button--primary:hover) {
  background: var(--primary) !important;
  color: #0a0e17 !important;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
  transform: translateY(-1px);
}

:deep(.action-buttons .el-button--success) {
  background: rgba(0, 255, 65, 0.15) !important;
  border-color: rgba(0, 255, 65, 0.5) !important;
  color: #00ff41 !important;
}

:deep(.action-buttons .el-button--success:hover) {
  background: #00ff41 !important;
  color: #0a0e17 !important;
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.6) !important;
  transform: translateY(-1px);
}

:deep(.action-buttons .el-button--warning) {
  background: rgba(255, 153, 0, 0.15) !important;
  border-color: rgba(255, 153, 0, 0.5) !important;
  color: #ff9900 !important;
}

:deep(.action-buttons .el-button--warning:hover) {
  background: #ff9900 !important;
  color: #0a0e17 !important;
  box-shadow: 0 0 15px rgba(255, 153, 0, 0.6) !important;
  transform: translateY(-1px);
}

:deep(.action-buttons .el-button--info) {
  background: rgba(124, 58, 237, 0.15) !important;
  border-color: rgba(124, 58, 237, 0.5) !important;
  color: #a78bfa !important;
}

:deep(.action-buttons .el-button--info:hover) {
  background: #7c3aed !important;
  color: white !important;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.6) !important;
  transform: translateY(-1px);
}

:deep(.action-buttons .el-button:disabled) {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  box-shadow: none !important;
  transform: none !important;
}

/* 搜索框 */
:deep(.action-buttons .el-input__wrapper) {
  background: rgba(17, 24, 39, 0.9) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  box-shadow: none !important;
  border-radius: 3px !important;
}

:deep(.action-buttons .el-input__wrapper.is-focus) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.2) !important;
}

:deep(.action-buttons .el-input__inner) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
}

:deep(.action-buttons .el-input__prefix) {
  color: var(--text-dim) !important;
}

/* ========== 统计卡片 ========== */
.stats {
  margin-bottom: 28px;
}

:deep(.stats .el-card) {
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(11, 16, 29, 0.95)) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.3) !important;
  transition: var(--transition) !important;
  backdrop-filter: blur(8px);
}

:deep(.stats .el-card:hover) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.6), 0 8px 30px rgba(0, 0, 0, 0.4) !important;
  transform: translateY(-2px);
}

:deep(.stats .el-card__body) {
  padding: 0 !important;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 18px 20px;
}

.stat-icon {
  font-size: 28px;
  margin-right: 14px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.stat-icon::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.15), transparent 60%);
  pointer-events: none;
}

.stat-icon.total {
  background: linear-gradient(135deg, #00f0ff 0%, #7c3aed 100%);
  color: #0a0e17;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #00ff41 0%, #00c48c 100%);
  color: #0a0e17;
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
}

.stat-icon.crawling {
  background: linear-gradient(135deg, #ff9900 0%, #ff6b35 100%);
  color: #0a0e17;
  box-shadow: 0 0 15px rgba(255, 153, 0, 0.4);
  animation: pulse-warning 2s infinite;
}

@keyframes pulse-warning {
  0%, 100% { box-shadow: 0 0 15px rgba(255, 153, 0, 0.4); }
  50% { box-shadow: 0 0 25px rgba(255, 153, 0, 0.7); }
}

.stat-icon.pending {
  background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%);
  color: white;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.4);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
  font-family: 'Fira Code', monospace;
  letter-spacing: -0.5px;
}

.stat-label {
  color: var(--text-dim);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

/* ========== 分类统计 ========== */
.category-stats {
  margin-bottom: 28px;
}

:deep(.category-stats .el-card) {
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(11, 16, 29, 0.95)) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

:deep(.category-stats .el-card__header) {
  background: rgba(0, 240, 255, 0.08) !important;
  border-bottom: 1px solid rgba(0, 240, 255, 0.3) !important;
  padding: 14px 20px !important;
}

:deep(.category-stats .el-card__header span) {
  color: var(--primary);
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.3px;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 16px 20px 20px;
}

:deep(.category-tag.el-tag) {
  background: rgba(17, 24, 39, 0.8) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  color: var(--text-main) !important;
  padding: 8px 16px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  transition: var(--transition) !important;
  cursor: pointer !important;
  border-radius: 3px !important;
}

:deep(.category-tag.el-tag:hover) {
  background: var(--primary-dim) !important;
  border-color: var(--primary) !important;
  color: var(--primary) !important;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.4) !important;
  transform: translateY(-1px);
}

:deep(.category-tag.el-tag--danger) { border-color: rgba(255, 51, 102, 0.5) !important; }
:deep(.category-tag.el-tag--primary) { border-color: rgba(0, 240, 255, 0.5) !important; }
:deep(.category-tag.el-tag--success) { border-color: rgba(0, 255, 65, 0.5) !important; }
:deep(.category-tag.el-tag--warning) { border-color: rgba(255, 153, 0, 0.5) !important; }
:deep(.category-tag.el-tag--info) { border-color: rgba(124, 58, 237, 0.5) !important; }

/* ========== 爬虫状态卡片 ========== */
.crawl-status-card {
  margin-bottom: 28px;
}

:deep(.crawl-status-card .el-card) {
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(11, 16, 29, 0.95)) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

:deep(.crawl-status-card .el-card__header) {
  background: rgba(0, 240, 255, 0.06) !important;
  border-bottom: 1px solid rgba(0, 240, 255, 0.25) !important;
  padding: 14px 20px !important;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.crawl-status-card .el-card__header span) {
  color: var(--primary);
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.3px;
}

:deep(.crawl-status-card .el-button--text) {
  color: var(--text-dim) !important;
  font-size: 13px !important;
}

:deep(.crawl-status-card .el-button--text:hover) {
  color: var(--primary) !important;
}

.crawl-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding: 20px;
  background: rgba(10, 14, 23, 0.4);
  border-radius: 4px;
  border: 1px solid rgba(0, 240, 255, 0.15);
}

.crawl-stat-item {
  text-align: center;
  flex: 1;
  padding: 8px 0;
  border-right: 1px dashed rgba(0, 240, 255, 0.2);
}

.crawl-stat-item:last-child {
  border-right: none;
}

.crawl-stat-label {
  color: var(--text-dim);
  font-size: 12px;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 500;
}

.crawl-stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  font-family: 'Fira Code', monospace;
}

.progress-section {
  padding: 0 20px 20px;
}

.progress-label {
  color: var(--text-dim);
  font-size: 13px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  font-family: 'Fira Code', monospace;
}

:deep(.progress-section .el-progress-bar__outer) {
  background: rgba(17, 24, 39, 0.8) !important;
  border-radius: 3px !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  overflow: hidden;
}

:deep(.progress-section .el-progress-bar__inner) {
  background: linear-gradient(90deg, var(--primary), #7c3aed) !important;
  border-radius: 3px !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.5) !important;
  position: relative;
}

:deep(.progress-section .el-progress-bar__inner::after) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.queue-status {
  padding: 0 20px 20px;
  display: flex;
  gap: 12px;
}

:deep(.queue-status .el-tag) {
  background: rgba(17, 24, 39, 0.9) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 12px !important;
  padding: 4px 12px !important;
  border-radius: 3px !important;
}

:deep(.queue-status .el-tag--success) {
  border-color: rgba(0, 255, 65, 0.4) !important;
  color: #00ff41 !important;
}

/* ========== 表格区域 ========== */
.website-list {
  margin-bottom: 20px;
}

:deep(.website-list .el-card) {
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(11, 16, 29, 0.95)) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

:deep(.website-list .el-card__header) {
  background: rgba(0, 240, 255, 0.05) !important;
  border-bottom: 1px solid rgba(0, 240, 255, 0.2) !important;
  padding: 14px 20px !important;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.table-header span {
  color: var(--primary);
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.3px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

:deep(.header-actions .el-select .el-input__wrapper) {
  background: rgba(17, 24, 39, 0.9) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  box-shadow: none !important;
  border-radius: 3px !important;
}

:deep(.header-actions .el-select .el-input__inner) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
}

:deep(.header-actions .el-select-dropdown) {
  background: rgba(17, 24, 39, 0.98) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
}

:deep(.header-actions .el-select-dropdown__item) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
}

:deep(.header-actions .el-select-dropdown__item.selected) {
  color: var(--primary) !important;
  background: rgba(0, 240, 255, 0.1) !important;
}

:deep(.header-actions .el-select-dropdown__item.hover) {
  background: rgba(0, 240, 255, 0.15) !important;
}

/* ========== Element Table 深度定制 ========== */
/* ========== 强制深色表格背景 ========== */
:deep(.el-table) {
  background: #0b1120 !important;  /* 深色背景 */
}

:deep(.el-table::before) {
  background-color: rgba(0, 240, 255, 0.2) !important;
}

:deep(.el-table__header-wrapper th) {
  background-color: rgba(0, 240, 255, 0.2) !important;
  color: #00f0ff !important;
}

:deep(.el-table__body tr) {
  background: #0b1120 !important;  /* 行背景深色 */
}


:deep(.el-table__body tr:hover) {
  background-color: rgba(0, 240, 255, 0.15) !important;
}

:deep(.el-table__body td) {
  background: transparent !important;
  color: #82b4f8 !important;  /* 文字浅色 */
}
:deep(.el-table__header th) {
  background: #1e293b !important;  /* 表头深色 */
  color: #00f0ff !important;
}
/* 斑马纹（如果有） */
:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: rgba(17, 24, 39, 0.7) !important;
}

/* 网址列样式 */
.website-url {
  line-height: 1.5;
  padding: 4px 0;
}

.url-link {
  color: var(--primary) !important;
  text-decoration: none !important;
  font-weight: 500 !important;
  word-break: break-all !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
  transition: var(--transition) !important;
  position: relative;
}

.url-link::after {
  content: '↗';
  margin-left: 4px;
  opacity: 0;
  transition: var(--transition);
  font-size: 11px;
}

.url-link:hover {
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.6) !important;
}

.url-link:hover::after {
  opacity: 1;
}

.domain {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 3px;
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.3px;
}

/* 状态标签 */
:deep(.el-table .el-tag) {
  border-radius: 3px !important;
  font-weight: 500 !important;
  font-size: 11px !important;
  padding: 4px 10px !important;
  border-width: 1px !important;
}

:deep(.el-table .el-tag--success) {
  background: rgba(0, 255, 65, 0.12) !important;
  border-color: rgba(0, 255, 65, 0.4) !important;
  color: #00ff41 !important;
}

:deep(.el-table .el-tag--warning) {
  background: rgba(255, 153, 0, 0.12) !important;
  border-color: rgba(255, 153, 0, 0.4) !important;
  color: #ff9900 !important;
  animation: pulse-warning 2s infinite;
}

:deep(.el-table .el-tag--danger) {
  background: rgba(255, 51, 102, 0.12) !important;
  border-color: rgba(255, 51, 102, 0.4) !important;
  color: #ff3366 !important;
}

:deep(.el-table .el-tag--info) {
  background: rgba(124, 58, 237, 0.12) !important;
  border-color: rgba(124, 58, 237, 0.4) !important;
  color: #a78bfa !important;
}

:deep(.el-table .el-tag--primary) {
  background: rgba(0, 240, 255, 0.12) !important;
  border-color: rgba(0, 240, 255, 0.4) !important;
  color: var(--primary) !important;
}

/* 操作按钮组 */
:deep(.el-table .el-button-group .el-button) {
  border-radius: 3px !important;
  font-size: 12px !important;
  padding: 6px 12px !important;
  font-weight: 500 !important;
  margin: 0 2px !important;
}

:deep(.el-table .el-button--primary) {
  background: rgba(0, 240, 255, 0.15) !important;
  border-color: rgba(0, 240, 255, 0.4) !important;
  color: var(--primary) !important;
}

:deep(.el-table .el-button--primary:hover) {
  background: var(--primary) !important;
  color: #0a0e17 !important;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.5) !important;
}

:deep(.el-table .el-button--success) {
  background: rgba(0, 255, 65, 0.15) !important;
  border-color: rgba(0, 255, 65, 0.4) !important;
  color: #00ff41 !important;
}

:deep(.el-table .el-button--success:hover) {
  background: #00ff41 !important;
  color: #0a0e17 !important;
  box-shadow: 0 0 12px rgba(0, 255, 65, 0.5) !important;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 240, 255, 0.15);
}

:deep(.pagination .el-pagination) {
  --el-pagination-button-color: var(--text-dim) !important;
  --el-pagination-hover-color: var(--primary) !important;
  --el-pagination-button-bg-color: rgba(17, 24, 39, 0.8) !important;
}

:deep(.pagination .el-pagination button:hover) {
  color: var(--primary) !important;
  background: rgba(0, 240, 255, 0.1) !important;
}

:deep(.pagination .el-pagination .el-pager li) {
  background: rgba(17, 24, 39, 0.8) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
}

:deep(.pagination .el-pagination .el-pager li.active) {
  background: var(--primary) !important;
  color: #0a0e17 !important;
  border-color: var(--primary) !important;
  font-weight: 600 !important;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.5) !important;
}

:deep(.pagination .el-pagination .el-select .el-input__inner) {
  background: rgba(17, 24, 39, 0.8) !important;
  border-color: rgba(0, 240, 255, 0.3) !important;
  color: var(--text-main) !important;
}

/* ========== 空状态 ========== */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

:deep(.empty-state .el-empty) {
  --el-empty-fill-color-0: rgba(0, 240, 255, 0.1) !important;
  --el-empty-fill-color-1: rgba(0, 240, 255, 0.15) !important;
  --el-empty-fill-color-2: rgba(0, 240, 255, 0.2) !important;
  --el-empty-fill-color-3: rgba(0, 240, 255, 0.1) !important;
  --el-empty-fill-color-4: rgba(0, 240, 255, 0.05) !important;
  --el-empty-fill-color-5: rgba(0, 240, 255, 0.02) !important;
  --el-empty-fill-color-6: rgba(0, 240, 255, 0.01) !important;
  --el-empty-fill-color-7: rgba(0, 240, 255, 0.005) !important;
  --el-empty-fill-color-8: rgba(0, 240, 255, 0.002) !important;
  --el-empty-fill-color-9: rgba(0, 240, 255, 0.001) !important;
}

:deep(.empty-state .el-empty__description) {
  color: var(--text-dim) !important;
  font-family: 'Fira Code', monospace !important;
}

:deep(.empty-state .el-button--primary) {
  background: linear-gradient(135deg, var(--primary), #7c3aed) !important;
  border: none !important;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.4) !important;
}

:deep(.empty-state .el-button--primary:hover) {
  box-shadow: 0 0 25px rgba(0, 240, 255, 0.7) !important;
}

/* ========== 上传对话框 ========== */
:deep(.el-dialog) {
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.98), rgba(10, 14, 23, 0.98)) !important;
  border: 2px solid var(--primary) !important;
  border-radius: 6px !important;
  box-shadow: 0 0 40px rgba(0, 240, 255, 0.3), 0 20px 60px rgba(0, 0, 0, 0.5) !important;
}

:deep(.el-dialog__title) {
  color: var(--primary) !important;
  font-weight: 600 !important;
  font-family: 'Fira Code', monospace !important;
  letter-spacing: 0.5px !important;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: var(--text-dim) !important;
}

:deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: var(--danger) !important;
}

:deep(.el-dialog__body) {
  padding: 20px 24px !important;
  color: var(--text-main) !important;
}

.upload-instructions {
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(10, 14, 23, 0.5);
  border-radius: 4px;
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-left: 3px solid var(--primary);
}

.upload-instructions p {
  color: var(--text-dim);
  font-size: 13px;
  margin: 8px 0;
}

.upload-instructions strong {
  color: var(--primary);
  font-weight: 600;
}

.upload-instructions pre {
  margin: 10px 0;
  padding: 12px;
  background: rgba(17, 24, 39, 0.8);
  border-radius: 4px;
  border: 1px solid rgba(0, 240, 255, 0.2);
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  color: var(--text-main);
  white-space: pre-wrap;
  word-break: break-all;
}

.upload-instructions em {
  color: var(--warning);
  font-style: normal;
}

:deep(.upload-demo .el-upload-dragger) {
  background: rgba(17, 24, 39, 0.6) !important;
  border: 2px dashed rgba(0, 240, 255, 0.4) !important;
  border-radius: 6px !important;
  transition: var(--transition) !important;
}

:deep(.upload-demo .el-upload-dragger:hover) {
  border-color: var(--primary) !important;
  background: rgba(0, 240, 255, 0.05) !important;
}

:deep(.upload-demo .el-upload-dragger.is-dragover) {
  border-color: var(--success) !important;
  background: rgba(0, 255, 65, 0.1) !important;
}

:deep(.upload-demo .el-icon--upload) {
  color: var(--primary) !important;
  font-size: 48px !important;
}

:deep(.upload-demo .el-upload__text) {
  color: var(--text-main) !important;
  font-size: 14px !important;
}

:deep(.upload-demo .el-upload__text em) {
  color: var(--primary) !important;
  font-style: normal !important;
}

:deep(.upload-demo .el-upload__tip) {
  color: var(--text-dim) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 12px !important;
}

/* ========== 按分类爬取对话框 ========== */
:deep(.el-dialog .el-form-item__label) {
  color: var(--text-dim) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
}

:deep(.el-dialog .el-form-item__content) {
  color: var(--text-main) !important;
}

:deep(.el-dialog .el-select .el-input__wrapper) {
  background: rgba(17, 24, 39, 0.8) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  box-shadow: none !important;
}

:deep(.el-dialog .el-select .el-input__inner) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
}

:deep(.el-dialog .el-checkbox__input.is-checked + .el-checkbox__label) {
  color: var(--primary) !important;
}

:deep(.el-dialog .el-checkbox__inner) {
  background: rgba(17, 24, 39, 0.8) !important;
  border-color: rgba(0, 240, 255, 0.4) !important;
}

:deep(.el-dialog .el-checkbox__input.is-checked .el-checkbox__inner) {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
}

:deep(.el-dialog .el-tag) {
  background: rgba(0, 240, 255, 0.1) !important;
  border-color: rgba(0, 240, 255, 0.4) !important;
  color: var(--primary) !important;
  font-family: 'Fira Code', monospace !important;
}

:deep(.el-dialog .dialog-footer) {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 240, 255, 0.15);
}

:deep(.el-dialog .el-button--primary) {
  background: linear-gradient(135deg, var(--primary), #7c3aed) !important;
  border: none !important;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.4) !important;
}

:deep(.el-dialog .el-button--primary:hover) {
  box-shadow: 0 0 25px rgba(0, 240, 255, 0.7) !important;
  transform: translateY(-1px);
}

/* ========== 加载状态 ========== */
:deep(.el-loading-mask) {
  background: rgba(10, 14, 23, 0.85) !important;
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner .path) {
  stroke: var(--primary) !important;
}

:deep(.el-loading-text) {
  color: var(--primary) !important;
  font-family: 'Fira Code', monospace !important;
  font-weight: 500 !important;
  margin-top: 12px !important;
}

/* ========== 响应式适配 ========== */
@media (max-width: 768px) {
  .home {
    padding: 12px;
  }

  .action-buttons {
    padding: 12px;
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons .el-input {
    width: 100% !important;
    margin-left: 0 !important;
    margin-top: 12px;
  }

  .crawl-stats {
    flex-wrap: wrap;
    gap: 16px;
  }

  .crawl-stat-item {
    flex: 0 0 calc(50% - 12px);
    border-right: none !important;
    border-bottom: 1px dashed rgba(0, 240, 255, 0.2);
    padding-bottom: 12px;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
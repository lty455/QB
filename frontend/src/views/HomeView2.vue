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
.home {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  color: #303133;
  margin-bottom: 10px;
  font-size: 28px;
}

h1 + p {
  color: #606266;
  margin-bottom: 30px;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  align-items: center;
}

.stats {
  margin-bottom: 30px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 15px;
}

.stat-icon {
  font-size: 32px;
  margin-right: 15px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.completed {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-icon.crawling {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
}

.stat-icon.pending {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.category-stats {
  margin-bottom: 30px;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.category-tag {
  cursor: pointer;
  transition: transform 0.3s;
}

.category-tag:hover {
  transform: scale(1.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.website-url {
  line-height: 1.4;
}

.url-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 500;
  word-break: break-all;
}

.url-link:hover {
  text-decoration: underline;
}

.domain {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.upload-instructions {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409EFF;
}

.upload-instructions pre {
  margin: 10px 0;
  padding: 10px;
  background-color: #e9ecef;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.upload-instructions p {
  margin: 5px 0;
}

.upload-instructions em {
  color: #f56c6c;
  font-style: normal;
}










.crawl-status-card {
  margin-bottom: 30px;
}

.crawl-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.crawl-stat-item {
  text-align: center;
  flex: 1;
}

.crawl-stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}

.crawl-stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.crawled-data {
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.crawled-data h4 {
  margin-bottom: 10px;
  color: #303133;
}

.data-stats {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.domain-list {
  max-height: 200px;
  overflow-y: auto;
}

.domain-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.domain-item:last-child {
  border-bottom: none;
}

.more-domains {
  text-align: center;
  padding: 10px;
  color: #909399;
  font-size: 14px;
}
</style>
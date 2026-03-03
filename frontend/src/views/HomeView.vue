<template>
  <div class="home">
    <h1>网站数据源管理系统</h1>
    <p>管理500+个网站数据源，支持自动分类和智能爬取</p>

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
    <el-card v-if="crawlStatusData" class="crawl-status-card">
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
          <div class="crawl-stat-value">{{ crawlStatusData.statistics.total_websites }}</div>
        </div>

        <div class="crawl-stat-item">
          <div class="crawl-stat-label">待抓取</div>
          <div class="crawl-stat-value" style="color: #909399;">
            {{ crawlStatusData.statistics.pending }}
          </div>
        </div>

        <div class="crawl-stat-item">
          <div class="crawl-stat-label">抓取中</div>
          <div class="crawl-stat-value" style="color: #E6A23C;">
            {{ crawlStatusData.statistics.processing }}
          </div>
        </div>

        <div class="crawl-stat-item">
          <div class="crawl-stat-label">已完成</div>
          <div class="crawl-stat-value" style="color: #67C23A;">
            {{ crawlStatusData.statistics.completed }}
          </div>
        </div>

        <div class="crawl-stat-item">
          <div class="crawl-stat-label">失败</div>
          <div class="crawl-stat-value" style="color: #F56C6C;">
            {{ crawlStatusData.statistics.failed }}
          </div>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-label">
          完成率: {{ crawlStatusData.statistics.completion_rate }}%
        </div>
        <el-progress
          :percentage="crawlStatusData.statistics.completion_rate"
          :color="getProgressColor(crawlStatusData.statistics.completion_rate)"
          :show-text="false"
        />
      </div>

      <!-- 队列状态 -->
      <div class="queue-status">
        <el-tag type="info">队列任务: {{ crawlStatusData.queue_size || 0 }}</el-tag>
        <el-tag type="success">活跃线程: {{ crawlStatusData.active_workers || 0 }}/{{ crawlStatusData.total_workers || 0 }}</el-tag>
      </div>
    </el-card>

    <!-- 爬虫参数预设选择 -->
    <div class="crawl-presets" v-if="showCrawlPresets">
      <el-card>
        <template #header>
          <span>⚙️ 爬取参数预设</span>
        </template>

        <div class="preset-options">
          <el-radio-group v-model="selectedPreset" @change="applyPreset">
            <el-radio-button label="quick">快速爬取</el-radio-button>
            <el-radio-button label="standard">标准爬取</el-radio-button>
            <el-radio-button label="deep">深度爬取</el-radio-button>
            <el-radio-button label="comprehensive">全面爬取</el-radio-button>
          </el-radio-group>

          <el-button
            type="text"
            @click="showAdvancedParams = !showAdvancedParams"
            style="margin-left: 20px;"
          >
            {{ showAdvancedParams ? '隐藏' : '显示' }}高级参数
          </el-button>
        </div>

        <!-- 当前参数显示 -->
        <div class="current-params" v-if="crawlParams">
          <el-descriptions :column="4" size="small" border>
            <el-descriptions-item label="最大页面数">
              <el-tag size="small">{{ crawlParams.max_pages }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="爬取深度">
              <el-tag size="small">{{ crawlParams.max_depth }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="延迟">
              <el-tag size="small">{{ crawlParams.delay }} 秒</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="超时时间">
              <el-tag size="small">{{ crawlParams.timeout }} 秒</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 高级参数配置 -->
        <div v-if="showAdvancedParams" class="advanced-params">
          <el-form :model="crawlParams" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="最大页面数">
                  <el-slider
                    v-model="crawlParams.max_pages"
                    :min="1"
                    :max="100"
                    :step="1"
                    show-input
                  />
                </el-form-item>

                <el-form-item label="爬取深度">
                  <el-slider
                    v-model="crawlParams.max_depth"
                    :min="1"
                    :max="5"
                    :step="1"
                    show-input
                  />
                  <div class="param-help">深度1：只爬取首页<br>深度2：爬取首页链接的页面</div>
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="延迟（秒）">
                  <el-slider
                    v-model="crawlParams.delay"
                    :min="0.1"
                    :max="5"
                    :step="0.1"
                    show-input
                  />
                  <div class="param-help">爬取每个页面的间隔时间，避免被封</div>
                </el-form-item>

                <el-form-item label="超时时间（秒）">
                  <el-slider
                    v-model="crawlParams.timeout"
                    :min="10"
                    :max="300"
                    :step="10"
                    show-input
                  />
                  <div class="param-help">单个页面爬取的最大时间</div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="递归爬取">
              <el-switch
                v-model="crawlParams.recursive"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
          </el-form>
        </div>

        <template #footer>
          <div class="preset-footer">
            <el-button @click="showCrawlPresets = false">取消</el-button>
            <el-button type="primary" @click="applyCrawlParams">
              应用参数
            </el-button>
          </div>
        </template>
      </el-card>
    </div>

    <!-- 操作按钮区域 -->
    <div class="action-buttons">
      <el-button type="primary" @click="loadWebsites" :loading="loading">
        🔄 刷新数据
      </el-button>

      <el-button type="success" @click="startRecursiveCrawl" :disabled="selectedWebsites.length === 0">
        🌐 递归爬取 ({{ selectedWebsites.length }}个)
      </el-button>

      <el-button type="warning" @click="showCrawlPresets = true">
        ⚙️ 设置爬取参数
      </el-button>

      <el-button type="info" @click="showTaskStatus = true">
        📊 查看任务状态
      </el-button>

      <!-- 搜索框 -->
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

    <!-- 网站列表表格 -->
    <div v-if="websites.length > 0" class="website-list">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>📋 网站列表 ({{ filteredWebsites.length }} 个)</span>
            <div class="header-info">
              <el-tag type="info" size="small">
                当前参数: {{ crawlParams.max_pages }}页/{{ crawlParams.max_depth }}层
              </el-tag>
            </div>
          </div>
        </template>

        <el-table
          :data="paginatedWebsites"
          style="width: 100%"
          @selection-change="handleSelectionChange"
          v-loading="loading"
        >
          <el-table-column type="selection" width="55" />

          <el-table-column prop="id" label="ID" width="80" align="center" />

          <el-table-column prop="url" label="网址" min-width="250">
            <template #default="{ row }">
              <div class="website-url">
                <a :href="row.url" target="_blank" class="url-link">
                  {{ row.url }}
                </a>
                <div class="domain">{{ row.domain }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="category" label="分类" width="100" align="center">
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

          <el-table-column prop="total_pages" label="已爬页面" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.status === '已完成'">{{ row.total_pages || 0 }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>

          <el-table-column prop="last_crawl" label="最后抓取" width="180">
            <template #default="{ row }">
              {{ formatDate(row.last_crawl) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="250" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  size="small"
                  type="primary"
                  @click="viewWebsite(row)"
                >
                  查看
                </el-button>

                <el-button
                  size="small"
                  type="success"
                  @click="recursiveCrawlWebsite(row)"
                  :loading="isWebsiteCrawling(row.id)"
                  :disabled="isWebsiteCrawling(row.id)"
                >
                  {{ isWebsiteCrawling(row.id) ? '爬取中...' : '递归爬取' }}
                </el-button>

                <el-button
                  size="small"
                  type="info"
                  @click="checkCrawlStatus(row)"
                >
                  状态
                </el-button>
              </el-button-group>
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
          />
        </div>
      </el-card>
    </div>

    <!-- 任务状态对话框 -->
    <el-dialog
      v-model="showTaskStatus"
      title="📊 爬虫任务状态"
      width="800px"
    >
      <div v-if="crawlStatusData">
        <!-- 全局状态 -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="队列中的任务">
            <el-tag :type="crawlStatusData.queue_size > 0 ? 'warning' : 'success'">
              {{ crawlStatusData.queue_size }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="活跃爬虫线程">
            <el-tag type="info">
              {{ crawlStatusData.active_workers }} / {{ crawlStatusData.total_workers }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="正在运行的任务">
            <el-tag :type="crawlStatusData.active_tasks > 0 ? 'primary' : 'info'">
              {{ crawlStatusData.active_tasks }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计信息 -->
        <el-divider>统计信息</el-divider>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="总网站数">
            {{ crawlStatusData.statistics.total_websites }}
          </el-descriptions-item>

          <el-descriptions-item label="总页面数">
            {{ crawlStatusData.statistics.total_pages }}
          </el-descriptions-item>

          <el-descriptions-item label="完成率">
            <el-progress
              :percentage="crawlStatusData.statistics.completion_rate"
              :status="crawlStatusData.statistics.completion_rate >= 80 ? 'success' :
                      crawlStatusData.statistics.completion_rate >= 50 ? 'warning' : 'exception'"
              style="width: 100px; display: inline-block; margin-left: 10px;"
            />
          </el-descriptions-item>
        </el-descriptions>

        <!-- 状态分布 -->
        <el-divider>状态分布</el-divider>
        <div class="status-distribution">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="已完成" :value="crawlStatusData.statistics.completed">
                <template #prefix>
                  <el-icon style="color: #67C23A;"><Check /></el-icon>
                </template>
              </el-statistic>
            </el-col>

            <el-col :span="6">
              <el-statistic title="待抓取" :value="crawlStatusData.statistics.pending">
                <template #prefix>
                  <el-icon style="color: #909399;"><Clock /></el-icon>
                </template>
              </el-statistic>
            </el-col>

            <el-col :span="6">
              <el-statistic title="抓取中" :value="crawlStatusData.statistics.processing">
                <template #prefix>
                  <el-icon style="color: #E6A23C;"><Loading /></el-icon>
                </template>
              </el-statistic>
            </el-col>

            <el-col :span="6">
              <el-statistic title="失败" :value="crawlStatusData.statistics.failed">
                <template #prefix>
                  <el-icon style="color: #F56C6C;"><CloseBold /></el-icon>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>

        <!-- 正在运行的任务 -->
        <div v-if="activeCrawlTasks.length > 0">
          <el-divider>正在运行的任务</el-divider>
          <el-table :data="activeCrawlTasks" size="small">
            <el-table-column prop="website_id" label="网站ID" width="80" />
            <el-table-column prop="url" label="网址" />
            <el-table-column prop="total_pages" label="已爬页面" width="100">
              <template #default="{ row }">
                {{ row.task_status?.total_pages || 0 }}
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.task_status?.start_time) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="loadCrawlStatus">刷新</el-button>
        <el-button type="primary" @click="showTaskStatus = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Check,
  Clock,
  Loading,
  CloseBold
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

// 爬取参数控制
const showCrawlPresets = ref(false)
const showAdvancedParams = ref(false)
const selectedPreset = ref('standard')
const crawlParams = ref({
  max_pages: 10,
  max_depth: 2,
  delay: 1.0,
  timeout: 60,
  recursive: true
})

// 任务状态
const showTaskStatus = ref(false)
const crawlStatusData = ref(null)
const activeCrawlTasks = ref([])
const websiteCrawlStatus = ref({})

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 统计信息
const stats = ref({
  total: 0,
  by_category: {},
  by_status: {}
})

// 加载状态
const loadingCrawlStatus = ref(false)

// 计算属性
const filteredWebsites = computed(() => {
  let filtered = websites.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(w =>
      w.url.toLowerCase().includes(search) ||
      w.domain.toLowerCase().includes(search)
    )
  }

  if (selectedCategory.value) {
    filtered = filtered.filter(w => w.category === selectedCategory.value)
  }

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

// 检查网站是否在爬取中
const isWebsiteCrawling = (websiteId) => {
  return websiteCrawlStatus.value[websiteId] === 'crawling'
}

// 加载网站数据
const loadWebsites = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/websites`)
    if (response.data.success) {
      websites.value = response.data.data.websites
      stats.value = response.data.data.stats

      // 检查每个网站的爬取状态
      await checkAllWebsiteStatus()

      console.log('✅ 网站数据加载成功')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('无法连接到后端服务')
  } finally {
    loading.value = false
  }
}

// 检查网站爬取状态
const checkWebsiteCrawlStatus = async (websiteId) => {
  try {
    const response = await axios.get(`${API_BASE}/websites/${websiteId}/crawl-status`)
    if (response.data.success) {
      if (response.data.is_running) {
        websiteCrawlStatus.value[websiteId] = 'crawling'
      } else {
        websiteCrawlStatus.value[websiteId] = response.data.status
      }
      return response.data
    }
  } catch (error) {
    console.error('检查爬取状态失败:', error)
  }
  return null
}

// 检查所有网站状态
const checkAllWebsiteStatus = async () => {
  for (const website of websites.value) {
    if (website.status === '抓取中') {
      const status = await checkWebsiteCrawlStatus(website.id)
      if (status && !status.is_running) {
        // 如果后端显示不在运行但前端状态是抓取中，刷新数据
        await loadWebsites()
        break
      }
    }
  }
}

// 加载爬虫状态
const loadCrawlStatus = async () => {
  loadingCrawlStatus.value = true
  try {
    const response = await axios.get(`${API_BASE}/crawl/status`)
    if (response.data.success) {
      crawlStatusData.value = response.data.data

      // 更新活跃任务
      updateActiveCrawlTasks()
    }
  } catch (error) {
    console.error('加载爬虫状态失败:', error)
  } finally {
    loadingCrawlStatus.value = false
  }
}

// 更新活跃爬取任务
const updateActiveCrawlTasks = () => {
  if (!crawlStatusData.value || crawlStatusData.value.active_tasks === 0) {
    activeCrawlTasks.value = []
    return
  }

  // 找出状态为"抓取中"的网站
  activeCrawlTasks.value = websites.value
    .filter(w => w.status === '抓取中')
    .map(w => ({
      website_id: w.id,
      url: w.url,
      status: w.status
    }))
}

// 递归爬取单个网站
const recursiveCrawlWebsite = async (website) => {
  try {
    ElMessageBox.confirm(
      `确定要递归爬取 ${website.url} 吗？\n\n` +
      `爬取参数:\n` +
      `- 最大页面数: ${crawlParams.value.max_pages}\n` +
      `- 爬取深度: ${crawlParams.value.max_depth}\n` +
      `- 延迟: ${crawlParams.value.delay}秒\n` +
      `- 超时: ${crawlParams.value.timeout}秒`,
      '确认递归爬取',
      {
        confirmButtonText: '开始爬取',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      // 标记为爬取中
      websiteCrawlStatus.value[website.id] = 'crawling'

      const response = await axios.post(
        `${API_BASE}/websites/${website.id}/recursive-crawl`,
        {
          params: crawlParams.value
        }
      )

      if (response.data.success) {
        ElMessage.success('已开始递归爬取，请稍后查看结果')

        // 更新网站状态为抓取中
        const index = websites.value.findIndex(w => w.id === website.id)
        if (index !== -1) {
          websites.value[index].status = '抓取中'
        }

        // 5秒后刷新数据
        setTimeout(() => {
          loadWebsites()
          loadCrawlStatus()
        }, 5000)
      }
    }).catch(() => {
      // 用户取消
    })
  } catch (error) {
    console.error('开始递归爬取失败:', error)
    ElMessage.error('爬取失败')
    websiteCrawlStatus.value[website.id] = 'error'
  }
}

// 批量递归爬取
const startRecursiveCrawl = async () => {
  if (selectedWebsites.value.length === 0) {
    ElMessage.warning('请先选择要爬取的网站')
    return
  }

  try {
    const confirmMessage = `确定要批量递归爬取 ${selectedWebsites.value.length} 个网站吗？\n\n` +
      `爬取参数:\n` +
      `- 最大页面数: ${crawlParams.value.max_pages}\n` +
      `- 爬取深度: ${crawlParams.value.max_depth}\n` +
      `- 延迟: ${crawlParams.value.delay}秒\n` +
      `- 超时: ${crawlParams.value.timeout}秒`

    ElMessageBox.confirm(
      confirmMessage,
      '确认批量爬取',
      {
        confirmButtonText: '开始爬取',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      const websiteIds = selectedWebsites.value.map(w => w.id)

      // 标记为爬取中
      selectedWebsites.value.forEach(website => {
        websiteCrawlStatus.value[website.id] = 'crawling'
      })

      const response = await axios.post(
        `${API_BASE}/websites/batch/recursive-crawl`,
        {
          website_ids: websiteIds,
          params: crawlParams.value
        }
      )

      if (response.data.success) {
        ElMessage.success(`已开始批量递归爬取 ${response.data.count} 个网站`)

        // 更新网站状态为抓取中
        selectedWebsites.value.forEach(website => {
          const index = websites.value.findIndex(w => w.id === website.id)
          if (index !== -1) {
            websites.value[index].status = '抓取中'
          }
        })

        // 清空选中
        selectedWebsites.value = []

        // 5秒后刷新数据
        setTimeout(() => {
          loadWebsites()
          loadCrawlStatus()
        }, 5000)
      }
    }).catch(() => {
      // 用户取消
    })
  } catch (error) {
    console.error('批量递归爬取失败:', error)
    ElMessage.error('批量爬取失败')
  }
}

// 加载爬取参数预设
const loadCrawlParamsPresets = async () => {
  try {
    const response = await axios.get(`${API_BASE}/crawl/params/presets`)
    if (response.data.success) {
      // 应用默认参数
      crawlParams.value = { ...response.data.defaults }
    }
  } catch (error) {
    console.error('加载爬取参数预设失败:', error)
  }
}

// 应用参数预设
const applyPreset = async (presetKey) => {
  try {
    const response = await axios.get(`${API_BASE}/crawl/params/presets`)
    if (response.data.success && response.data.presets[presetKey]) {
      const preset = response.data.presets[presetKey]
      crawlParams.value = {
        ...crawlParams.value,
        ...preset
      }
      ElMessage.success(`已应用"${preset.name}"预设`)
    }
  } catch (error) {
    console.error('应用预设失败:', error)
  }
}

// 应用自定义参数
const applyCrawlParams = () => {
  showCrawlPresets.value = false
  ElMessage.success('爬取参数已更新')
}

// 查看网站
const viewWebsite = (website) => {
  window.open(website.url, '_blank')
}

// 检查爬取状态
const checkCrawlStatus = async (website) => {
  const status = await checkWebsiteCrawlStatus(website.id)

  if (status) {
    if (status.is_running) {
      ElMessage.info(`网站 ${website.url} 正在爬取中`)
    } else {
      ElMessage.info(`网站 ${website.url} 状态: ${status.status}`)
      if (status.total_pages > 0) {
        ElMessage.info(`已爬取 ${status.total_pages} 个页面`)
      }
    }
  }
}

// 按分类筛选
const filterByCategory = (category) => {
  selectedCategory.value = category
  currentPage.value = 1
}

// 事件处理
const handleSelectionChange = (selection) => {
  selectedWebsites.value = selection
}

// 工具函数
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
    '科研': 'success',
    '军事': 'warning',
    '政府': 'info'
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

const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67C23A'
  if (percentage >= 50) return '#E6A23C'
  return '#F56C6C'
}

// 组件挂载时
onMounted(() => {
  loadWebsites()
  loadCrawlStatus()
  loadCrawlParamsPresets()

  // 每30秒检查一次爬取状态
  setInterval(() => {
    checkAllWebsiteStatus()
    loadCrawlStatus()
  }, 30000)
})

// 监听筛选条件变化
watch([selectedCategory, selectedStatus], () => {
  currentPage.value = 1
})
</script>

<style scoped>
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
  flex-wrap: wrap;
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
/* 状态分布 */
.status-distribution {
  margin: 20px 0;
}
.header-actions {
  display: flex;
  gap: 10px;
}
.header-info {
  display: flex;
  align-items: center;
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
.home {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

/* 爬虫参数预设 */
.crawl-presets {
  margin-bottom: 30px;
}

.preset-options {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.current-params {
  margin: 20px 0;
}

.advanced-params {
  margin-top: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.param-help {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.preset-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
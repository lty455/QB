<template>
  <div class="home">
    <h1>多源情报数据源扫描与管理系统</h1>
    <p>管理500+个数据源，支持自动分类和智能扫描</p>

    <!-- 数据统计 -->
    <div v-if="stats.total > 0" class="stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-icon total">🌐</div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.total }}</div>
                <div class="stat-label">总数据源</div>
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
                <div class="stat-label">扫描中</div>
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
                <div class="stat-label">待扫描</div>
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
          <span>📊 数据源类别</span>
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
          <span>📊 扫描统计 (持久化)</span>
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
          <div class="crawl-stat-label">总数据源</div>
          <div class="crawl-stat-value">{{ crawlStatusData.statistics.total_websites }}</div>
        </div>

        <div class="crawl-stat-item">
          <div class="crawl-stat-label">待扫描</div>
          <div class="crawl-stat-value" style="color: #909399;">
            {{ crawlStatusData.statistics.pending }}
          </div>
        </div>

        <div class="crawl-stat-item">
          <div class="crawl-stat-label">扫描中</div>
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
          <span>⚙️ 扫描参数预设</span>
        </template>

        <div class="preset-options">
          <el-radio-group v-model="selectedPreset" @change="applyPreset">
            <el-radio-button label="quick">快速扫描</el-radio-button>
            <el-radio-button label="standard">标准扫描</el-radio-button>
            <el-radio-button label="deep">深度扫描</el-radio-button>
            <el-radio-button label="comprehensive">全面扫描</el-radio-button>
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
            <el-descriptions-item label="最大情报数目">
              <el-tag size="small">{{ crawlParams.max_pages }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="扫描深度">
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
                <el-form-item label="最大情报数目">
                  <el-slider
                    v-model="crawlParams.max_pages"
                    :min="1"
                    :max="200"
                    :step="1"
                    show-input
                  />
                </el-form-item>

                <el-form-item label="扫描深度">
                  <el-slider
                    v-model="crawlParams.max_depth"
                    :min="1"
                    :max="5"
                    :step="1"
                    show-input
                  />
                  <div class="param-help">深度1：只扫描首页<br>深度2：扫描首页链接的页面</div>
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
                  <div class="param-help">扫描每个页面的间隔时间，避免被封</div>
                </el-form-item>

                <el-form-item label="超时时间（秒）">
                  <el-slider
                    v-model="crawlParams.timeout"
                    :min="10"
                    :max="300"
                    :step="10"
                    show-input
                  />
                  <div class="param-help">单个情报扫描的最大时间</div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="递归扫描">
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
        🌐 递归扫描 ({{ selectedWebsites.length }}个)
      </el-button>

      <el-button type="warning" @click="showCrawlPresets = true">
        ⚙️ 设置扫描参数
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
            <span>📋 数据源列表 ({{ filteredWebsites.length }} 个)</span>
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

/* ========== 布局容器 ========== */
.home {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
  background:
    linear-gradient(145deg, rgba(17, 24, 39, 0.5), rgba(10, 14, 23, 0.7)),
    radial-gradient(circle at 20% 80%, rgba(124, 58, 237, 0.08), transparent 40%),
    radial-gradient(circle at 80% 20%, rgba(0, 240, 255, 0.06), transparent 40%);
  border-radius: 6px;
  min-height: calc(100vh - 120px);
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

/* ========== 统计卡片 ========== */
.stats {
  margin-bottom: 28px;
}

:deep(.el-card) {
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(11, 16, 29, 0.95)) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: var(--border-glow), 0 4px 20px rgba(0, 0, 0, 0.3) !important;
  transition: var(--transition) !important;
  backdrop-filter: blur(8px);
}

:deep(.el-card:hover) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.6), 0 8px 30px rgba(0, 0, 0, 0.4) !important;
  transform: translateY(-2px);
}

:deep(.el-card__body) {
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

:deep(.el-progress-bar__outer) {
  background: rgba(17, 24, 39, 0.8) !important;
  border-radius: 3px !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  overflow: hidden;
}

:deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, var(--primary), #7c3aed) !important;
  border-radius: 3px !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.5) !important;
  position: relative;
}

:deep(.el-progress-bar__inner::after) {
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
}

:deep(.queue-status .el-tag--success) {
  border-color: rgba(0, 255, 65, 0.4) !important;
  color: #00ff41 !important;
}

/* ========== 参数预设卡片 ========== */
.crawl-presets {
  margin-bottom: 28px;
}

:deep(.crawl-presets .el-card__header) {
  background: rgba(124, 58, 237, 0.08) !important;
  border-bottom: 1px solid rgba(124, 58, 237, 0.3) !important;
  padding: 14px 20px !important;
}

:deep(.crawl-presets .el-card__header span) {
  color: #a78bfa;
  font-weight: 600;
  font-size: 15px;
}

.preset-options {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
  flex-wrap: wrap;
  gap: 12px;
}

:deep(.preset-options .el-radio-button__inner) {
  background: rgba(17, 24, 39, 0.8) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  color: var(--text-main) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 10px 18px !important;
  transition: var(--transition) !important;
  border-radius: 3px !important;
}

:deep(.preset-options .el-radio-button__inner:hover) {
  color: var(--primary) !important;
  border-color: var(--primary) !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
}

:deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner) {
  background: var(--primary) !important;
  color: #0a0e17 !important;
  border-color: var(--primary) !important;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
  font-weight: 600 !important;
}

.current-params {
  margin: 20px 0;
  padding: 0 20px;
}

:deep(.current-params .el-descriptions) {
  background: rgba(10, 14, 23, 0.4) !important;
  border: 1px solid rgba(0, 240, 255, 0.15) !important;
  border-radius: 4px !important;
}

:deep(.current-params .el-descriptions__cell) {
  border-color: rgba(0, 240, 255, 0.15) !important;
}

:deep(.current-params .el-descriptions__label) {
  background: rgba(17, 24, 39, 0.6) !important;
  color: var(--text-dim) !important;
  font-weight: 500 !important;
  font-size: 12px !important;
}

:deep(.current-params .el-descriptions__content) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
}

:deep(.current-params .el-tag) {
  background: rgba(0, 240, 255, 0.1) !important;
  border-color: rgba(0, 240, 255, 0.4) !important;
  color: var(--primary) !important;
  font-family: 'Fira Code', monospace !important;
}

.advanced-params {
  margin-top: 20px;
  padding: 20px;
  background: rgba(10, 14, 23, 0.5);
  border-radius: 4px;
  border: 1px solid rgba(124, 58, 237, 0.25);
}

:deep(.advanced-params .el-form-item__label) {
  color: var(--text-dim) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
}

:deep(.advanced-params .el-slider__runway) {
  background: rgba(17, 24, 39, 0.8) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
}

:deep(.advanced-params .el-slider__bar) {
  background: linear-gradient(90deg, var(--primary), #7c3aed) !important;
}

:deep(.advanced-params .el-slider__button) {
  border: 2px solid var(--primary) !important;
  background: #0a0e17 !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.5) !important;
}

:deep(.advanced-params .el-input-number) {
  background: rgba(17, 24, 39, 0.8) !important;
  border-color: rgba(0, 240, 255, 0.3) !important;
}

:deep(.advanced-params .el-input-number__inner) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
}

.param-help {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 6px;
  line-height: 1.5;
  font-family: 'Fira Code', monospace;
  padding-left: 4px;
  border-left: 2px solid rgba(0, 240, 255, 0.3);
}

.preset-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px 20px;
  border-top: 1px solid rgba(0, 240, 255, 0.15);
}

:deep(.preset-footer .el-button) {
  border-radius: 3px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 10px 20px !important;
}

:deep(.preset-footer .el-button--primary) {
  background: linear-gradient(135deg, var(--primary), #7c3aed) !important;
  border: none !important;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.4) !important;
}

:deep(.preset-footer .el-button--primary:hover) {
  box-shadow: 0 0 25px rgba(0, 240, 255, 0.7) !important;
  transform: translateY(-1px);
}

/* ========== 表格区域 ========== */
.website-list {
  margin-bottom: 20px;
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

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

:deep(.header-info .el-tag) {
  background: rgba(17, 24, 39, 0.8) !important;
  border: 1px solid rgba(124, 58, 237, 0.4) !important;
  color: #a78bfa !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 11px !important;
  padding: 3px 10px !important;
}

/* ========== Element Table 深度定制 ========== */
:deep(.el-table) {
  background: #0b1120 !important;  /* 【修改】改为深色 */
  --el-table-border-color: rgba(0, 240, 255, 0.15) !important;
  --el-table-header-bg-color: rgba(17, 24, 39, 0.9) !important;
  --el-table-row-hover-bg-color: rgba(0, 240, 255, 0.08) !important;
  --el-table-text-color: var(--text-main) !important;
  --el-table-header-text-color: var(--primary) !important;
}

:deep(.el-table__header-wrapper) {
  border-bottom: 2px solid rgba(0, 240, 255, 0.3) !important;
}

:deep(.el-table th.el-table__cell) {
  background: rgba(17, 24, 39, 0.95) !important;
  color: var(--primary) !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  border-color: rgba(0, 240, 255, 0.15) !important;
}

:deep(.el-table td.el-table__cell) {
  border-color: rgba(0, 240, 255, 0.1) !important;
  background: #0b1120 !important;  /* 【修改】从 rgba(10, 14, 23, 0.3) 改为 #0b1120 */
  transition: var(--transition) !important;
  color: #e2e8f0 !important;  /* 【添加】文字改为浅色 */
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background: rgba(0, 240, 255, 0.15) !important;
  box-shadow: inset 0 0 0 1px rgba(0, 240, 255, 0.3) !important;
}

:deep(.el-table__empty-block) {
  background: rgba(17, 24, 39, 0.5) !important;
  border: 1px dashed rgba(0, 240, 255, 0.2) !important;
  border-radius: 4px !important;
}

:deep(.el-table__empty-text) {
  color: var(--text-dim) !important;
  font-family: 'Fira Code', monospace !important;
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

:deep(.el-table .el-button--info) {
  background: rgba(124, 58, 237, 0.15) !important;
  border-color: rgba(124, 58, 237, 0.4) !important;
  color: #a78bfa !important;
}

:deep(.el-table .el-button--info:hover) {
  background: #7c3aed !important;
  color: white !important;
  box-shadow: 0 0 12px rgba(124, 58, 237, 0.5) !important;
}

/* ========== 分页组件深度定制 ========== */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 240, 255, 0.2);
  gap: 8px;
}

:deep(.pagination .el-pagination) {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 总数量文字 */
:deep(.pagination .el-pagination__total) {
  color: var(--text-dim) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
  margin-right: 8px !important;
}

/* 每页数量下拉框 */
:deep(.pagination .el-pagination__sizes) {
  margin-right: 8px !important;
}

:deep(.pagination .el-select .el-input__wrapper) {
  background: rgba(17, 24, 39, 0.9) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  border-radius: 4px !important;
  box-shadow: none !important;
  padding: 0 12px !important;
  min-height: 32px !important;
}

:deep(.pagination .el-select .el-input__wrapper:hover) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.15) !important;
}

:deep(.pagination .el-select .el-input__inner) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
}

:deep(.pagination .el-select-dropdown) {
  background: rgba(11, 16, 29, 0.98) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  border-radius: 4px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 240, 255, 0.2) !important;
}

:deep(.pagination .el-select-dropdown__item) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
}

:deep(.pagination .el-select-dropdown__item.selected) {
  color: var(--primary) !important;
  background: rgba(0, 240, 255, 0.15) !important;
  font-weight: 600 !important;
}

:deep(.pagination .el-select-dropdown__item.hover) {
  background: rgba(0, 240, 255, 0.1) !important;
}

/* 页码按钮 */
:deep(.pagination .el-pagination .el-pager li) {
  background: rgba(17, 24, 39, 0.9) !important;
  border: 1px solid rgba(0, 240, 255, 0.25) !important;
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  min-width: 32px !important;
  height: 32px !important;
  line-height: 32px !important;
  margin: 0 2px !important;
  border-radius: 4px !important;
  transition: all 0.25s ease !important;
}

:deep(.pagination .el-pagination .el-pager li:hover) {
  color: var(--primary) !important;
  border-color: var(--primary) !important;
  background: rgba(0, 240, 255, 0.12) !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
  transform: translateY(-1px) !important;
}

:deep(.pagination .el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, var(--primary), #7c3aed) !important;
  color: #0a0e17 !important;
  border-color: var(--primary) !important;
  font-weight: 600 !important;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
  transform: translateY(-1px) !important;
}

/* 上一页/下一页按钮 */
:deep(.pagination .el-pagination .btn-prev),
:deep(.pagination .el-pagination .btn-next) {
  background: rgba(17, 24, 39, 0.9) !important;
  border: 1px solid rgba(0, 240, 255, 0.25) !important;
  color: var(--text-main) !important;
  min-width: 32px !important;
  height: 32px !important;
  border-radius: 4px !important;
  transition: all 0.25s ease !important;
}

:deep(.pagination .el-pagination .btn-prev:hover),
:deep(.pagination .el-pagination .btn-next:hover) {
  color: var(--primary) !important;
  border-color: var(--primary) !important;
  background: rgba(0, 240, 255, 0.12) !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
  transform: translateY(-1px) !important;
}

:deep(.pagination .el-pagination .btn-prev:disabled),
:deep(.pagination .el-pagination .btn-next:disabled) {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
  background: rgba(17, 24, 39, 0.6) !important;
}

/* 更多按钮 (...) */
:deep(.pagination .el-pagination .el-pager li.more) {
  background: transparent !important;
  border: none !important;
  color: var(--text-dim) !important;
}

/* 跳转框 */
:deep(.pagination .el-pagination__jump) {
  margin-left: 12px !important;
  color: var(--text-dim) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
}

:deep(.pagination .el-pagination__jump .el-input__wrapper) {
  background: rgba(17, 24, 39, 0.9) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  border-radius: 4px !important;
  box-shadow: none !important;
  padding: 0 10px !important;
  min-height: 32px !important;
  margin: 0 4px !important;
}

:deep(.pagination .el-pagination__jump .el-input__inner) {
  color: var(--text-main) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
  text-align: center !important;
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

  .preset-options {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
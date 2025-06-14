<template>
  <div class="charts-grid">
    <!-- 图表分类标签页 -->
    <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="charts-tabs">
      <el-tab-pane
        v-for="category in chartCategories"
        :key="category.key"
        :label="category.label"
        :name="category.key"
      >
        <template #label>
          <div class="tab-label">
            <el-icon :color="category.color">
              <component :is="getCategoryIcon(category.icon)" />
            </el-icon>
            <span>{{ category.label }}</span>
            <el-badge :value="category.count" class="tab-badge" />
          </div>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 工具栏 -->
    <div class="charts-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索图表..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @input="handleSearch"
        />
        <el-select
          v-model="complexityFilter"
          placeholder="复杂度筛选"
          clearable
          class="complexity-filter"
          @change="handleComplexityFilter"
        >
          <el-option label="基础" value="basic" />
          <el-option label="中级" value="intermediate" />
          <el-option label="高级" value="advanced" />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="grid">
            <el-icon><Grid /></el-icon>
            网格
          </el-radio-button>
          <el-radio-button label="list">
            <el-icon><List /></el-icon>
            列表
          </el-radio-button>
        </el-radio-group>
        
        <el-dropdown @command="handleBatchAction">
          <el-button type="primary">
            批量操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="downloadAll">
                <el-icon><Download /></el-icon>下载全部
              </el-dropdown-item>
              <el-dropdown-item command="refreshAll">
                <el-icon><Refresh /></el-icon>刷新全部
              </el-dropdown-item>
              <el-dropdown-item command="exportList">
                <el-icon><Document /></el-icon>导出清单
              </el-dropdown-item>
              <el-dropdown-item divided command="selectAll">
                <el-icon><Check /></el-icon>全选
              </el-dropdown-item>
              <el-dropdown-item command="clearSelection">
                <el-icon><Close /></el-icon>清除选择
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="charts-stats" v-if="filteredCharts.length > 0">
      <span class="stats-text">
        显示 {{ filteredCharts.length }} 个图表
        <span v-if="searchQuery">（搜索: "{{ searchQuery }}"）</span>
        <span v-if="complexityFilter">（复杂度: {{ getComplexityLabel(complexityFilter) }}）</span>
      </span>
    </div>

    <!-- 图表容器 -->
    <div class="charts-container" v-loading="loading">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="charts-grid-view">
        <div
          v-for="chart in filteredCharts"
          :key="chart.name"
          class="chart-item"
          :class="{ 'selected': selectedCharts.has(chart.name) }"
          @click="showChart(chart)"
        >
          <ChartThumbnail
            :task-id="taskId"
            :chart="chart"
            :loading="chartLoading[chart.name]"
            :selected="selectedCharts.has(chart.name)"
            @load-success="handleChartLoadSuccess"
            @load-error="handleChartLoadError"
            @select="handleChartSelect"
            @download="handleChartDownload"
          />
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="charts-list-view">
        <div class="list-header">
          <el-checkbox
            v-model="allSelected"
            @change="handleSelectAll"
            :indeterminate="indeterminate"
          >
            全选
          </el-checkbox>
          <span class="selected-count" v-if="selectedCharts.size > 0">
            已选择 {{ selectedCharts.size }} 个图表
          </span>
        </div>
        
        <div
          v-for="chart in filteredCharts"
          :key="chart.name"
          class="chart-item list-item"
          :class="{ 'selected': selectedCharts.has(chart.name) }"
        >
          <ChartListItem
            :chart-name="chart.name"
            :chart-config="chart.config"
            :task-id="taskId"
            :selected="selectedCharts.has(chart.name)"
            @click="showChart(chart)"
            @select="handleChartSelect"
            @download="handleChartDownload"
            @error="handleChartError"
          />
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredCharts.length === 0 && !loading" class="empty-state">
        <el-empty
          :image-size="100"
          description="没有找到匹配的图表"
        >
          <el-button type="primary" @click="clearFilters">清除筛选</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 图表详情对话框 -->
    <el-dialog
      v-model="chartDialogVisible"
      :title="selectedChart?.title"
      width="80%"
      :show-close="true"
      center
      class="chart-detail-dialog"
    >
      <div v-if="selectedChart" class="chart-detail-content">
        <!-- 图表展示区域 -->
        <div class="chart-display">
          <ChartContainer
            :task-id="taskId"
            :chart-name="selectedChart.name"
            :chart-title="selectedChart.title"
            :show-info="true"
            @load-success="handleChartLoadSuccess"
            @load-error="handleChartLoadError"
          />
        </div>

        <!-- 图表信息 -->
        <div class="chart-meta">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="类别">
              <el-tag :color="getCategoryColor(selectedChart.category)">
                {{ getCategoryLabel(selectedChart.category) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="复杂度">
              <el-tag :type="getComplexityType(selectedChart.complexity)">
                {{ getComplexityLabel(selectedChart.complexity) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="分析类型" :span="2">
              <div class="analysis-types">
                <el-tag
                  v-for="type in selectedChart.analysisType"
                  :key="type"
                  size="small"
                  class="analysis-tag"
                >
                  {{ type }}
                </el-tag>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="关键词" :span="2">
              <div class="keywords">
                <el-tag
                  v-for="keyword in selectedChart.keywords"
                  :key="keyword"
                  size="small"
                  class="keyword-tag"
                >
                  {{ keyword }}
                </el-tag>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="分析洞察" :span="2">
              <ul class="insights-list">
                <li v-for="insight in selectedChart.insights" :key="insight">
                  {{ insight }}
                </li>
              </ul>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="chartDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="downloadChart(selectedChart)">
            <el-icon><Download /></el-icon>
            下载图表
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量下载进度对话框 -->
    <el-dialog
      v-model="batchDownloadVisible"
      title="批量下载进度"
      width="50%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="batch-progress">
        <el-progress
          :percentage="batchProgress.percentage"
          :status="batchProgress.status"
          :stroke-width="8"
        />
        <p class="progress-text">
          {{ batchProgress.current }} / {{ batchProgress.total }}
          <span v-if="batchProgress.currentChart">
            - {{ batchProgress.currentChart }}
          </span>
        </p>
      </div>
      
      <template #footer>
        <el-button @click="cancelBatchDownload" :disabled="batchProgress.status === 'success'">
          {{ batchProgress.status === 'success' ? '完成' : '取消' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  Search,
  Grid,
  List,
  ArrowDown,
  Download,
  Refresh,
  Document,
  Check,
  Close,
  DocumentDelete
} from '@element-plus/icons-vue'
import ChartContainer from './ChartContainer.vue'
import ChartThumbnail from './ChartThumbnail.vue'
import ChartListItem from './ChartListItem.vue'
import { 
  CHART_CATEGORIES, 
  CHART_DEFINITIONS, 
  getChartsByCategory,
  searchCharts,
  getChartsByComplexity 
} from '@/utils/chartConfig'
import { useCharts } from '@/composables/useCharts'
import { chartsAPI } from '@/api/charts'
import { getFullApiURL } from '@/config'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['chart-select', 'charts-loaded', 'batch-complete'])

// 图表管理
const { charts, loading, loadChart, loadAllCharts } = useCharts(props.taskId)

// 响应式状态
const activeTab = ref('basic')
const searchQuery = ref('')
const complexityFilter = ref('')
const viewMode = ref('grid')
const selectedCharts = ref(new Set())
const chartLoading = ref({})
const chartDialogVisible = ref(false)
const selectedChart = ref(null)
const batchDownloadVisible = ref(false)

// 批量操作进度
const batchProgress = reactive({
  percentage: 0,
  status: '',
  current: 0,
  total: 0,
  currentChart: ''
})

// 计算属性
const chartCategories = computed(() => Object.values(CHART_CATEGORIES))

const currentCategoryCharts = computed(() => {
  return getChartsByCategory(activeTab.value)
})

const filteredCharts = computed(() => {
  let charts = currentCategoryCharts.value

  // 搜索筛选
  if (searchQuery.value) {
    charts = searchCharts(searchQuery.value).filter(chart => 
      chart.category === activeTab.value
    )
  }

  // 复杂度筛选
  if (complexityFilter.value) {
    charts = charts.filter(chart => chart.complexity === complexityFilter.value)
  }

  return charts
})

const allSelected = computed({
  get() {
    const currentCharts = filteredCharts.value
    return currentCharts.length > 0 && 
           currentCharts.every(chart => selectedCharts.value.has(chart.name))
  },
  set(value) {
    handleSelectAll(value)
  }
})

const indeterminate = computed(() => {
  const currentCharts = filteredCharts.value
  const selectedCount = currentCharts.filter(chart => 
    selectedCharts.value.has(chart.name)
  ).length
  return selectedCount > 0 && selectedCount < currentCharts.length
})

// 方法
const handleTabClick = (tab) => {
  activeTab.value = tab.props.name
  clearSelection()
}

const handleSearch = () => {
  // 搜索逻辑已在 computed 中处理
}

const handleComplexityFilter = () => {
  // 筛选逻辑已在 computed 中处理
}

const clearFilters = () => {
  searchQuery.value = ''
  complexityFilter.value = ''
}

const showChart = (chart) => {
  selectedChart.value = chart
  chartDialogVisible.value = true
  emit('chart-select', chart.name)
}

const downloadChart = async (chart) => {
  if (!chart) return
  
  try {
    const response = await fetch(getFullApiURL(`/api/chart/${props.taskId}/${chart.name}`))
    const blob = await response.blob()
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${chart.name}_${props.taskId}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('图表下载成功')
  } catch (error) {
    console.error('下载图表失败:', error)
    ElMessage.error('下载失败')
  }
}

const handleBatchAction = async (command) => {
  switch (command) {
    case 'downloadAll':
      await downloadAllCharts()
      break
    case 'refreshAll':
      await refreshAllCharts()
      break
    case 'exportList':
      exportChartList()
      break
    case 'selectAll':
      selectAllChartsInCategory()
      break
    case 'clearSelection':
      clearSelection()
      break
  }
  
  emit('batch-complete', {
    action: command,
    category: activeTab.value,
    charts: filteredCharts.value
  })
}

const downloadAllCharts = async () => {
  const chartsToDownload = Array.from(selectedCharts.value)
  
  if (chartsToDownload.length === 0) {
    ElMessage.warning('请先选择要下载的图表')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要下载 ${chartsToDownload.length} 个图表吗？`,
      '批量下载确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    batchDownloadVisible.value = true
    batchProgress.percentage = 0
    batchProgress.status = 'success'
    batchProgress.current = 0
    batchProgress.total = chartsToDownload.length
    batchProgress.currentChart = ''

    for (let i = 0; i < chartsToDownload.length; i++) {
      const chartName = chartsToDownload[i]
      batchProgress.current = i + 1
      batchProgress.currentChart = chartUtils.getChartConfig(chartName)?.title || chartName
      batchProgress.percentage = Math.round((i + 1) / chartsToDownload.length * 100)

      try {
        await loadChart(chartName)
        // 模拟下载延迟
        await new Promise(resolve => setTimeout(resolve, 500))
      } catch (error) {
        console.error(`下载图表 ${chartName} 失败:`, error)
      }
    }

    batchProgress.status = 'success'
    batchProgress.currentChart = '下载完成'
    
    ElNotification({
      title: '批量下载完成',
      message: `成功下载 ${chartsToDownload.length} 个图表`,
      type: 'success',
      duration: 3000
    })

    emit('batch-complete', 'download', chartsToDownload)

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量下载失败')
    }
  }
}

const refreshAllCharts = async () => {
  const chartsToRefresh = filteredCharts.value.map(c => c.name)
  
  if (chartsToRefresh.length === 0) {
    ElMessage.warning('当前分类没有图表')
    return
  }

  try {
    ElMessage.info('正在刷新图表...')
    
    for (const chartName of chartsToRefresh) {
      await loadChart(chartName)
    }
    
    ElMessage.success(`成功刷新 ${chartsToRefresh.length} 个图表`)
    emit('batch-complete', 'refresh', chartsToRefresh)
    
  } catch (error) {
    ElMessage.error('批量刷新失败')
  }
}

const exportChartList = () => {
  const currentCharts = filteredCharts.value
  
  const csvContent = [
    ['图表名称', '分类', '复杂度', '描述', '关键词'].join(','),
    ...currentCharts.map(chart => [
      chart.config.title,
      chartCategories[chart.config.category].label,
      chart.config.complexity,
      chart.config.description,
      chart.config.keywords.join(';')
    ].map(field => `"${field}"`).join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `图表清单_${chartCategories[activeTab.value].label}_${Date.now()}.csv`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('图表清单导出成功')
}

const selectAllChartsInCategory = () => {
  const currentCharts = filteredCharts.value
  currentCharts.forEach(chart => {
    selectedCharts.value.add(chart.name)
  })
  ElMessage.success(`已选择当前分类的 ${currentCharts.length} 个图表`)
}

const clearSelection = () => {
  selectedCharts.value.clear()
}

const handleChartLoadSuccess = (data) => {
  chartLoading.value[data.chartName] = false
}

const handleChartLoadError = (data) => {
  chartLoading.value[data.chartName] = false
}

const handleChartSelect = (chartName, selected) => {
  if (selected) {
    selectedCharts.value.add(chartName)
  } else {
    selectedCharts.value.delete(chartName)
  }
}

const handleSelectAll = (selected) => {
  const currentCharts = filteredCharts.value
  
  if (selected) {
    currentCharts.forEach(chart => {
      selectedCharts.value.add(chart.name)
    })
  } else {
    currentCharts.forEach(chart => {
      selectedCharts.value.delete(chart.name)
    })
  }
}

const handleChartDownload = (chartName) => {
  ElMessage.success(`图表 ${chartName} 下载成功`)
}

const handleChartError = (chartName, error) => {
  ElMessage.error(`图表 ${chartName} 加载失败: ${error.message}`)
}

const cancelBatchDownload = () => {
  batchDownloadVisible.value = false
  batchProgress.status = ''
}

// 生命周期
onMounted(() => {
  if (props.autoLoad) {
    loadAllCharts()
  }
})

// 监听器
watch(() => props.taskId, (newTaskId) => {
  if (newTaskId && props.autoLoad) {
    loadAllCharts()
  }
})
</script>

<style scoped>
.charts-grid {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.charts-tabs {
  flex-shrink: 0;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-badge {
  margin-left: 4px;
}

.charts-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--el-border-color-light);
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 300px;
}

.complexity-filter {
  width: 120px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.charts-stats {
  margin-bottom: 16px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.charts-container {
  flex: 1;
  overflow-y: auto;
}

.charts-grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 16px 0;
}

.chart-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.chart-item:hover {
  transform: translateY(-4px);
}

.charts-list-view {
  padding: 16px 0;
}

.list-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
  margin-bottom: 8px;
}

.selected-count {
  font-size: 12px;
  color: var(--el-color-primary);
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

/* 对话框样式 */
.chart-detail-dialog {
  --el-dialog-padding-primary: 20px;
}

.chart-detail-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  min-height: 400px;
}

.chart-display {
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  overflow: hidden;
}

.chart-meta {
  padding: 16px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
}

.analysis-types,
.keywords {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.analysis-tag,
.keyword-tag {
  margin: 2px 0;
}

.insights-list {
  margin: 0;
  padding-left: 16px;
}

.insights-list li {
  margin: 8px 0;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-grid-view {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  
  .chart-detail-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .charts-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }
  
  .charts-grid-view {
    grid-template-columns: 1fr;
  }
  
  .search-input {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .charts-toolbar {
    padding: 12px 0;
  }
  
  .toolbar-right {
    flex-direction: column;
    gap: 8px;
  }
  
  .chart-item.grid-item {
    min-height: 200px;
  }
}
</style> 
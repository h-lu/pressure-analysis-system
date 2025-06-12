<template>
  <div class="chart-detail">
    <!-- 头部信息 -->
    <div class="detail-header">
      <div class="header-content">
        <h2 class="chart-title">{{ chartConfig?.title || chartName }}</h2>
        <p class="chart-description">{{ chartConfig?.description }}</p>
        
        <div class="header-badges">
          <el-tag 
            v-if="chartConfig?.complexity" 
            :type="complexityType" 
            size="large"
          >
            {{ complexityText }}复杂度
          </el-tag>
          <el-tag 
            v-if="chartConfig?.category"
            :color="categoryColor"
            size="large"
            effect="light"
          >
            {{ categoryLabel }}
          </el-tag>
          <el-tag 
            v-if="chartConfig?.priority"
            :type="priorityType"
            size="large"
          >
            {{ priorityText }}
          </el-tag>
        </div>
      </div>
      
      <div class="header-actions">
        <el-button @click="$emit('close')" size="large">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </div>
    </div>

    <!-- 图表展示 -->
    <div class="detail-chart">
      <ChartContainer
        :chart-name="chartName"
        :task-id="taskId"
        :title="chartConfig?.title"
        :show-title="false"
        height="400px"
      />
    </div>

    <!-- 详细信息面板 -->
    <div class="detail-info">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <div class="info-section">
            <div class="info-grid">
              <div class="info-item">
                <label>图表名称:</label>
                <span>{{ chartConfig?.title || chartName }}</span>
              </div>
              <div class="info-item">
                <label>英文名称:</label>
                <span>{{ chartName }}</span>
              </div>
              <div class="info-item">
                <label>分类:</label>
                <span>{{ categoryLabel }}</span>
              </div>
              <div class="info-item">
                <label>复杂度:</label>
                <span>{{ complexityText }}</span>
              </div>
              <div class="info-item">
                <label>优先级:</label>
                <span>{{ priorityText }}</span>
              </div>
              <div class="info-item">
                <label>任务ID:</label>
                <span>{{ taskId }}</span>
              </div>
            </div>

            <div class="info-description">
              <h4>图表描述</h4>
              <p>{{ chartConfig?.description || '暂无描述' }}</p>
            </div>
          </div>
        </el-tab-pane>

        <!-- 分析类型 -->
        <el-tab-pane label="分析类型" name="analysis">
          <div class="info-section">
            <div class="analysis-types-detail">
              <h4>支持的分析类型</h4>
              <div class="types-grid">
                <el-card
                  v-for="type in chartConfig?.analysisTypes || []"
                  :key="type"
                  class="type-card"
                  shadow="hover"
                >
                  <div class="type-content">
                    <el-icon class="type-icon"><TrendCharts /></el-icon>
                    <span class="type-name">{{ type }}</span>
                  </div>
                </el-card>
              </div>
              <div v-if="!chartConfig?.analysisTypes?.length" class="no-data">
                <el-icon><InfoFilled /></el-icon>
                <span>暂无分析类型信息</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 关键词 -->
        <el-tab-pane label="关键词" name="keywords">
          <div class="info-section">
            <div class="keywords-detail">
              <h4>相关关键词</h4>
              <div class="keywords-cloud">
                <el-tag
                  v-for="keyword in chartConfig?.keywords || []"
                  :key="keyword"
                  size="large"
                  effect="plain"
                  class="keyword-tag"
                >
                  {{ keyword }}
                </el-tag>
              </div>
              <div v-if="!chartConfig?.keywords?.length" class="no-data">
                <el-icon><InfoFilled /></el-icon>
                <span>暂无关键词信息</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 洞察要点 -->
        <el-tab-pane label="洞察要点" name="insights">
          <div class="info-section">
            <div class="insights-detail">
              <h4>主要洞察</h4>
              <ul class="insights-list">
                <li 
                  v-for="(insight, index) in chartConfig?.insights || []"
                  :key="index"
                  class="insight-item"
                >
                  <div class="insight-number">{{ index + 1 }}</div>
                  <div class="insight-content">{{ insight }}</div>
                </li>
              </ul>
              <div v-if="!chartConfig?.insights?.length" class="no-data">
                <el-icon><InfoFilled /></el-icon>
                <span>暂无洞察信息</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 使用场景 -->
        <el-tab-pane label="使用场景" name="usecases">
          <div class="info-section">
            <div class="usecases-detail">
              <h4>适用场景</h4>
              <div class="usecases-list">
                <div
                  v-for="(usecase, index) in chartConfig?.useCases || []"
                  :key="index"
                  class="usecase-item"
                >
                  <div class="usecase-icon">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="usecase-content">
                    <div class="usecase-title">场景 {{ index + 1 }}</div>
                    <div class="usecase-description">{{ usecase }}</div>
                  </div>
                </div>
              </div>
              <div v-if="!chartConfig?.useCases?.length" class="no-data">
                <el-icon><InfoFilled /></el-icon>
                <span>暂无使用场景信息</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 技术信息 -->
        <el-tab-pane label="技术信息" name="technical">
          <div class="info-section">
            <div class="technical-info">
              <h4>技术详情</h4>
              <div class="tech-grid">
                <div class="tech-item">
                  <label>图表文件:</label>
                  <span>{{ chartName }}.png</span>
                </div>
                <div class="tech-item">
                  <label>API路径:</label>
                  <span>/api/chart/{{ taskId }}/{{ chartName }}</span>
                </div>
                <div class="tech-item">
                  <label>图表URL:</label>
                  <div class="url-container">
                    <el-input
                      :model-value="chartUrl"
                      readonly
                      size="small"
                    >
                      <template #append>
                        <el-button @click="copyUrl" size="small">
                          <el-icon><CopyDocument /></el-icon>
                        </el-button>
                      </template>
                    </el-input>
                  </div>
                </div>
                <div class="tech-item">
                  <label>生成时间:</label>
                  <span>{{ formatDate(new Date()) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 操作按钮 -->
    <div class="detail-actions">
      <el-button @click="handleDownload" type="primary" size="large">
        <el-icon><Download /></el-icon>
        下载图表
      </el-button>
      <el-button @click="handleFullscreen" size="large">
        <el-icon><FullScreen /></el-icon>
        全屏查看
      </el-button>
      <el-button @click="handleRefresh" size="large">
        <el-icon><Refresh /></el-icon>
        刷新图表
      </el-button>
      <el-button @click="handleShareLink" size="large">
        <el-icon><Share /></el-icon>
        分享链接
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Close,
  TrendCharts,
  InfoFilled,
  Document,
  Download,
  FullScreen,
  Refresh,
  Share,
  CopyDocument
} from '@element-plus/icons-vue'
import ChartContainer from './ChartContainer.vue'
import { chartCategories } from '@/config/chartConfig'

const props = defineProps({
  chartName: {
    type: String,
    required: true
  },
  chartConfig: {
    type: Object,
    default: () => ({})
  },
  taskId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])

// 响应式数据
const activeTab = ref('basic')

// 计算属性
const complexityType = computed(() => {
  if (!props.chartConfig?.complexity) return 'info'
  switch (props.chartConfig.complexity) {
    case 'basic': return 'success'
    case 'intermediate': return 'warning'
    case 'advanced': return 'danger'
    default: return 'info'
  }
})

const complexityText = computed(() => {
  if (!props.chartConfig?.complexity) return '未知'
  switch (props.chartConfig.complexity) {
    case 'basic': return '基础'
    case 'intermediate': return '中级'
    case 'advanced': return '高级'
    default: return '未知'
  }
})

const priorityType = computed(() => {
  if (!props.chartConfig?.priority) return 'info'
  switch (props.chartConfig.priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
})

const priorityText = computed(() => {
  if (!props.chartConfig?.priority) return '未设置'
  switch (props.chartConfig.priority) {
    case 'high': return '高优先级'
    case 'medium': return '中等优先级'
    case 'low': return '低优先级'
    default: return '未设置'
  }
})

const categoryLabel = computed(() => {
  const category = props.chartConfig?.category
  return category ? chartCategories[category]?.label || category : '未分类'
})

const categoryColor = computed(() => {
  const category = props.chartConfig?.category
  return category ? chartCategories[category]?.color || '#909399' : '#909399'
})

const chartUrl = computed(() => {
  return `http://localhost:8000/api/chart/${props.taskId}/${props.chartName}`
})

// 方法
const formatDate = (date) => {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(chartUrl.value)
    ElMessage.success('URL已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleDownload = () => {
  try {
    const link = document.createElement('a')
    link.href = chartUrl.value
    link.download = `${props.chartConfig?.title || props.chartName}_${props.taskId}.png`
    link.click()
    ElMessage.success('开始下载图表')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const handleFullscreen = () => {
  // 这里可以实现全屏查看功能
  const imageWindow = window.open('', '_blank', 'fullscreen=yes')
  imageWindow.document.write(`
    <html>
      <head>
        <title>${props.chartConfig?.title || props.chartName}</title>
        <style>
          body { margin: 0; padding: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }
          img { max-width: 100%; max-height: 100%; object-fit: contain; }
        </style>
      </head>
      <body>
        <img src="${chartUrl.value}" alt="${props.chartConfig?.title || props.chartName}" />
      </body>
    </html>
  `)
  imageWindow.document.close()
}

const handleRefresh = () => {
  // 刷新图表的逻辑会在ChartContainer组件中处理
  ElMessage.info('正在刷新图表...')
}

const handleShareLink = async () => {
  const shareText = `${props.chartConfig?.title || props.chartName} - 压力分析图表`
  const shareUrl = chartUrl.value
  
  if (navigator.share) {
    try {
      await navigator.share({
        title: shareText,
        url: shareUrl
      })
    } catch (error) {
      copyUrl()
    }
  } else {
    copyUrl()
  }
}

// 生命周期
onMounted(() => {
  // 组件挂载时的初始化逻辑
})
</script>

<style scoped>
.chart-detail {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--el-bg-color);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color-page);
}

.header-content {
  flex: 1;
}

.chart-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.chart-description {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.header-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-actions {
  flex-shrink: 0;
  margin-left: 24px;
}

.detail-chart {
  padding: 24px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.detail-info {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.info-section {
  padding: 16px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item label {
  font-weight: 500;
  color: var(--el-text-color-secondary);
  min-width: 80px;
}

.info-item span {
  color: var(--el-text-color-primary);
}

.info-description h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.info-description p {
  margin: 0;
  line-height: 1.6;
  color: var(--el-text-color-secondary);
}

.analysis-types-detail h4,
.keywords-detail h4,
.insights-detail h4,
.usecases-detail h4,
.technical-info h4 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.type-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.type-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  color: var(--el-color-primary);
  font-size: 18px;
}

.type-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.keyword-tag {
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.keyword-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.insights-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  border-left: 4px solid var(--el-color-primary);
}

.insight-number {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  background: var(--el-color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.insight-content {
  flex: 1;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

.usecases-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.usecase-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

.usecase-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.usecase-content {
  flex: 1;
}

.usecase-title {
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.usecase-description {
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.tech-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tech-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.tech-item label {
  font-weight: 500;
  color: var(--el-text-color-secondary);
  min-width: 100px;
  flex-shrink: 0;
}

.tech-item span {
  color: var(--el-text-color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
}

.url-container {
  flex: 1;
  max-width: 500px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: var(--el-text-color-placeholder);
  font-size: 14px;
}

.detail-actions {
  display: flex;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color-page);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    margin-left: 0;
    align-self: flex-end;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .types-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-actions {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .detail-actions .el-button {
    flex: 1;
    min-width: 120px;
  }
}

@media (max-width: 480px) {
  .detail-header,
  .detail-chart,
  .detail-info,
  .detail-actions {
    padding: 16px;
  }
  
  .chart-title {
    font-size: 20px;
  }
  
  .keywords-cloud {
    gap: 8px;
  }
  
  .keyword-tag {
    font-size: 12px;
    padding: 6px 10px;
  }
  
  .insight-item,
  .usecase-item {
    padding: 12px;
  }
}
</style> 
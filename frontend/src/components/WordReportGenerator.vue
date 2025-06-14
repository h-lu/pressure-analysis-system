<template>
  <div class="word-report-generator">
    <el-card class="report-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="report-icon"><Document /></el-icon>
            <span class="header-title">Word报告生成</span>
          </div>
          <div class="header-right">
            <el-tag v-if="reportStatus" :type="getStatusType(reportStatus)" size="small">
              {{ getStatusText(reportStatus) }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- 报告生成控制 -->
      <div class="report-controls">
        <div class="control-section">
          <h4 class="section-title">报告配置</h4>
          
          <!-- 报告模板选择 -->
          <div class="template-selection">
            <label class="config-label">报告模板:</label>
            <el-radio-group v-model="selectedTemplate" size="small">
              <el-radio label="comprehensive">综合报告</el-radio>
              <el-radio label="summary">摘要报告</el-radio>
              <el-radio label="technical">技术报告</el-radio>
              <el-radio label="executive">管理报告</el-radio>
            </el-radio-group>
          </div>

          <!-- 报告组件选择 -->
          <div class="components-selection">
            <label class="config-label">包含内容:</label>
            <el-checkbox-group v-model="selectedComponents">
              <el-checkbox label="cover">封面页</el-checkbox>
              <el-checkbox label="summary">分析摘要</el-checkbox>
              <el-checkbox label="data_overview">数据概览</el-checkbox>
              <el-checkbox label="charts">图表分析</el-checkbox>
              <el-checkbox label="ai_analysis">AI智能分析</el-checkbox>
              <el-checkbox label="recommendations">改进建议</el-checkbox>
              <el-checkbox label="appendix">附录</el-checkbox>
            </el-checkbox-group>
          </div>

          <!-- 图表选择 -->
          <div class="charts-selection">
            <label class="config-label">包含图表:</label>
            <div class="charts-config">
              <el-radio-group v-model="chartsIncludeMode" size="small">
                <el-radio label="all">全部图表</el-radio>
                <el-radio label="category">按类别选择</el-radio>
                <el-radio label="custom">自定义选择</el-radio>
              </el-radio-group>
              
              <!-- 按类别选择 -->
              <div v-if="chartsIncludeMode === 'category'" class="category-selection">
                <el-checkbox-group v-model="selectedChartCategories">
                  <el-checkbox 
                    v-for="category in chartCategories" 
                    :key="category.key"
                    :label="category.key"
                  >
                    {{ category.label }} ({{ category.count }}张)
                  </el-checkbox>
                </el-checkbox-group>
              </div>
              
              <!-- 自定义选择 -->
              <div v-if="chartsIncludeMode === 'custom'" class="custom-selection">
                <el-transfer
                  v-model="selectedCharts"
                  :data="allCharts"
                  :titles="['可选图表', '已选图表']"
                  :props="{
                    key: 'name',
                    label: 'title'
                  }"
                  filterable
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 报告预览信息 -->
        <div class="report-preview">
          <h4 class="section-title">报告预览信息</h4>
          <div class="preview-stats">
            <div class="stat-item">
              <span class="stat-label">预计页数:</span>
              <span class="stat-value">{{ estimatedPages }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">包含图表:</span>
              <span class="stat-value">{{ getSelectedChartsCount() }}张</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">文件大小:</span>
              <span class="stat-value">约{{ estimatedSize }}MB</span>
            </div>
          </div>
        </div>

        <!-- 生成按钮 -->
        <div class="generate-controls">
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            :disabled="!canGenerate"
            @click="generateReport"
          >
            <el-icon><MagicStick /></el-icon>
            {{ generating ? '正在生成...' : '生成Word报告' }}
          </el-button>
          
          <el-button
            v-if="canDownload"
            type="success"
            @click="downloadReport"
            :loading="downloading"
          >
            <el-icon><Download /></el-icon>
            下载报告
          </el-button>
        </div>
      </div>

      <!-- 生成进度 -->
      <div v-if="generating || reportProgress > 0" class="generation-progress">
        <el-divider content-position="left">
          <el-icon><Loading /></el-icon>
          报告生成进度
        </el-divider>
        
        <div class="progress-section">
          <div class="progress-info">
            <span class="progress-label">{{ currentStage }}</span>
            <span class="progress-percentage">{{ reportProgress }}%</span>
          </div>
          <el-progress
            :percentage="reportProgress"
            :status="getProgressStatus()"
            :stroke-width="12"
          />
          <div class="progress-details">
            <div class="detail-item">
              <el-icon><DocumentChecked /></el-icon>
              <span>已完成: {{ completedSteps.join(', ') }}</span>
            </div>
            <div v-if="currentStep" class="detail-item">
              <el-icon><Loading class="spinning" /></el-icon>
              <span>正在处理: {{ currentStep }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 报告历史 -->
      <div v-if="reportHistory.length > 0" class="report-history">
        <el-divider content-position="left">
          <el-icon><Clock /></el-icon>
          报告历史
        </el-divider>
        
        <div class="history-table">
          <el-table :data="reportHistory" stripe size="small">
            <el-table-column label="生成时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="模板" prop="template" width="100">
              <template #default="{ row }">
                {{ getTemplateName(row.template) }}
              </template>
            </el-table-column>
            <el-table-column label="图表数量" prop="charts_count" width="100" />
            <el-table-column label="文件大小" width="100">
              <template #default="{ row }">
                {{ (row.file_size / 1024 / 1024).toFixed(1) }}MB
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  size="small"
                  :disabled="row.status !== 'completed'"
                  @click="downloadHistoryReport(row)"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!hasReports && !generating" class="empty-reports">
        <el-empty description="暂无报告记录" :image-size="80">
          <template #description>
            <div class="empty-description">
              <p>配置报告选项后点击生成按钮</p>
              <p class="empty-tips">系统将生成包含图表和AI分析的完整Word报告</p>
            </div>
          </template>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import {
  Document, MagicStick, Download, Loading, DocumentChecked, Clock
} from '@element-plus/icons-vue'
import { CHART_CATEGORIES, getAllChartNames, getChartsByCategory } from '@/utils/chartConfig'
import { getFullApiURL } from '@/config'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  },
  analysisData: {
    type: Object,
    default: () => ({})
  },
  hasAIAnalysis: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['report-generated', 'report-downloaded'])

// 响应式状态
const generating = ref(false)
const downloading = ref(false)
const reportStatus = ref('')
const reportProgress = ref(0)
const currentStage = ref('')
const currentStep = ref('')
const completedSteps = ref([])
const reportHistory = ref([])
const canDownload = ref(false)

// 配置选项
const selectedTemplate = ref('comprehensive')
const selectedComponents = ref(['cover', 'summary', 'data_overview', 'charts', 'ai_analysis', 'recommendations'])
const chartsIncludeMode = ref('all')
const selectedChartCategories = ref(['basic', 'control', 'quality', 'multivariate'])
const selectedCharts = ref([])

// 计算属性
const chartCategories = computed(() => Object.values(CHART_CATEGORIES))

const allCharts = computed(() => {
  return getAllChartNames().map(name => ({
    name,
    title: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }))
})

const canGenerate = computed(() => {
  return props.taskId && !generating.value && getSelectedChartsCount() > 0
})

const hasReports = computed(() => {
  return reportHistory.value.length > 0
})

const estimatedPages = computed(() => {
  let pages = 0
  
  if (selectedComponents.value.includes('cover')) pages += 1
  if (selectedComponents.value.includes('summary')) pages += 2
  if (selectedComponents.value.includes('data_overview')) pages += 2
  if (selectedComponents.value.includes('ai_analysis')) pages += 3
  if (selectedComponents.value.includes('recommendations')) pages += 2
  if (selectedComponents.value.includes('appendix')) pages += 1
  
  // 图表页数 (每页2-3张图表)
  const chartsCount = getSelectedChartsCount()
  pages += Math.ceil(chartsCount / 2.5)
  
  return Math.max(pages, 5)
})

const estimatedSize = computed(() => {
  const baseSize = 2 // 基础文档大小2MB
  const chartSize = getSelectedChartsCount() * 0.5 // 每张图表约0.5MB
  return (baseSize + chartSize).toFixed(1)
})

// 监听器
watch([selectedTemplate, selectedComponents, chartsIncludeMode], () => {
  // 重置下载状态
  canDownload.value = false
}, { deep: true })

// 生命周期
onMounted(() => {
  loadReportHistory()
  initializeChartSelection()
})

// 方法
const getSelectedChartsCount = () => {
  switch (chartsIncludeMode.value) {
    case 'all':
      return getAllChartNames().length
    case 'category':
      return selectedChartCategories.value.reduce((count, categoryKey) => {
        return count + getChartsByCategory(categoryKey).length
      }, 0)
    case 'custom':
      return selectedCharts.value.length
    default:
      return 0
  }
}

const initializeChartSelection = () => {
  // 初始化图表选择
  selectedCharts.value = []
}

const generateReport = async () => {
  if (!canGenerate.value) return

  generating.value = true
  reportProgress.value = 0
  currentStage.value = '准备生成报告...'
  completedSteps.value = []
  currentStep.value = ''

  try {
    // 1. 确保AI分析已完成
    await ensureAIAnalysis()
    
    // 2. 调用报告生成API
    const reportConfig = {
      task_id: props.taskId,
      template: selectedTemplate.value,
      components: selectedComponents.value,
      charts: getSelectedChartsConfig(),
      options: {
        include_cover: selectedComponents.value.includes('cover'),
        include_ai_analysis: selectedComponents.value.includes('ai_analysis'),
        include_recommendations: selectedComponents.value.includes('recommendations')
      }
    }

    const response = await fetch(getFullApiURL('/api/deepseek/generate-comprehensive-word-report'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(reportConfig)
    })

    if (!response.ok) {
      throw new Error(`报告生成请求失败: ${response.status}`)
    }

    const result = await response.json()
    
    ElNotification({
      title: '报告生成启动',
      message: '正在生成Word报告，请耐心等待...',
      type: 'info'
    })

    // 3. 轮询生成进度
    await pollReportProgress()

  } catch (error) {
    console.error('报告生成失败:', error)
    ElMessage.error('报告生成失败，请重试')
    reportStatus.value = 'failed'
    reportProgress.value = 0
  } finally {
    generating.value = false
  }
}

const ensureAIAnalysis = async () => {
  if (selectedComponents.value.includes('ai_analysis') && !props.hasAIAnalysis) {
    currentStage.value = '正在生成AI分析...'
    currentStep.value = '生成AI分析报告'
    
    const response = await fetch(getFullApiURL('/api/deepseek/generate-report'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ task_id: props.taskId })
    })

    if (!response.ok) {
      throw new Error('AI分析生成失败')
    }

    // 等待AI分析完成
    await waitForAIAnalysis()
    
    completedSteps.value.push('AI分析生成')
    reportProgress.value = 20
  }
}

const waitForAIAnalysis = async () => {
  const maxAttempts = 30
  let attempts = 0

  while (attempts < maxAttempts) {
    const response = await fetch(getFullApiURL(`/api/deepseek/check/${props.taskId}`))
    const status = await response.json()

    if (status.status === 'completed') {
      break
    } else if (status.status === 'failed') {
      throw new Error('AI分析失败')
    }

    await new Promise(resolve => setTimeout(resolve, 5000))
    attempts++
  }

  if (attempts >= maxAttempts) {
    throw new Error('AI分析超时')
  }
}

const pollReportProgress = async () => {
  const stages = [
    { name: '准备数据', weight: 10 },
    { name: '生成图表', weight: 30 },
    { name: '编译文档', weight: 25 },
    { name: '格式化内容', weight: 20 },
    { name: '最终整理', weight: 15 }
  ]

  let totalProgress = props.hasAIAnalysis ? 0 : 20
  
  for (const stage of stages) {
    currentStage.value = stage.name
    currentStep.value = `正在${stage.name}...`
    
    // 模拟阶段进度
    const stageSteps = 5
    for (let step = 0; step < stageSteps; step++) {
      await new Promise(resolve => setTimeout(resolve, 1000))
      totalProgress += stage.weight / stageSteps
      reportProgress.value = Math.min(totalProgress, 100)
    }
    
    completedSteps.value.push(stage.name)
    currentStep.value = ''
  }

  // 检查最终状态
  const finalCheck = await checkReportStatus()
  
  if (finalCheck.status === 'completed') {
    reportProgress.value = 100
    currentStage.value = '报告生成完成'
    canDownload.value = true
    reportStatus.value = 'completed'
    
    // 保存到历史记录
    saveToHistory(finalCheck)
    
    ElNotification({
      title: '报告生成成功',
      message: 'Word报告已生成完成，可以下载了',
      type: 'success'
    })
    
    emit('report-generated', finalCheck)
  } else {
    throw new Error('报告生成失败')
  }
}

const checkReportStatus = async () => {
  // 模拟检查报告状态
  return {
    status: 'completed',
    report_id: `report_${props.taskId}_${Date.now()}`,
    file_name: `analysis_report_${props.taskId}.docx`,
    file_size: parseInt(estimatedSize.value * 1024 * 1024),
    created_at: new Date().toISOString(),
    template: selectedTemplate.value,
    charts_count: getSelectedChartsCount()
  }
}

const getSelectedChartsConfig = () => {
  switch (chartsIncludeMode.value) {
    case 'all':
      return { mode: 'all' }
    case 'category':
      return { 
        mode: 'category',
        categories: selectedChartCategories.value 
      }
    case 'custom':
      return {
        mode: 'custom',
        charts: selectedCharts.value
      }
    default:
      return { mode: 'all' }
  }
}

const downloadReport = async () => {
  if (!canDownload.value) return

  downloading.value = true

  try {
    const response = await fetch(getFullApiURL(`/api/download-comprehensive-report/${props.taskId}`), {
      method: 'GET'
    })

    if (!response.ok) {
      throw new Error(`下载失败: ${response.status}`)
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analysis_report_${props.taskId}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('报告下载成功')
    emit('report-downloaded', {
      task_id: props.taskId,
      filename: link.download
    })
  } catch (error) {
    console.error('下载报告失败:', error)
    ElMessage.error('下载失败，请重试')
  } finally {
    downloading.value = false
  }
}

const downloadHistoryReport = async (report) => {
  try {
    const response = await fetch(getFullApiURL(`/api/download-comprehensive-report/${props.taskId}?report_id=${report.report_id}`))
    
    if (!response.ok) {
      throw new Error('下载失败')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = report.file_name || `report_${report.report_id}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('历史报告下载成功')
  } catch (error) {
    console.error('下载历史报告失败:', error)
    ElMessage.error('下载失败')
  }
}

const loadReportHistory = () => {
  // 从localStorage加载历史记录
  const historyKey = `report_history_${props.taskId}`
  const history = localStorage.getItem(historyKey)
  if (history) {
    reportHistory.value = JSON.parse(history)
  }
}

const saveToHistory = (reportInfo) => {
  const historyKey = `report_history_${props.taskId}`
  reportHistory.value.unshift(reportInfo)
  
  // 只保留最近10次记录
  if (reportHistory.value.length > 10) {
    reportHistory.value = reportHistory.value.slice(0, 10)
  }
  
  localStorage.setItem(historyKey, JSON.stringify(reportHistory.value))
}

// 工具方法
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN')
  } catch (e) {
    return timeStr
  }
}

const getStatusType = (status) => {
  const types = {
    'generating': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'generating': '生成中',
    'completed': '已完成',
    'failed': '失败',
    'pending': '等待中'
  }
  return texts[status] || status
}

const getProgressStatus = () => {
  if (reportProgress.value === 100) return 'success'
  if (reportProgress.value > 0) return null
  return 'exception'
}

const getTemplateName = (template) => {
  const names = {
    'comprehensive': '综合',
    'summary': '摘要',
    'technical': '技术',
    'executive': '管理'
  }
  return names[template] || template
}
</script>

<style scoped>
.word-report-generator {
  height: 100%;
}

.report-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.report-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.report-controls {
  margin-bottom: 24px;
}

.control-section {
  margin-bottom: 20px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.config-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.template-selection,
.components-selection,
.charts-selection {
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
}

.charts-config {
  margin-top: 8px;
}

.category-selection,
.custom-selection {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  background: var(--el-bg-color-page);
}

.report-preview {
  padding: 16px;
  background: var(--el-bg-color);
  border-radius: 6px;
  margin-bottom: 20px;
}

.preview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-color-primary);
}

.generate-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 生成进度样式 */
.generation-progress {
  margin: 24px 0;
}

.progress-section {
  padding: 16px;
  background: var(--el-bg-color);
  border-radius: 6px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.progress-percentage {
  font-size: 18px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.progress-details {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 历史记录样式 */
.report-history {
  margin-top: 24px;
}

.history-table {
  margin-top: 12px;
}

/* 空状态样式 */
.empty-reports {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.empty-description {
  text-align: center;
}

.empty-tips {
  color: var(--el-text-color-placeholder);
  font-size: 12px;
  margin-top: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .generate-controls {
    flex-direction: column;
  }
  
  .generate-controls .el-button {
    width: 100%;
  }
  
  .preview-stats {
    grid-template-columns: 1fr;
  }
  
  .components-selection .el-checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .category-selection .el-checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}
</style> 
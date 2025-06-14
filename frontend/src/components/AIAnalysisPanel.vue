<template>
  <div class="ai-analysis-panel">
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="ai-icon"><UserFilled /></el-icon>
            <span class="header-title">DeepSeek AI 智能分析</span>
          </div>
          <div class="header-right">
            <el-tag v-if="analysisStatus" :type="getStatusType(analysisStatus)" size="small">
              {{ getStatusText(analysisStatus) }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- AI分析控制区域 -->
      <div class="analysis-controls">
        <div class="control-section">
          <h4 class="section-title">分析控制</h4>
          <div class="control-buttons">
            <el-button
              type="primary"
              :loading="generating"
              :disabled="!canGenerate"
              @click="generateAnalysis"
              size="large"
            >
              <el-icon><MagicStick /></el-icon>
              {{ generating ? '正在分析...' : '开始AI分析' }}
            </el-button>
            
            <el-button
              v-if="hasAnalysis"
              @click="refreshAnalysis"
              :loading="refreshing"
            >
              <el-icon><Refresh /></el-icon>
              重新分析
            </el-button>
            
            <el-button
              v-if="hasAnalysis"
              @click="exportAnalysis"
              :loading="exporting"
            >
              <el-icon><Download /></el-icon>
              导出分析
            </el-button>
          </div>
        </div>

        <!-- 分析选项 -->
        <div class="analysis-options" v-if="!hasAnalysis">
          <h4 class="section-title">分析选项</h4>
          <div class="options-grid">
            <el-checkbox-group v-model="selectedAnalysisTypes">
              <el-checkbox label="quality" border>质量评估</el-checkbox>
              <el-checkbox label="capability" border>过程能力</el-checkbox>
              <el-checkbox label="anomaly" border>异常检测</el-checkbox>
              <el-checkbox label="trend" border>趋势分析</el-checkbox>
              <el-checkbox label="recommendation" border>改进建议</el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </div>

      <!-- 分析结果展示 -->
      <div v-if="analysisResult" class="analysis-result">
        <el-divider content-position="left">
          <el-icon><DocumentChecked /></el-icon>
          分析结果
        </el-divider>

        <!-- 分析概要 -->
        <div class="analysis-summary">
          <el-alert
            :title="`分析完成时间: ${formatTime(analysisResult.timestamp)}`"
            type="success"
            :closable="false"
            class="summary-alert"
          >
            <template #default>
              <div class="summary-stats">
                <div class="stat-item">
                  <span class="stat-label">总体评分:</span>
                  <span class="stat-value">{{ analysisResult.overall_score }}/100</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">质量等级:</span>
                  <span class="stat-value">{{ analysisResult.quality_grade }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">分析项目:</span>
                  <span class="stat-value">{{ analysisResult.analysis_items?.length || 0 }}项</span>
                </div>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- 分析结果分类展示 -->
        <el-tabs v-model="activeAnalysisTab" class="analysis-tabs">
          <!-- 质量评估 -->
          <el-tab-pane label="质量评估" name="quality">
            <div class="analysis-section">
              <div class="section-content">
                <div class="quality-assessment">
                  <div class="assessment-metrics">
                    <div
                      v-for="metric in analysisResult.quality_assessment || []"
                      :key="metric.name"
                      class="metric-item"
                    >
                      <div class="metric-header">
                        <span class="metric-name">{{ metric.name }}</span>
                        <el-tag :type="getMetricType(metric.score)" size="small">
                          {{ metric.score }}分
                        </el-tag>
                      </div>
                      <div class="metric-description">{{ metric.description }}</div>
                      <el-progress
                        :percentage="metric.score"
                        :status="getProgressStatus(metric.score)"
                        :stroke-width="8"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 过程能力 -->
          <el-tab-pane label="过程能力" name="capability">
            <div class="analysis-section">
              <div class="capability-analysis">
                <div class="capability-indices">
                  <div
                    v-for="index in analysisResult.capability_indices || []"
                    :key="index.name"
                    class="capability-item"
                  >
                    <div class="capability-card">
                      <div class="capability-header">
                        <h5 class="capability-title">{{ index.name }}</h5>
                        <span class="capability-value">{{ index.value }}</span>
                      </div>
                      <div class="capability-interpretation">
                        <el-tag :type="getCapabilityLevel(index.value)" size="small">
                          {{ index.interpretation }}
                        </el-tag>
                      </div>
                      <div class="capability-description">{{ index.description }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 异常检测 -->
          <el-tab-pane label="异常检测" name="anomaly">
            <div class="analysis-section">
              <div class="anomaly-detection">
                <div class="anomaly-summary">
                  <el-statistic
                    title="检测到的异常"
                    :value="analysisResult.anomalies?.length || 0"
                    suffix="个"
                  />
                </div>
                
                <div v-if="analysisResult.anomalies?.length" class="anomaly-list">
                  <div
                    v-for="(anomaly, index) in analysisResult.anomalies"
                    :key="index"
                    class="anomaly-item"
                  >
                    <div class="anomaly-header">
                      <el-icon class="anomaly-icon"><Warning /></el-icon>
                      <span class="anomaly-type">{{ anomaly.type }}</span>
                      <el-tag :type="getSeverityType(anomaly.severity)" size="small">
                        {{ anomaly.severity }}
                      </el-tag>
                    </div>
                    <div class="anomaly-description">{{ anomaly.description }}</div>
                    <div class="anomaly-location" v-if="anomaly.location">
                      <el-icon><Location /></el-icon>
                      位置: {{ anomaly.location }}
                    </div>
                  </div>
                </div>
                
                <el-empty v-else description="未检测到异常数据" :image-size="60" />
              </div>
            </div>
          </el-tab-pane>

          <!-- 趋势分析 -->
          <el-tab-pane label="趋势分析" name="trend">
            <div class="analysis-section">
              <div class="trend-analysis">
                <div class="trend-insights">
                  <div
                    v-for="(trend, index) in analysisResult.trend_analysis || []"
                    :key="index"
                    class="trend-item"
                  >
                    <div class="trend-header">
                      <el-icon class="trend-icon">
                        <TrendCharts v-if="trend.direction === 'up'" />
                        <Bottom v-else-if="trend.direction === 'down'" />
                        <Minus v-else />
                      </el-icon>
                      <span class="trend-title">{{ trend.metric }}</span>
                      <el-tag :type="getTrendType(trend.direction)" size="small">
                        {{ getTrendText(trend.direction) }}
                      </el-tag>
                    </div>
                    <div class="trend-description">{{ trend.description }}</div>
                    <div class="trend-confidence">
                      <span class="confidence-label">置信度:</span>
                      <el-progress
                        :percentage="trend.confidence * 100"
                        :stroke-width="6"
                        :show-text="false"
                        class="confidence-bar"
                      />
                      <span class="confidence-value">{{ (trend.confidence * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 改进建议 -->
          <el-tab-pane label="改进建议" name="recommendation">
            <div class="analysis-section">
              <div class="recommendations">
                <div
                  v-for="(rec, index) in analysisResult.recommendations || []"
                  :key="index"
                  class="recommendation-item"
                >
                  <div class="recommendation-header">
                    <div class="rec-priority">
                      <el-tag :type="getPriorityType(rec.priority)" size="small">
                        {{ getPriorityText(rec.priority) }}
                      </el-tag>
                    </div>
                    <h5 class="rec-title">{{ rec.title }}</h5>
                  </div>
                  <div class="rec-description">{{ rec.description }}</div>
                  <div v-if="rec.actions?.length" class="rec-actions">
                    <h6 class="actions-title">具体行动:</h6>
                    <ul class="actions-list">
                      <li v-for="action in rec.actions" :key="action">{{ action }}</li>
                    </ul>
                  </div>
                  <div v-if="rec.expected_impact" class="rec-impact">
                    <el-icon><TrendCharts /></el-icon>
                    <span>预期改善: {{ rec.expected_impact }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 分析历史记录 -->
      <div v-if="analysisHistory.length > 0" class="analysis-history">
        <el-divider content-position="left">
          <el-icon><Clock /></el-icon>
          分析历史
        </el-divider>
        
        <div class="history-list">
          <div
            v-for="(history, index) in analysisHistory.slice(0, 5)"
            :key="index"
            class="history-item"
            @click="loadHistoryAnalysis(history)"
          >
            <div class="history-header">
              <span class="history-time">{{ formatTime(history.timestamp) }}</span>
              <el-tag :type="getStatusType(history.status)" size="small">
                {{ getStatusText(history.status) }}
              </el-tag>
            </div>
            <div class="history-summary">
              评分: {{ history.overall_score }}/100 | 
              等级: {{ history.quality_grade }}
            </div>
          </div>
        </div>
        
        <div class="history-actions">
          <el-button size="small" @click="showAllHistory">查看全部历史</el-button>
          <el-button size="small" @click="clearHistory" type="danger" plain>清空历史</el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!hasAnalysis && !generating" class="empty-analysis">
        <el-empty description="暂无AI分析结果" :image-size="80">
          <template #description>
            <div class="empty-description">
              <p>点击上方按钮开始AI智能分析</p>
              <p class="empty-tips">AI将为您提供质量评估、异常检测、趋势分析和改进建议</p>
            </div>
          </template>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import {
  UserFilled, MagicStick, Refresh, Download, DocumentChecked,
  Warning, Location, TrendCharts, Bottom, Minus, Clock
} from '@element-plus/icons-vue'
import { getFullApiURL } from '@/config'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  },
  analysisData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['analysis-generated', 'analysis-exported'])

// 响应式状态
const generating = ref(false)
const refreshing = ref(false)
const exporting = ref(false)
const analysisStatus = ref('')
const analysisResult = ref(null)
const analysisHistory = ref([])
const activeAnalysisTab = ref('quality')
const selectedAnalysisTypes = ref(['quality', 'capability', 'anomaly', 'trend', 'recommendation'])

// 计算属性
const canGenerate = computed(() => {
  return props.taskId && !generating.value && selectedAnalysisTypes.value.length > 0
})

const hasAnalysis = computed(() => {
  return analysisResult.value !== null
})

// 生命周期
onMounted(() => {
  loadExistingAnalysis()
  loadAnalysisHistory()
})

// 方法
const generateAnalysis = async () => {
  if (!canGenerate.value) return

  generating.value = true
  analysisStatus.value = 'generating'

  try {
    ElNotification({
      title: 'AI分析启动',
      message: '正在启动DeepSeek AI分析引擎...',
      type: 'info'
    })

    const response = await fetch(getFullApiURL('/api/deepseek/generate-report'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        task_id: props.taskId,
        analysis_types: selectedAnalysisTypes.value
      })
    })

    if (!response.ok) {
      throw new Error(`AI分析请求失败: ${response.status}`)
    }

    const result = await response.json()
    
    // 轮询分析状态
    await pollAnalysisStatus()

  } catch (error) {
    console.error('AI分析失败:', error)
    ElMessage.error('AI分析失败，请重试')
    analysisStatus.value = 'failed'
  } finally {
    generating.value = false
  }
}

const pollAnalysisStatus = async () => {
  const maxAttempts = 60 // 最多轮询5分钟
  let attempts = 0

  const poll = async () => {
    try {
      const response = await fetch(getFullApiURL(`/api/deepseek/check/${props.taskId}`))
      const status = await response.json()

      analysisStatus.value = status.status

      if (status.status === 'completed') {
        await loadAnalysisResult()
        ElNotification({
          title: 'AI分析完成',
          message: '智能分析已完成，请查看分析结果',
          type: 'success'
        })
        return true
      } else if (status.status === 'failed') {
        throw new Error('AI分析失败')
      } else if (attempts < maxAttempts) {
        attempts++
        setTimeout(poll, 5000) // 5秒后重试
      } else {
        throw new Error('AI分析超时')
      }
    } catch (error) {
      console.error('轮询分析状态失败:', error)
      analysisStatus.value = 'failed'
      ElMessage.error('获取分析状态失败')
    }
  }

  await poll()
}

const loadExistingAnalysis = async () => {
  try {
    const response = await fetch(getFullApiURL(`/api/deepseek/get/${props.taskId}`))
    
    if (response.ok) {
      const result = await response.json()
      if (result.analysis) {
        analysisResult.value = parseAnalysisResult(result.analysis)
        analysisStatus.value = 'completed'
      }
    }
  } catch (error) {
    console.error('加载已有分析失败:', error)
  }
}

const loadAnalysisResult = async () => {
  try {
    const response = await fetch(getFullApiURL(`/api/deepseek/get/${props.taskId}`))
    const result = await response.json()
    
    if (result.analysis) {
      analysisResult.value = parseAnalysisResult(result.analysis)
      
      // 保存到历史记录
      saveToHistory(analysisResult.value)
      
      emit('analysis-generated', analysisResult.value)
    }
  } catch (error) {
    console.error('加载分析结果失败:', error)
    ElMessage.error('加载分析结果失败')
  }
}

const parseAnalysisResult = (analysisText) => {
  // 这里需要解析AI返回的文本，提取结构化数据
  // 实际实现需要根据AI返回格式调整
  return {
    timestamp: new Date().toISOString(),
    overall_score: Math.floor(Math.random() * 40 + 60), // 模拟数据
    quality_grade: 'B+',
    analysis_items: ['质量评估', '过程能力', '异常检测', '趋势分析', '改进建议'],
    quality_assessment: [
      {
        name: '测量精度',
        score: 85,
        description: '测量精度符合标准要求，偶有小幅偏差'
      },
      {
        name: '数据稳定性',
        score: 78,
        description: '数据总体稳定，存在轻微波动'
      },
      {
        name: '过程一致性',
        score: 92,
        description: '过程表现一致，控制效果良好'
      }
    ],
    capability_indices: [
      {
        name: 'Cp',
        value: '1.25',
        interpretation: '良好',
        description: '过程能力指数表明过程能力良好'
      },
      {
        name: 'Cpk',
        value: '1.18',
        interpretation: '良好',
        description: '过程能力偏移指数在可接受范围内'
      }
    ],
    anomalies: [
      {
        type: '数据异常',
        severity: '中等',
        description: '检测到3个数据点超出3σ限制',
        location: '时间点: 15:30-15:45'
      }
    ],
    trend_analysis: [
      {
        metric: '平均值趋势',
        direction: 'stable',
        description: '平均值保持稳定，无明显趋势变化',
        confidence: 0.85
      }
    ],
    recommendations: [
      {
        priority: 'high',
        title: '优化测量流程',
        description: '建议对异常时段的测量流程进行检查和优化',
        actions: [
          '检查测量设备校准状态',
          '分析异常时段的环境因素',
          '优化操作流程'
        ],
        expected_impact: '提升5-10%的测量稳定性'
      }
    ]
  }
}

const refreshAnalysis = async () => {
  refreshing.value = true
  
  try {
    // 清除当前结果
    analysisResult.value = null
    
    // 重新生成分析
    await generateAnalysis()
    
    ElMessage.success('分析已刷新')
  } catch (error) {
    ElMessage.error('刷新分析失败')
  } finally {
    refreshing.value = false
  }
}

const exportAnalysis = async () => {
  if (!analysisResult.value) return

  exporting.value = true

  try {
    const exportData = {
      task_id: props.taskId,
      analysis_result: analysisResult.value,
      export_time: new Date().toISOString()
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ai_analysis_${props.taskId}_${Date.now()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('分析结果已导出')
    emit('analysis-exported', exportData)
  } catch (error) {
    console.error('导出分析失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const loadAnalysisHistory = () => {
  // 从localStorage加载历史记录
  const historyKey = `analysis_history_${props.taskId}`
  const history = localStorage.getItem(historyKey)
  if (history) {
    analysisHistory.value = JSON.parse(history)
  }
}

const saveToHistory = (result) => {
  const historyKey = `analysis_history_${props.taskId}`
  analysisHistory.value.unshift({
    ...result,
    id: Date.now()
  })
  
  // 只保留最近10次记录
  if (analysisHistory.value.length > 10) {
    analysisHistory.value = analysisHistory.value.slice(0, 10)
  }
  
  localStorage.setItem(historyKey, JSON.stringify(analysisHistory.value))
}

const loadHistoryAnalysis = (history) => {
  analysisResult.value = history
  ElMessage.info('已加载历史分析结果')
}

const showAllHistory = () => {
  // 显示完整历史记录对话框
  ElMessageBox.alert(
    `共有 ${analysisHistory.value.length} 条分析记录`,
    '分析历史',
    {
      confirmButtonText: '确定'
    }
  )
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有分析历史记录吗？',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const historyKey = `analysis_history_${props.taskId}`
    localStorage.removeItem(historyKey)
    analysisHistory.value = []
    
    ElMessage.success('历史记录已清空')
  } catch {
    // 用户取消
  }
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
    'generating': '分析中',
    'completed': '已完成',
    'failed': '失败',
    'pending': '等待中'
  }
  return texts[status] || status
}

const getMetricType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 70) return 'warning'
  return 'danger'
}

const getProgressStatus = (score) => {
  if (score >= 90) return 'success'
  if (score >= 70) return 'warning'
  return 'exception'
}

const getCapabilityLevel = (value) => {
  const val = parseFloat(value)
  if (val >= 1.33) return 'success'
  if (val >= 1.0) return 'warning'
  return 'danger'
}

const getSeverityType = (severity) => {
  const types = {
    '低': 'info',
    '中等': 'warning',
    '高': 'danger',
    '严重': 'danger'
  }
  return types[severity] || 'info'
}

const getTrendType = (direction) => {
  const types = {
    'up': 'success',
    'down': 'danger',
    'stable': 'info'
  }
  return types[direction] || 'info'
}

const getTrendText = (direction) => {
  const texts = {
    'up': '上升',
    'down': '下降',
    'stable': '稳定'
  }
  return texts[direction] || direction
}

const getPriorityType = (priority) => {
  const types = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return types[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = {
    'high': '高优先级',
    'medium': '中优先级',
    'low': '低优先级'
  }
  return texts[priority] || priority
}
</script>

<style scoped>
.ai-analysis-panel {
  height: 100%;
}

.analysis-card {
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

.ai-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.analysis-controls {
  margin-bottom: 24px;
}

.control-section,
.analysis-options {
  margin-bottom: 20px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.control-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.options-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.analysis-result {
  flex: 1;
}

.analysis-summary {
  margin-bottom: 20px;
}

.summary-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  gap: 8px;
}

.stat-label {
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.analysis-tabs {
  margin-top: 16px;
}

.analysis-section {
  padding: 16px 0;
}

/* 质量评估样式 */
.assessment-metrics {
  display: grid;
  gap: 16px;
}

.metric-item {
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-name {
  font-weight: 600;
}

.metric-description {
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
  font-size: 14px;
}

/* 过程能力样式 */
.capability-indices {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.capability-card {
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
}

.capability-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.capability-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.capability-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.capability-interpretation {
  margin-bottom: 8px;
}

.capability-description {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

/* 异常检测样式 */
.anomaly-detection {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.anomaly-summary {
  padding: 16px;
  background: var(--el-bg-color);
  border-radius: 6px;
  text-align: center;
}

.anomaly-list {
  display: grid;
  gap: 12px;
}

.anomaly-item {
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
}

.anomaly-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.anomaly-icon {
  color: var(--el-color-warning);
}

.anomaly-type {
  font-weight: 600;
}

.anomaly-description {
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.anomaly-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

/* 趋势分析样式 */
.trend-insights {
  display: grid;
  gap: 16px;
}

.trend-item {
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
}

.trend-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.trend-icon {
  color: var(--el-color-primary);
}

.trend-title {
  font-weight: 600;
  flex: 1;
}

.trend-description {
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
}

.trend-confidence {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.confidence-bar {
  flex: 1;
}

.confidence-value {
  font-size: 12px;
  font-weight: 600;
}

/* 改进建议样式 */
.recommendations {
  display: grid;
  gap: 16px;
}

.recommendation-item {
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.rec-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.rec-description {
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
}

.rec-actions {
  margin-bottom: 12px;
}

.actions-title {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
}

.actions-list {
  margin: 0;
  padding-left: 16px;
  color: var(--el-text-color-secondary);
}

.rec-impact {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--el-color-success);
}

/* 历史记录样式 */
.analysis-history {
  margin-top: 24px;
}

.history-list {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.history-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.history-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.history-summary {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.history-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* 空状态样式 */
.empty-analysis {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
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
  .control-buttons {
    flex-direction: column;
  }
  
  .control-buttons .el-button {
    width: 100%;
  }
  
  .summary-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .capability-indices {
    grid-template-columns: 1fr;
  }
  
  .options-grid .el-checkbox {
    width: 100%;
    margin-right: 0;
    margin-bottom: 8px;
  }
}
</style> 
<template>
  <div class="task-status-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">任务监控 / 任务ID: {{ taskId }}</h1>
      <!-- 操作按钮 -->
      <div class="page-actions">
        <el-button 
          v-if="taskInfo.status === 'completed'" 
          class="action-btn" 
          type="primary"
          @click="viewResults"
        >
          查看结果
        </el-button>
        <el-button 
          v-else 
          class="action-btn" 
          type="info"
          @click="viewResults"
        >
          查看详情
        </el-button>
        <el-button 
          v-if="taskInfo.status === 'running' || taskInfo.status === 'pending'" 
          class="action-btn stop-btn" 
          type="danger" 
          @click="stopTask"
        >
          停止任务
        </el-button>
      </div>
    </div>

    <!-- 任务状态卡片 -->
    <div class="task-status-card">
      <div class="card-header">
        <h3 class="card-title">📊 实时任务状态</h3>
      </div>
      <div class="card-content">
        <!-- 状态指示器 -->
        <div class="status-indicator-row">
          <div class="status-badge" :class="taskInfo.status">
            <span class="status-dot"></span>
            <span class="status-text">{{ getStatusText(taskInfo.status) }}</span>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="progress-section">
          <div class="progress-header">
            <span class="progress-label">图表生成进度:</span>
            <span class="progress-percentage">{{ chartsCompleted }}/35 ({{ Math.round(progressPercentage) }}%)</span>
          </div>
          <el-progress 
            :percentage="progressPercentage" 
            :status="progressStatus"
            :stroke-width="20"
            :show-text="false"
            class="main-progress"
          />
        </div>

        <!-- 状态信息 -->
        <div class="status-info">
          <div class="status-message">
            {{ getStatusMessage() }}
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getFullApiURL } from '@/config'

const route = useRoute()
const router = useRouter()
const taskId = ref(route.params.taskId || '4514bcbf-1459-409c-8e17-710e6b73ab31')

// 任务信息
const taskInfo = ref({
  status: 'pending',
  task_id: '',
  created_at: '',
  started_at: '',
  completed_at: '',
  progress: 0,
  message: '',
  error: null
})

// 图表计数
const chartsCompleted = ref(0)
const totalCharts = 35

// 轮询状态
const isPolling = ref(false)

// 计算属性
const progressPercentage = computed(() => {
  if (taskInfo.value.status === 'completed') return 100
  return Math.min((chartsCompleted.value / totalCharts) * 100, 99)
})

const progressStatus = computed(() => {
  if (taskInfo.value.status === 'failed') return 'exception'
  if (taskInfo.value.status === 'completed') return 'success'
  return 'active'
})

const getStatusText = (status) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'running': return '运行中'
    case 'failed': return '失败'
    case 'pending': return '等待中'
    default: return status
  }
}

const getStatusMessage = () => {
  switch (taskInfo.value.status) {
    case 'pending':
      return '任务正在准备中，请稍候...'
    case 'running':
      return `正在生成图表... (${chartsCompleted.value}/${totalCharts})`
    case 'completed':
      return '所有图表生成完成！即将跳转到结果页面...'
    case 'failed':
      return `任务执行失败: ${taskInfo.value.error || '未知错误'}`
    default:
      return '获取状态中...'
  }
}

// 检查图表生成进度
const checkChartsProgress = async () => {
  try {
    const response = await fetch(getFullApiURL(`/api/charts-count/${taskId.value}`))
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        chartsCompleted.value = data.count || 0
      }
    }
  } catch (error) {
    console.log('获取图表计数失败:', error)
    // 如果API不存在，根据任务状态估算进度
    if (taskInfo.value.status === 'running') {
      chartsCompleted.value = Math.min(chartsCompleted.value + 1, totalCharts - 1)
    } else if (taskInfo.value.status === 'completed') {
      chartsCompleted.value = totalCharts
    }
  }
}

const viewResults = () => {
  router.push(`/results/${taskId.value}`)
}

const stopTask = async () => {
  try {
    const response = await fetch(getFullApiURL(`/api/task/${taskId.value}`), {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('任务已停止')
      // 重新获取任务状态
      await fetchTaskInfo()
    } else {
      ElMessage.error('停止任务失败')
    }
  } catch (error) {
    console.error('停止任务失败:', error)
    ElMessage.error('停止任务失败')
  }
}

const pollTaskStatus = async () => {
  if (!taskId.value) return

  try {
    const response = await fetch(getFullApiURL(`/api/task/${taskId.value}`), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`获取任务状态失败: ${response.status}`)
    }

    const data = await response.json()
    console.log('任务状态:', data)

    if (data.success && data.task) {
      taskInfo.value = data.task
      
      if (data.task.status === 'completed') {
        ElMessage.success('分析完成！')
        stopPolling()
        // 延迟跳转，让用户看到完成消息
        setTimeout(() => {
          router.push(`/results/${taskId.value}`)
        }, 1500)
      } else if (data.task.status === 'failed') {
        ElMessage.error(`分析失败: ${data.task.error || '未知错误'}`)
        stopPolling()
      }
    }
  } catch (error) {
    console.error('获取任务状态失败:', error)
    ElMessage.error('获取任务状态失败')
  }
}

const fetchTaskInfo = async () => {
  if (!taskId.value) return

  try {
    const response = await fetch(getFullApiURL(`/api/task/${taskId.value}`))
    
    if (!response.ok) {
      throw new Error(`获取任务信息失败: ${response.status}`)
    }

    const data = await response.json()
    console.log('任务状态:', data)
    
    if (data.success && data.task) {
      const previousStatus = taskInfo.value.status
      taskInfo.value = data.task
      
      // 检查图表进度
      await checkChartsProgress()
      
      // 检查任务是否完成
      if (data.task.status === 'completed' && previousStatus !== 'completed') {
        console.log('任务完成，准备跳转')
        ElMessage.success('分析完成！')
        stopPolling()
        // 延迟跳转，让用户看到完成消息
        setTimeout(() => {
          console.log('执行跳转到结果页面')
          router.push(`/results/${taskId.value}`)
        }, 2000)
      } else if (data.task.status === 'failed') {
        ElMessage.error(`分析失败: ${data.task.error || '未知错误'}`)
        stopPolling()
      }
    } else {
      throw new Error(data.message || '获取任务信息失败')
    }
  } catch (error) {
    console.error('获取任务信息失败:', error)
    ElMessage.error(error.message || '获取任务信息失败')
  }
}

// 定时更新任务状态
let statusInterval = null

const startPolling = () => {
  if (statusInterval) return
  isPolling.value = true
  statusInterval = setInterval(fetchTaskInfo, 2000)
}

const stopPolling = () => {
  if (statusInterval) {
    clearInterval(statusInterval)
    statusInterval = null
  }
  isPolling.value = false
}

onMounted(async () => {
  console.log('TaskStatus页面加载，任务ID:', taskId.value)
  
  // 立即获取一次状态
  await fetchTaskInfo()
  
  // 只有当任务还在运行时才启动轮询
  if (['running', 'pending'].includes(taskInfo.value.status)) {
    console.log('启动轮询，当前状态:', taskInfo.value.status)
    startPolling()
  } else {
    console.log('任务已完成或失败，不启动轮询，状态:', taskInfo.value.status)
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.task-status-page {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  color: #303133;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  width: 80px;
  height: 30px;
  font-size: 12px;
}

.stop-btn {
  background-color: #F56C6C;
  border-color: #F56C6C;
}

/* 任务状态卡片 */
.task-status-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 20px;
  min-height: 180px;
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.card-title {
  color: #303133;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.card-content {
  padding: 20px;
}

.status-indicator-row {
  margin-bottom: 20px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.status-badge.running .status-dot {
  width: 16px;
  height: 16px;
  background-color: #E6A23C;
  border-radius: 50%;
}

.status-badge.running .status-text {
  color: #E6A23C;
  font-size: 16px;
  font-weight: bold;
}

.status-badge.completed .status-dot {
  width: 16px;
  height: 16px;
  background-color: #67C23A;
  border-radius: 50%;
}

.status-badge.completed .status-text {
  color: #67C23A;
  font-size: 16px;
  font-weight: bold;
}

.status-badge.failed .status-dot {
  width: 16px;
  height: 16px;
  background-color: #F56C6C;
  border-radius: 50%;
}

.status-badge.failed .status-text {
  color: #F56C6C;
  font-size: 16px;
  font-weight: bold;
}

/* 进度条样式 */
.progress-section {
  margin: 25px 0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.progress-percentage {
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
}

.main-progress {
  margin-bottom: 10px;
}

/* 状态信息 */
.status-info {
  margin-top: 20px;
  text-align: center;
}

.status-message {
  font-size: 14px;
  color: #606266;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.status-badge.pending .status-dot {
  width: 16px;
  height: 16px;
  background-color: #909399;
  border-radius: 50%;
}

.status-badge.pending .status-text {
  color: #909399;
  font-size: 16px;
  font-weight: bold;
}

.task-info-grid {
  margin-bottom: 25px;
}

.info-row {
  display: flex;
  gap: 50px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  gap: 10px;
}

.info-label {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
  min-width: 80px;
}

.info-value {
  color: #606266;
  font-size: 14px;
}

.remaining-time {
  color: #E6A23C;
}

.progress-section {
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-label {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
}

.progress-percentage {
  color: #E6A23C;
  font-size: 14px;
  font-weight: bold;
}

.main-progress {
  width: 400px;
}

.current-stage {
  margin-bottom: 15px;
}

.stage-label {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
}

.stage-text {
  color: #E6A23C;
  font-size: 14px;
  margin-left: 10px;
}

.detailed-progress {
  display: flex;
  gap: 50px;
}

.detail-info {
  color: #909399;
  font-size: 12px;
}

/* 任务日志卡片 */
.task-log-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  min-height: 320px;
}

.log-toolbar {
  background-color: #f9f9f9;
  border-bottom: 1px solid #e4e7ed;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.real-time-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.indicator-dot.active {
  background-color: #67C23A;
}

.indicator-text {
  color: #606266;
  font-size: 12px;
}

.export-btn {
  background-color: #e4e7ed;
  color: #909399;
  border: none;
  width: 80px;
  height: 20px;
  font-size: 11px;
}

.log-content {
  background-color: #fafbfc;
  border: 1px solid #e4e7ed;
  padding: 15px 20px;
  max-height: 245px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 11px;
}

.log-time {
  color: #909399;
  min-width: 70px;
}

.log-icon {
  min-width: 15px;
  text-align: center;
}

.log-icon.completed {
  color: #67C23A;
}

.log-icon.running {
  color: #E6A23C;
}

.log-icon.failed {
  color: #F56C6C;
}

.log-message {
  color: #303133;
  flex: 1;
}

.log-running .log-message {
  color: #E6A23C;
}

.log-predictions {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 10px;
}

.prediction .log-time,
.prediction .log-message {
  color: #c0c4cc;
}

.prediction-text {
  font-style: italic;
}
</style> 
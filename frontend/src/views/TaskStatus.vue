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

        <!-- 任务信息网格 -->
        <div class="task-info-grid">
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">开始时间:</span>
              <span class="info-value">{{ taskInfo.startTime || '未开始' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">运行时长:</span>
              <span class="info-value">{{ taskInfo.duration }}</span>
            </div>
          </div>
          
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">预计剩余:</span>
              <span class="info-value remaining-time">{{ taskInfo.remainingTime }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">数据文件:</span>
              <span class="info-value">{{ taskInfo.dataFile || '未知文件' }}</span>
            </div>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="progress-section">
          <div class="progress-header">
            <span class="progress-label">总体进度:</span>
            <span class="progress-percentage">{{ taskInfo.progress }}%</span>
          </div>
          <el-progress 
            :percentage="taskInfo.progress" 
            :status="progressStatus"
            :stroke-width="16"
            :show-text="false"
            class="main-progress"
          />
        </div>

        <!-- 当前阶段 -->
        <div class="current-stage">
          <span class="stage-label">当前阶段:</span>
          <span class="stage-text">{{ taskInfo.currentStage || '等待中' }}</span>
        </div>

        <!-- 详细进度 -->
        <div class="detailed-progress">
          <span class="detail-info">图表生成进度: {{ taskInfo.chartsCompleted }}/35 完成</span>
          <span class="detail-info">当前: {{ taskInfo.currentChart || '等待开始' }}</span>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const taskId = ref(route.params.taskId || '4514bcbf-1459-409c-8e17-710e6b73ab31')

// 任务信息
const taskInfo = ref({
  startTime: '',
  duration: '',
  remainingTime: '',
  dataFile: '',
  progress: 0,
  currentStage: '',
  chartsCompleted: 0,
  currentChart: '',
  status: 'pending'
})

// 轮询状态
const isPolling = ref(false)

// 计算属性
const progressStatus = computed(() => {
  if (taskInfo.value.status === 'failed') return 'exception'
  if (taskInfo.value.progress < 100) return 'active'
  return 'success'
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

const viewResults = () => {
  router.push(`/results/${taskId.value}`)
}

const stopTask = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/task/${taskId.value}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('任务已停止')
      // 重新获取任务状态
      await fetchTaskStatus()
    } else {
      ElMessage.error('停止任务失败')
    }
  } catch (error) {
    console.error('停止任务失败:', error)
    ElMessage.error('停止任务失败')
  }
}



// 获取任务状态
const fetchTaskStatus = async () => {
  try {
    console.log('Fetching task status for:', taskId.value)
    
    const response = await fetch(`http://localhost:8000/api/task/${taskId.value}`)
    
    if (!response.ok) {
      throw new Error(`API返回错误: ${response.status}`)
    }
    
    const data = await response.json()
    const task = data.task || data
    console.log('API返回数据:', task)
    
    if (!task) {
      throw new Error('无法找到任务信息')
    }
    
    // 计算图表生成进度（基于实际生成的图片文件）
    let chartsCompleted = 0
    let calculatedProgress = task.progress || 0
    
    if (task.status === 'completed') {
      chartsCompleted = 35
      calculatedProgress = 100
    } else if (task.status === 'running') {
      // 如果任务正在运行，尝试通过图表数量计算进度
      chartsCompleted = Math.floor((task.progress || 0) * 35 / 100)
      calculatedProgress = Math.min((chartsCompleted / 35) * 100, 99) // 确保不超过99%，除非真正完成
    }
    
    // 格式化时间显示
    const formatDisplayTime = (timeStr) => {
      if (!timeStr) return ''
      try {
        const date = new Date(timeStr)
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
      } catch (e) {
        return timeStr
      }
    }
    
    // 使用正确的字段名（后端返回的是started_at而不是start_time）
    const startTime = task.started_at || task.created_at
    
    taskInfo.value = {
      startTime: formatDisplayTime(startTime),
      duration: task.status === 'completed' 
        ? calculateCompletedDuration(startTime, task.completed_at)
        : formatDuration(startTime),
      remainingTime: task.status === 'completed' 
        ? '已完成' 
        : calculateRemainingTime(calculatedProgress, startTime),
      dataFile: task.filename || task.name || task.file_id || '未知文件',
      progress: Math.round(calculatedProgress),
      currentStage: task.status === 'completed' ? '分析完成' : (task.message || task.stage || '等待中'),
      chartsCompleted: chartsCompleted,
      currentChart: task.status === 'completed' ? '所有图表已生成' : (task.message || task.stage || '等待开始'),
      status: task.status || 'pending'
    }
    
    console.log('更新后的taskInfo:', taskInfo.value)
    
    // 如果任务完成或失败，停止轮询
    if (['completed', 'failed'].includes(task.status)) {
      stopPolling()
    }
    
  } catch (error) {
    console.error('获取任务状态失败:', error)
    // 如果API调用失败，停止轮询
    stopPolling()
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString()
}

// 格式化持续时间
const formatDuration = (startTime) => {
  if (!startTime) return '00:00:00'
  const start = new Date(startTime)
  const now = new Date()
  const diff = now - start
  const hours = Math.floor(diff / 3600000)
  const minutes = Math.floor((diff % 3600000) / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// 计算已完成任务的持续时间
const calculateCompletedDuration = (startTime, endTime) => {
  if (!startTime) return '00:00:00'
  
  const start = new Date(startTime)
  const end = endTime ? new Date(endTime) : new Date(startTime)
  const diff = end - start
  
  const hours = Math.floor(diff / 3600000)
  const minutes = Math.floor((diff % 3600000) / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// 计算剩余时间
const calculateRemainingTime = (progress, startTime) => {
  if (!progress || progress <= 0 || !startTime) return '计算中...'
  if (progress >= 100) return '已完成'
  
  const start = new Date(startTime)
  const now = new Date()
  const elapsed = now - start
  const totalTime = elapsed / (progress / 100)
  const remaining = totalTime - elapsed
  if (remaining <= 0) return '即将完成'
  
  const minutes = Math.floor(remaining / 60000)
  const seconds = Math.floor((remaining % 60000) / 1000)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}



// 定时更新任务状态
let statusInterval = null

const startPolling = () => {
  if (statusInterval) return
  isPolling.value = true
  statusInterval = setInterval(fetchTaskStatus, 2000)
}

const stopPolling = () => {
  if (statusInterval) {
    clearInterval(statusInterval)
    statusInterval = null
  }
  isPolling.value = false
}

onMounted(async () => {
  // 立即获取一次状态
  await fetchTaskStatus()
  
  // 只有当任务还在运行时才启动轮询
  if (['running', 'pending'].includes(taskInfo.value.status)) {
    startPolling()
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
  min-height: 200px;
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
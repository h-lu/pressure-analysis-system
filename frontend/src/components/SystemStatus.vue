<template>
  <el-card class="system-status">
    <template #header>
      <div class="status-header">
        <el-icon><Monitor /></el-icon>
        <span>系统状态</span>
        <el-button 
          @click="refreshStatus" 
          :loading="refreshing"
          size="small"
          type="text"
        >
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </template>
    
    <div class="status-list">
      <div class="status-item">
        <span class="status-label">后端服务</span>
        <el-tag 
          :type="backendStatus.type" 
          :icon="backendStatus.icon"
          size="small"
        >
          {{ backendStatus.text }}
        </el-tag>
      </div>
      
      <div class="status-item">
        <span class="status-label">AI服务</span>
        <el-tag 
          :type="aiStatus.type"
          :icon="aiStatus.icon" 
          size="small"
        >
          {{ aiStatus.text }}
        </el-tag>
      </div>
      
      <div class="status-item">
        <span class="status-label">运行任务</span>
        <el-tag type="info" size="small">
          {{ runningTasks }}个
        </el-tag>
      </div>
      
      <div class="status-item">
        <span class="status-label">内存使用</span>
        <el-tag 
          :type="memoryUsage > 80 ? 'danger' : memoryUsage > 60 ? 'warning' : 'success'"
          size="small"
        >
          {{ memoryUsage }}%
        </el-tag>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Monitor, Refresh, Connection, UserFilled, Warning } from '@element-plus/icons-vue'
import { apiClient } from '@/utils/http'
import { useAnalysisStore } from '@/stores/analysis'

const analysisStore = useAnalysisStore()

const refreshing = ref(false)
const backendStatus = ref({
  type: 'info',
  text: '检测中...',
  icon: Connection
})
const aiStatus = ref({
  type: 'info', 
  text: '检测中...',
  icon: UserFilled
})
const runningTasks = ref(0)
const memoryUsage = ref(46)

let statusInterval = null

// 检测后端状态
const checkBackendStatus = async () => {
  try {
    const response = await apiClient.get('/health')
    if (response.status === 'healthy') {
      backendStatus.value = {
        type: 'success',
        text: '正常',
        icon: Connection
      }
      return true
    }
  } catch (error) {
    console.error('后端连接失败:', error)
    backendStatus.value = {
      type: 'danger',
      text: '断开',
      icon: Warning
    }
    return false
  }
}

// 检测AI服务状态
const checkAIStatus = async () => {
  try {
    await apiClient.get('/api/deepseek/test-connection')
    aiStatus.value = {
      type: 'success',
      text: '正常',
      icon: UserFilled
    }
  } catch (error) {
    console.error('AI服务连接失败:', error)
    aiStatus.value = {
      type: 'warning',
      text: '不可用',
      icon: Warning
    }
  }
}

// 检测运行任务数量
const checkRunningTasks = async () => {
  try {
    const tasks = await apiClient.get('/api/tasks')
    const running = tasks.filter(task => 
      ['pending', 'running'].includes(task.status)
    ).length
    runningTasks.value = running
  } catch (error) {
    console.error('获取任务列表失败:', error)
    runningTasks.value = 0
  }
}

// 刷新所有状态
const refreshStatus = async () => {
  if (refreshing.value) return
  
  refreshing.value = true
  try {
    await Promise.all([
      checkBackendStatus(),
      checkAIStatus(), 
      checkRunningTasks()
    ])
  } finally {
    refreshing.value = false
  }
}

// 定期检查状态
const startStatusCheck = () => {
  statusInterval = setInterval(async () => {
    await refreshStatus()
  }, 30000) // 每30秒检查一次
}

const stopStatusCheck = () => {
  if (statusInterval) {
    clearInterval(statusInterval)
    statusInterval = null
  }
}

onMounted(() => {
  refreshStatus()
  startStatusCheck()
})

onUnmounted(() => {
  stopStatusCheck()
})
</script>

<style scoped>
.system-status {
  margin-bottom: 16px;
}

.status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-header span {
  margin-left: 8px;
  font-weight: 500;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.status-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
}
</style> 
<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h3>压力分析系统</h3>
    </div>
    
    <el-menu
      :default-active="activeRoute"
      :router="true"
      class="sidebar-menu"
    >
      <el-menu-item index="/analysis">
        <el-icon><Upload /></el-icon>
        <span>数据分析</span>
      </el-menu-item>

      <el-menu-item index="/tasks">
        <el-icon><List /></el-icon>
        <span>任务管理</span>
      </el-menu-item>

      <el-submenu index="results">
        <template #title>
          <el-icon><DataAnalysis /></el-icon>
          <span>分析结果</span>
        </template>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
      </el-submenu>

      <el-menu-item index="/files">
        <el-icon><Folder /></el-icon>
        <span>文件管理</span>
      </el-menu-item>

      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <span>系统设置</span>
      </el-menu-item>
    </el-menu>

    <!-- 系统状态 -->
    <div class="system-status">
      <el-divider content-position="left">
        <span class="status-title">系统状态</span>
      </el-divider>
      
      <div class="status-item" :class="getSystemStatusClass()">
        <el-icon class="status-icon" :class="getSystemStatusIconClass()">
          <component :is="getSystemStatusIcon()" />
        </el-icon>
        <span class="status-text">{{ getSystemStatusText() }}</span>
      </div>
      
      <div class="status-item">
        <el-icon class="status-icon"><Cpu /></el-icon>
        <span class="status-text">运行中任务: {{ runningTasks }}</span>
      </div>
      
      <div class="status-item clickable" @click="runDiagnostic">
        <el-icon class="status-icon"><Connection /></el-icon>
        <span class="status-text">后端连接: {{ backendStatus ? '正常' : '异常' }}</span>
        <el-tag :type="backendStatus ? 'success' : 'danger'" size="small">
          {{ backendStatus ? '✓' : '✗' }}
        </el-tag>
      </div>
      
      <!-- 错误统计 -->
      <div class="status-item error-stats clickable" @click="showErrorDetails = !showErrorDetails">
        <el-icon class="status-icon" :class="errorSeverity"><WarningFilled /></el-icon>
        <span class="status-text">错误统计: {{ totalErrors }}</span>
        <el-tag :type="errorSeverity" size="small">{{ totalErrors }}</el-tag>
      </div>

      <!-- 错误详情 -->
      <div v-if="showErrorDetails" class="error-details">
        <div class="error-item">
          <span>文件格式错误</span>
          <el-tag size="small" type="danger">{{ errorStats.fileFormatErrors }}</el-tag>
        </div>
        <div class="error-item">
          <span>R脚本错误</span>
          <el-tag size="small" type="danger">{{ errorStats.rScriptErrors }}</el-tag>
        </div>
        <div class="error-item">
          <span>内存不足错误</span>
          <el-tag size="small" type="warning">{{ errorStats.memoryErrors }}</el-tag>
        </div>
        <div class="error-item">
          <span>网络连接错误</span>
          <el-tag size="small" type="info">{{ errorStats.networkErrors }}</el-tag>
        </div>
        
        <!-- 错误管理操作 -->
        <div class="error-actions">
          <el-button size="small" @click="handleQuickDiagnostics">
            <el-icon><Refresh /></el-icon>
            快速诊断
          </el-button>
          <el-button size="small" @click="handleExportReport">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
          <el-button size="small" type="danger" @click="handleClearErrors">
            <el-icon><CircleClose /></el-icon>
            清除记录
          </el-button>
        </div>
      </div>

      <!-- 传统错误记录 -->
      <div v-if="unreadErrorsCount > 0" class="status-item error-summary clickable" @click="showErrorPanel">
        <el-icon class="status-icon error"><WarningFilled /></el-icon>
        <span class="status-text">系统错误: {{ unreadErrorsCount }}</span>
        <el-button type="text" size="small" class="error-btn">查看</el-button>
      </div>
      
      <!-- 快速操作 -->
      <div class="quick-actions">
        <el-button 
          size="small" 
          type="primary" 
          @click="runDiagnostic"
          :loading="diagnosticRunning"
        >
          <el-icon><Monitor /></el-icon>
          系统诊断
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Upload, 
  List, 
  DataAnalysis, 
  Clock, 
  Folder, 
  Setting,
  Connection,
  Cpu,
  Monitor,
  WarningFilled,
  CircleCheck,
  Warning,
  CircleClose,
  Refresh,
  Download
} from '@element-plus/icons-vue'
import { useAnalysisStore } from '@/stores/analysis'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useSpecificErrorHandler } from '@/composables/useSpecificErrorHandler'

const route = useRoute()
const analysisStore = useAnalysisStore()
const errorHandler = useErrorHandler()
const { errorStats, exportDiagnosticReport, clearErrorHistory } = useSpecificErrorHandler()

const activeRoute = computed(() => route.path)
const backendStatus = ref(true)
const runningTasks = ref(0)
const diagnosticRunning = ref(false)

let statusPolling = null

// 计算属性
const unreadErrorsCount = computed(() => {
  return errorHandler.errors.value.filter(e => !e.resolved).length
})

// 系统状态相关方法
const getSystemStatusClass = () => {
  const status = errorHandler.systemStatus.value
  return {
    'status-normal': status === 'normal',
    'status-warning': status === 'warning',
    'status-error': status === 'error',
    'status-critical': status === 'critical'
  }
}

const getSystemStatusIconClass = () => {
  const status = errorHandler.systemStatus.value
  return {
    'healthy': status === 'normal',
    'warning': status === 'warning',
    'error': status === 'error' || status === 'critical'
  }
}

const getSystemStatusIcon = () => {
  const status = errorHandler.systemStatus.value
  switch (status) {
    case 'normal': return CircleCheck
    case 'warning': return Warning
    case 'error':
    case 'critical': return CircleClose
    default: return CircleCheck
  }
}

const getSystemStatusText = () => {
  const status = errorHandler.systemStatus.value
  switch (status) {
    case 'normal': return '系统正常'
    case 'warning': return '系统警告'
    case 'error': return '系统错误'
    case 'critical': return '严重错误'
    default: return '系统正常'
  }
}

// 状态检查方法
async function checkBackendStatus() {
  try {
    const response = await fetch('http://localhost:8000/health', { 
      timeout: 5000,
      signal: AbortSignal.timeout(5000)
    })
    backendStatus.value = response.ok
    
    if (!response.ok) {
      errorHandler.handleNetworkError(
        new Error(`Backend health check failed: ${response.status}`),
        'Sidebar health check'
      )
    }
  } catch (error) {
    backendStatus.value = false
    errorHandler.handleNetworkError(error, 'Sidebar backend connection check')
  }
}

async function updateRunningTasks() {
  try {
    // 从 store 获取运行中的任务数量
    const tasks = analysisStore.tasks || []
    runningTasks.value = tasks.filter(task => 
      ['pending', 'running'].includes(task.status)
    ).length
  } catch (error) {
    errorHandler.handleError(error, 'Sidebar task count update')
  }
}

// 系统诊断
const runDiagnostic = async () => {
  diagnosticRunning.value = true
  try {
    const diagnostics = await errorHandler.runSystemDiagnostic()
    
    const status = diagnostics.backend_connection ? '正常' : '异常'
    const networkStatus = diagnostics.network_status
    const errorCount = diagnostics.errors_count
    
    await ElMessageBox.alert(
      `后端连接: ${status}\n网络状态: ${networkStatus}\n浏览器兼容性: ${diagnostics.browser_compatibility ? '支持' : '不支持'}\n本地存储: ${diagnostics.local_storage ? '可用' : '不可用'}\n错误记录: ${errorCount} 条`,
      '系统诊断结果',
      {
        confirmButtonText: '确定',
        type: diagnostics.backend_connection ? 'success' : 'warning'
      }
    )
  } catch (error) {
    errorHandler.handleError(error, 'System diagnostic')
  } finally {
    diagnosticRunning.value = false
  }
}

// 显示错误面板
const showErrorPanel = () => {
  const recentErrors = errorHandler.errors.value
    .filter(e => !e.resolved)
    .slice(0, 5)
    .map(e => `[${e.type}] ${e.message}`)
    .join('\n')
  
  ElMessageBox.confirm(
    `最近的错误:\n${recentErrors}`,
    '错误记录',
    {
      confirmButtonText: '导出诊断报告',
      cancelButtonText: '清理错误',
      type: 'warning'
    }
  ).then(() => {
    errorHandler.exportDiagnosticReport()
  }).catch((action) => {
    if (action === 'cancel') {
      errorHandler.clearErrors()
    }
  })
}

function startStatusPolling() {
  statusPolling = setInterval(async () => {
    await checkBackendStatus()
    await updateRunningTasks()
  }, 15000) // 每15秒检查一次
}

function stopStatusPolling() {
  if (statusPolling) {
    clearInterval(statusPolling)
    statusPolling = null
  }
}

onMounted(() => {
  checkBackendStatus()
  updateRunningTasks()
  startStatusPolling()
})

onUnmounted(() => {
  stopStatusPolling()
})

// 错误处理相关
const showErrorDetails = ref(false)

const totalErrors = computed(() => {
  return errorStats.fileFormatErrors + 
         errorStats.rScriptErrors + 
         errorStats.memoryErrors + 
         errorStats.networkErrors
})

const errorSeverity = computed(() => {
  if (totalErrors.value === 0) return 'success'
  if (totalErrors.value < 5) return 'warning'
  return 'danger'
})

// 快速诊断
const handleQuickDiagnostics = async () => {
  ElMessage.info('正在运行系统诊断...')
  try {
    await errorHandler.runSystemDiagnostics()
    ElMessage.success('系统诊断完成')
  } catch (error) {
    ElMessage.error('诊断过程中出现错误')
  }
}

// 导出错误报告
const handleExportReport = () => {
  exportDiagnosticReport()
}

// 清除错误历史
const handleClearErrors = () => {
  clearErrorHistory()
}
</script>

<style scoped>
.sidebar {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: white;
  border-right: 1px solid var(--el-border-color-light);
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  text-align: center;
}

.sidebar-menu {
  flex: 1;
  border: none;
}

.sidebar-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 4px 8px;
  border-radius: 6px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: var(--el-color-primary-light-9);
}

.sidebar-menu .el-menu-item.is-active {
  background-color: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  font-weight: 600;
}

.sidebar-menu .el-submenu .el-menu-item {
  padding-left: 48px !important;
}

.system-status {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-light);
}

.status-title {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 14px;
  transition: all 0.2s;
}

.status-item.clickable {
  cursor: pointer;
  border-radius: 4px;
  padding: 8px 4px;
}

.status-item.clickable:hover {
  background-color: var(--el-color-primary-light-9);
}

.status-item .status-text {
  flex: 1;
  color: var(--el-text-color-secondary);
}

.status-icon {
  font-size: 16px;
}

.status-icon.healthy {
  color: var(--el-color-success);
}

.status-icon.warning {
  color: var(--el-color-warning);
}

.status-icon.error {
  color: var(--el-color-danger);
}

/* 系统状态类 */
.status-item.status-normal .status-text {
  color: var(--el-color-success);
}

.status-item.status-warning .status-text {
  color: var(--el-color-warning);
}

.status-item.status-error .status-text,
.status-item.status-critical .status-text {
  color: var(--el-color-danger);
}

.error-summary {
  background-color: var(--el-color-danger-light-9);
  border-left: 3px solid var(--el-color-danger);
  margin: 4px 0;
  padding: 8px;
  border-radius: 4px;
}

.error-btn {
  color: var(--el-color-danger) !important;
  font-size: 12px;
  padding: 0;
  margin-left: 8px;
}

.quick-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.quick-actions .el-button {
  width: 100%;
  justify-content: center;
}

.error-stats {
  cursor: pointer;
  transition: background-color 0.2s;
}

.error-stats:hover {
  background-color: var(--el-fill-color-light);
}

.error-details {
  margin-top: 8px;
  padding: 8px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 4px;
  border: 1px solid var(--el-border-color-light);
}

.error-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
}

.error-item:last-child {
  margin-bottom: 8px;
}

.error-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}

.error-actions .el-button {
  justify-content: flex-start;
  font-size: 11px;
  padding: 4px 8px;
}

.error-actions .el-button .el-icon {
  margin-right: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .error-actions .el-button {
    flex: 1;
    min-width: 0;
  }
}
</style> 
import { ref } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'

export function useErrorHandler() {
  const errors = ref([])
  const networkErrors = ref([])
  const systemStatus = ref('normal') // normal, warning, error
  
  // 错误类型定义
  const ERROR_TYPES = {
    NETWORK: 'network',
    API: 'api',
    VALIDATION: 'validation',
    SYSTEM: 'system',
    TASK: 'task'
  }
  
  // 严重程度定义
  const SEVERITY_LEVELS = {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    CRITICAL: 'critical'
  }
  
  // 错误处理器
  const handleError = (error, context = '', options = {}) => {
    const {
      type = ERROR_TYPES.SYSTEM,
      severity = SEVERITY_LEVELS.MEDIUM,
      showMessage = true,
      showNotification = false,
      retryable = false,
      silent = false
    } = options
    
    // 创建错误对象
    const errorObj = {
      id: Date.now() + Math.random(),
      type,
      severity,
      context,
      message: getErrorMessage(error),
      originalError: error,
      timestamp: new Date(),
      retryable,
      resolved: false
    }
    
    // 记录错误
    errors.value.unshift(errorObj)
    
    // 保持错误列表在合理大小
    if (errors.value.length > 100) {
      errors.value = errors.value.slice(0, 100)
    }
    
    // 更新系统状态
    updateSystemStatus()
    
    // 显示用户反馈
    if (!silent) {
      if (showNotification) {
        showErrorNotification(errorObj)
      } else if (showMessage) {
        showErrorMessage(errorObj)
      }
    }
    
    // 记录到控制台
    console.error(`[${context}] ${type.toUpperCase()} Error:`, error)
    
    return errorObj
  }
  
  // 网络错误处理
  const handleNetworkError = (error, context = '') => {
    const networkError = {
      id: Date.now() + Math.random(),
      context,
      error: error,
      timestamp: new Date(),
      status: error.response?.status || 'unknown',
      message: getNetworkErrorMessage(error)
    }
    
    networkErrors.value.unshift(networkError)
    
    // 保持网络错误列表在合理大小
    if (networkErrors.value.length > 50) {
      networkErrors.value = networkErrors.value.slice(0, 50)
    }
    
    return handleError(error, context, {
      type: ERROR_TYPES.NETWORK,
      severity: getNetworkErrorSeverity(error),
      showMessage: true,
      retryable: isRetryableNetworkError(error)
    })
  }
  
  // API错误处理
  const handleAPIError = (error, context = '') => {
    return handleError(error, context, {
      type: ERROR_TYPES.API,
      severity: getAPIErrorSeverity(error),
      showMessage: true,
      retryable: isRetryableAPIError(error)
    })
  }
  
  // 任务错误处理
  const handleTaskError = (error, taskId, context = '') => {
    return handleError(error, `Task ${taskId}: ${context}`, {
      type: ERROR_TYPES.TASK,
      severity: SEVERITY_LEVELS.HIGH,
      showNotification: true,
      retryable: true
    })
  }
  
  // 验证错误处理
  const handleValidationError = (error, context = '') => {
    return handleError(error, context, {
      type: ERROR_TYPES.VALIDATION,
      severity: SEVERITY_LEVELS.LOW,
      showMessage: true,
      retryable: false
    })
  }
  
  // 系统诊断
  const runSystemDiagnostic = async () => {
    const diagnostics = {
      timestamp: new Date(),
      backend_connection: false,
      api_health: false,
      browser_compatibility: true,
      local_storage: true,
      network_status: 'unknown',
      errors_count: errors.value.length,
      critical_errors: errors.value.filter(e => e.severity === SEVERITY_LEVELS.CRITICAL).length
    }
    
    try {
      // 检查后端连接
      const response = await fetch('/health', { timeout: 5000 })
      diagnostics.backend_connection = response.ok
      diagnostics.api_health = response.ok
      diagnostics.network_status = 'online'
    } catch (error) {
      diagnostics.backend_connection = false
      diagnostics.api_health = false
      diagnostics.network_status = 'offline'
    }
    
    // 检查本地存储
    try {
      localStorage.setItem('test', 'test')
      localStorage.removeItem('test')
      diagnostics.local_storage = true
    } catch (error) {
      diagnostics.local_storage = false
    }
    
    // 检查浏览器兼容性
    diagnostics.browser_compatibility = 
      'fetch' in window && 
      'Promise' in window && 
      'WebSocket' in window
    
    return diagnostics
  }
  
  // 导出诊断报告
  const exportDiagnosticReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      system_status: systemStatus.value,
      errors: errors.value.slice(0, 20), // 最近20个错误
      network_errors: networkErrors.value.slice(0, 10), // 最近10个网络错误
      user_agent: navigator.userAgent,
      url: window.location.href,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    }
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `diagnostic_report_${Date.now()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('诊断报告已导出')
    return report
  }
  
  // 清理错误
  const clearErrors = () => {
    errors.value = []
    networkErrors.value = []
    updateSystemStatus()
    ElMessage.success('错误记录已清理')
  }
  
  // 标记错误为已解决
  const resolveError = (errorId) => {
    const error = errors.value.find(e => e.id === errorId)
    if (error) {
      error.resolved = true
      updateSystemStatus()
    }
  }
  
  // 重试错误操作
  const retryOperation = async (errorId, retryFn) => {
    const error = errors.value.find(e => e.id === errorId)
    if (!error || !error.retryable) {
      ElMessage.warning('此错误不支持重试')
      return false
    }
    
    try {
      await retryFn()
      resolveError(errorId)
      ElMessage.success('重试成功')
      return true
    } catch (retryError) {
      handleError(retryError, `重试失败: ${error.context}`)
      return false
    }
  }
  
  // 工具函数
  const getErrorMessage = (error) => {
    if (typeof error === 'string') return error
    if (error.message) return error.message
    if (error.response?.data?.message) return error.response.data.message
    if (error.response?.data?.detail) return error.response.data.detail
    return '未知错误'
  }
  
  const getNetworkErrorMessage = (error) => {
    if (error.code === 'NETWORK_ERROR') return '网络连接失败'
    if (error.code === 'TIMEOUT') return '请求超时'
    if (error.response?.status === 404) return '请求的资源不存在'
    if (error.response?.status === 500) return '服务器内部错误'
    if (error.response?.status >= 400 && error.response?.status < 500) {
      return '请求参数错误'
    }
    return '网络请求失败'
  }
  
  const getNetworkErrorSeverity = (error) => {
    if (error.response?.status >= 500) return SEVERITY_LEVELS.HIGH
    if (error.response?.status === 404) return SEVERITY_LEVELS.MEDIUM
    if (error.code === 'TIMEOUT') return SEVERITY_LEVELS.MEDIUM
    return SEVERITY_LEVELS.LOW
  }
  
  const getAPIErrorSeverity = (error) => {
    if (error.response?.status >= 500) return SEVERITY_LEVELS.HIGH
    if (error.response?.status === 401) return SEVERITY_LEVELS.HIGH
    return SEVERITY_LEVELS.MEDIUM
  }
  
  const isRetryableNetworkError = (error) => {
    return error.code === 'TIMEOUT' || 
           error.response?.status >= 500 ||
           error.code === 'NETWORK_ERROR'
  }
  
  const isRetryableAPIError = (error) => {
    return error.response?.status >= 500 ||
           error.response?.status === 429 // Too Many Requests
  }
  
  const updateSystemStatus = () => {
    const criticalErrors = errors.value.filter(
      e => !e.resolved && e.severity === SEVERITY_LEVELS.CRITICAL
    )
    const highErrors = errors.value.filter(
      e => !e.resolved && e.severity === SEVERITY_LEVELS.HIGH
    )
    
    if (criticalErrors.length > 0) {
      systemStatus.value = 'critical'
    } else if (highErrors.length > 0) {
      systemStatus.value = 'error'
    } else if (errors.value.filter(e => !e.resolved).length > 5) {
      systemStatus.value = 'warning'
    } else {
      systemStatus.value = 'normal'
    }
  }
  
  const showErrorMessage = (errorObj) => {
    const type = errorObj.severity === SEVERITY_LEVELS.CRITICAL ? 'error' :
                 errorObj.severity === SEVERITY_LEVELS.HIGH ? 'error' :
                 errorObj.severity === SEVERITY_LEVELS.MEDIUM ? 'warning' : 'info'
    
    ElMessage({
      message: errorObj.message,
      type,
      duration: errorObj.severity === SEVERITY_LEVELS.CRITICAL ? 0 : 5000
    })
  }
  
  const showErrorNotification = (errorObj) => {
    ElNotification({
      title: `${errorObj.type.toUpperCase()} 错误`,
      message: errorObj.message,
      type: 'error',
      duration: 0,
      onClick: () => {
        // 可以打开错误详情
        showErrorDetails(errorObj)
      }
    })
  }
  
  const showErrorDetails = (errorObj) => {
    ElMessageBox.alert(
      `错误类型: ${errorObj.type}\n严重程度: ${errorObj.severity}\n上下文: ${errorObj.context}\n时间: ${errorObj.timestamp.toLocaleString()}\n详细信息: ${errorObj.message}`,
      '错误详情',
      {
        confirmButtonText: '确定',
        type: 'error'
      }
    )
  }
  
  return {
    // 状态
    errors,
    networkErrors,
    systemStatus,
    
    // 错误处理方法
    handleError,
    handleNetworkError,
    handleAPIError,
    handleTaskError,
    handleValidationError,
    
    // 诊断方法
    runSystemDiagnostic,
    exportDiagnosticReport,
    
    // 管理方法
    clearErrors,
    resolveError,
    retryOperation,
    showErrorDetails,
    
    // 常量
    ERROR_TYPES,
    SEVERITY_LEVELS
  }
} 
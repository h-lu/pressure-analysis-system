import { ref, reactive, computed, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { chartsAPI } from '@/api/charts'

export function useCharts(taskId) {
  // 响应式数据
  const loading = ref(false)
  const error = ref(null)
  const charts = reactive({})
  const chartStatus = reactive({})
  const batchLoading = ref(false)
  const batchProgress = ref(0)
  
  // 缓存清理定时器
  let cacheCleanupTimer = null

  // 计算属性
  const loadedCharts = computed(() => {
    return Object.keys(charts).filter(name => charts[name] && !chartStatus[name]?.error)
  })

  const failedCharts = computed(() => {
    return Object.keys(chartStatus).filter(name => chartStatus[name]?.error)
  })

  const loadingCharts = computed(() => {
    return Object.keys(chartStatus).filter(name => chartStatus[name]?.loading)
  })

  const totalCharts = computed(() => {
    return Object.keys(chartStatus).length
  })

  const successRate = computed(() => {
    if (totalCharts.value === 0) return 0
    return Math.round((loadedCharts.value.length / totalCharts.value) * 100)
  })

  // 方法
  const loadChart = async (chartName, options = {}) => {
    if (!taskId || !chartName) {
      throw new Error('缺少必要参数')
    }

    const { force = false, timeout = 30000 } = options

    // 如果已经加载且不强制刷新，返回缓存
    if (!force && charts[chartName] && !chartStatus[chartName]?.error) {
      return charts[chartName]
    }

    // 设置加载状态
    chartStatus[chartName] = { loading: true, error: null }
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      const url = `http://localhost:8000/api/chart/${taskId}/${chartName}`
      const response = await fetch(url, { 
        signal: controller.signal,
        headers: {
          'Cache-Control': force ? 'no-cache' : 'default'
        }
      })
      
      clearTimeout(timeoutId)

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('图表文件不存在')
        } else if (response.status === 500) {
          throw new Error('服务器内部错误')
        } else {
          throw new Error(`加载失败: ${response.status}`)
        }
      }

      const blob = await response.blob()
      const chartUrl = URL.createObjectURL(blob)
      
      // 缓存图表URL
      charts[chartName] = chartUrl
      chartStatus[chartName] = { loading: false, error: null, loadTime: Date.now() }
      
      return chartUrl
    } catch (err) {
      const errorMessage = err.name === 'AbortError' ? '加载超时' : err.message
      chartStatus[chartName] = { 
        loading: false, 
        error: errorMessage,
        retryCount: (chartStatus[chartName]?.retryCount || 0) + 1
      }
      
      ElMessage.error(`图表 ${chartName} 加载失败: ${errorMessage}`)
      throw err
    }
  }

  const loadAllCharts = async (chartNames, options = {}) => {
    if (!chartNames || chartNames.length === 0) {
      ElMessage.warning('没有可加载的图表')
      return
    }

    batchLoading.value = true
    batchProgress.value = 0
    
    const { concurrency = 3, onProgress } = options
    let completed = 0
    const results = {}

    try {
      // 分批并发加载
      for (let i = 0; i < chartNames.length; i += concurrency) {
        const batch = chartNames.slice(i, i + concurrency)
        
        const batchPromises = batch.map(async (chartName) => {
          try {
            const url = await loadChart(chartName, options)
            results[chartName] = { success: true, url }
          } catch (error) {
            results[chartName] = { success: false, error: error.message }
          } finally {
            completed++
            batchProgress.value = Math.round((completed / chartNames.length) * 100)
            
            if (onProgress) {
              onProgress(completed, chartNames.length, batchProgress.value)
            }
          }
        })

        await Promise.all(batchPromises)
      }

      const successCount = Object.values(results).filter(r => r.success).length
      const failCount = chartNames.length - successCount
      
      if (failCount === 0) {
        ElMessage.success(`成功加载所有 ${chartNames.length} 个图表`)
      } else if (successCount === 0) {
        ElMessage.error(`所有图表加载失败`)
      } else {
        ElMessage.warning(`加载完成: 成功 ${successCount} 个，失败 ${failCount} 个`)
      }

      return results
    } finally {
      batchLoading.value = false
      batchProgress.value = 100
    }
  }

  const refreshChart = async (chartName) => {
    return loadChart(chartName, { force: true })
  }

  const refreshAllCharts = async (chartNames) => {
    return loadAllCharts(chartNames, { force: true })
  }

  const downloadChart = async (chartName, filename) => {
    const chartUrl = charts[chartName]
    if (!chartUrl) {
      throw new Error('图表未加载')
    }

    try {
      const link = document.createElement('a')
      link.href = chartUrl
      link.download = filename || `${chartName}_${taskId}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      ElMessage.success('图表下载成功')
    } catch (error) {
      ElMessage.error('图表下载失败')
      throw error
    }
  }

  const downloadAllCharts = async (chartNames, options = {}) => {
    if (!chartNames || chartNames.length === 0) {
      ElMessage.warning('没有可下载的图表')
      return
    }

    const { zipName = `charts_${taskId}.zip` } = options
    
    try {
      loading.value = true
      
      // 这里可以实现ZIP打包下载
      // 目前简化为逐个下载
      for (const chartName of chartNames) {
        if (charts[chartName]) {
          await downloadChart(chartName)
          await new Promise(resolve => setTimeout(resolve, 100)) // 避免过快下载
        }
      }
      
      ElMessage.success(`完成下载 ${chartNames.length} 个图表`)
    } catch (error) {
      ElMessage.error('批量下载失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const retryFailedCharts = async () => {
    const failed = failedCharts.value
    if (failed.length === 0) {
      ElMessage.info('没有失败的图表需要重试')
      return
    }

    ElMessage.info(`开始重试 ${failed.length} 个失败的图表`)
    return loadAllCharts(failed, { force: true })
  }

  const getChartInfo = (chartName) => {
    return {
      url: charts[chartName],
      status: chartStatus[chartName],
      isLoaded: !!charts[chartName] && !chartStatus[chartName]?.error,
      isLoading: chartStatus[chartName]?.loading || false,
      error: chartStatus[chartName]?.error,
      retryCount: chartStatus[chartName]?.retryCount || 0,
      loadTime: chartStatus[chartName]?.loadTime
    }
  }

  const clearChart = (chartName) => {
    if (charts[chartName]) {
      URL.revokeObjectURL(charts[chartName])
      delete charts[chartName]
    }
    delete chartStatus[chartName]
  }

  const clearAllCharts = () => {
    Object.keys(charts).forEach(chartName => {
      if (charts[chartName]) {
        URL.revokeObjectURL(charts[chartName])
      }
    })
    
    Object.keys(charts).forEach(key => delete charts[key])
    Object.keys(chartStatus).forEach(key => delete chartStatus[key])
    
    ElMessage.success('已清空所有图表缓存')
  }

  const preloadCharts = async (chartNames, options = {}) => {
    const { priority = [], delay = 0 } = options
    
    // 优先加载重要图表
    const priorityCharts = priority.filter(name => chartNames.includes(name))
    const regularCharts = chartNames.filter(name => !priority.includes(name))
    
    const loadOrder = [...priorityCharts, ...regularCharts]
    
    for (const chartName of loadOrder) {
      try {
        await loadChart(chartName)
        if (delay > 0) {
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      } catch (error) {
        console.warn(`预加载图表失败: ${chartName}`, error)
      }
    }
  }

  const startCacheCleanup = (interval = 300000) => { // 5分钟
    if (cacheCleanupTimer) {
      clearInterval(cacheCleanupTimer)
    }
    
    cacheCleanupTimer = setInterval(() => {
      const now = Date.now()
      const maxAge = 600000 // 10分钟
      
      Object.keys(chartStatus).forEach(chartName => {
        const status = chartStatus[chartName]
        if (status?.loadTime && (now - status.loadTime) > maxAge) {
          clearChart(chartName)
        }
      })
    }, interval)
  }

  const stopCacheCleanup = () => {
    if (cacheCleanupTimer) {
      clearInterval(cacheCleanupTimer)
      cacheCleanupTimer = null
    }
  }

  // 监听 taskId 变化，清空缓存
  watch(() => taskId, (newTaskId, oldTaskId) => {
    if (newTaskId !== oldTaskId) {
      clearAllCharts()
    }
  }, { immediate: false })

  // 组件卸载时清理
  onUnmounted(() => {
    clearAllCharts()
    stopCacheCleanup()
  })

  // 返回API
  return {
    // 状态
    loading,
    error,
    charts,
    chartStatus,
    batchLoading,
    batchProgress,
    
    // 计算属性
    loadedCharts,
    failedCharts,
    loadingCharts,
    totalCharts,
    successRate,
    
    // 方法
    loadChart,
    loadAllCharts,
    refreshChart,
    refreshAllCharts,
    downloadChart,
    downloadAllCharts,
    retryFailedCharts,
    getChartInfo,
    clearChart,
    clearAllCharts,
    preloadCharts,
    startCacheCleanup,
    stopCacheCleanup
  }
}

// 图表批量操作工具
export function useChartBatch() {
  const selectedCharts = ref(new Set())
  const selectAll = ref(false)
  
  const isSelected = (chartName) => {
    return selectedCharts.value.has(chartName)
  }
  
  const toggleChart = (chartName) => {
    if (selectedCharts.value.has(chartName)) {
      selectedCharts.value.delete(chartName)
    } else {
      selectedCharts.value.add(chartName)
    }
  }
  
  const toggleAll = (chartNames) => {
    if (selectAll.value) {
      selectedCharts.value.clear()
    } else {
      chartNames.forEach(name => selectedCharts.value.add(name))
    }
    selectAll.value = !selectAll.value
  }
  
  const clearSelection = () => {
    selectedCharts.value.clear()
    selectAll.value = false
  }
  
  const getSelectedCharts = () => {
    return Array.from(selectedCharts.value)
  }
  
  const selectedCount = computed(() => {
    return selectedCharts.value.size
  })
  
  return {
    selectedCharts,
    selectAll,
    selectedCount,
    isSelected,
    toggleChart,
    toggleAll,
    clearSelection,
    getSelectedCharts
  }
}

// 图表性能监控
export function useChartPerformance() {
  const metrics = reactive({
    totalRequests: 0,
    successRequests: 0,
    failedRequests: 0,
    totalLoadTime: 0,
    averageLoadTime: 0,
    cacheHits: 0,
    cacheMisses: 0
  })
  
  const recordLoadStart = (chartName) => {
    return {
      chartName,
      startTime: performance.now()
    }
  }
  
  const recordLoadEnd = (loadRecord, success, fromCache = false) => {
    const loadTime = performance.now() - loadRecord.startTime
    
    metrics.totalRequests++
    metrics.totalLoadTime += loadTime
    metrics.averageLoadTime = metrics.totalLoadTime / metrics.totalRequests
    
    if (success) {
      metrics.successRequests++
    } else {
      metrics.failedRequests++
    }
    
    if (fromCache) {
      metrics.cacheHits++
    } else {
      metrics.cacheMisses++
    }
  }
  
  const getPerformanceReport = () => {
    const successRate = metrics.totalRequests > 0 
      ? Math.round((metrics.successRequests / metrics.totalRequests) * 100) 
      : 0
    
    const cacheHitRate = (metrics.cacheHits + metrics.cacheMisses) > 0
      ? Math.round((metrics.cacheHits / (metrics.cacheHits + metrics.cacheMisses)) * 100)
      : 0
    
    return {
      ...metrics,
      successRate,
      cacheHitRate,
      averageLoadTime: Math.round(metrics.averageLoadTime)
    }
  }
  
  const resetMetrics = () => {
    Object.keys(metrics).forEach(key => {
      metrics[key] = 0
    })
  }
  
  return {
    metrics,
    recordLoadStart,
    recordLoadEnd,
    getPerformanceReport,
    resetMetrics
  }
} 
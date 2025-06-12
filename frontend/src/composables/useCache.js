import { ref, reactive, computed, onUnmounted } from 'vue'

// LRU 缓存实现
class LRUCache {
  constructor(maxSize = 100, maxAge = 5 * 60 * 1000) { // 默认5分钟过期
    this.maxSize = maxSize
    this.maxAge = maxAge
    this.cache = new Map()
    this.accessTimes = new Map()
  }

  get(key) {
    if (!this.cache.has(key)) {
      return null
    }

    const item = this.cache.get(key)
    const now = Date.now()

    // 检查是否过期
    if (now - item.timestamp > this.maxAge) {
      this.delete(key)
      return null
    }

    // 更新访问时间
    this.accessTimes.set(key, now)
    
    // 移到最后（最近使用）
    this.cache.delete(key)
    this.cache.set(key, item)

    return item.data
  }

  set(key, data, customMaxAge) {
    const now = Date.now()
    const maxAge = customMaxAge || this.maxAge

    // 如果已存在，先删除
    if (this.cache.has(key)) {
      this.cache.delete(key)
      this.accessTimes.delete(key)
    }

    // 检查容量，删除最旧的项
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value
      this.delete(oldestKey)
    }

    // 添加新项
    this.cache.set(key, {
      data,
      timestamp: now,
      maxAge
    })
    this.accessTimes.set(key, now)
  }

  delete(key) {
    this.cache.delete(key)
    this.accessTimes.delete(key)
  }

  clear() {
    this.cache.clear()
    this.accessTimes.clear()
  }

  size() {
    return this.cache.size
  }

  keys() {
    return Array.from(this.cache.keys())
  }

  // 清理过期项
  cleanup() {
    const now = Date.now()
    const keysToDelete = []

    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.maxAge) {
        keysToDelete.push(key)
      }
    }

    keysToDelete.forEach(key => this.delete(key))
    return keysToDelete.length
  }

  // 获取缓存统计信息
  getStats() {
    const now = Date.now()
    let expiredCount = 0
    let totalSize = 0

    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.maxAge) {
        expiredCount++
      }
      
      // 估算数据大小
      totalSize += this.estimateSize(item.data)
    }

    return {
      totalItems: this.cache.size,
      expiredItems: expiredCount,
      estimatedSize: totalSize,
      maxSize: this.maxSize,
      maxAge: this.maxAge
    }
  }

  // 估算对象大小（简单实现）
  estimateSize(obj) {
    const type = typeof obj
    
    if (type === 'string') {
      return obj.length * 2 // 假设每个字符2字节
    } else if (type === 'number') {
      return 8
    } else if (type === 'boolean') {
      return 4
    } else if (obj instanceof Blob) {
      return obj.size
    } else if (obj instanceof ArrayBuffer) {
      return obj.byteLength
    } else if (Array.isArray(obj)) {
      return obj.reduce((size, item) => size + this.estimateSize(item), 0)
    } else if (type === 'object' && obj !== null) {
      return Object.values(obj).reduce((size, value) => size + this.estimateSize(value), 0)
    }
    
    return 100 // 默认估算值
  }
}

// 缓存管理组合式函数
export function useCache(options = {}) {
  const {
    maxSize = 100,
    maxAge = 5 * 60 * 1000, // 5分钟
    autoCleanup = true,
    cleanupInterval = 60 * 1000 // 1分钟清理一次
  } = options

  const cache = new LRUCache(maxSize, maxAge)
  const hitCount = ref(0)
  const missCount = ref(0)
  const cleanupTimer = ref(null)

  // 缓存统计
  const stats = computed(() => {
    const cacheStats = cache.getStats()
    const total = hitCount.value + missCount.value
    
    return {
      ...cacheStats,
      hitCount: hitCount.value,
      missCount: missCount.value,
      hitRate: total > 0 ? (hitCount.value / total * 100).toFixed(2) : 0
    }
  })

  // 获取缓存数据
  const get = (key) => {
    const data = cache.get(key)
    if (data !== null) {
      hitCount.value++
      return data
    } else {
      missCount.value++
      return null
    }
  }

  // 设置缓存数据
  const set = (key, data, customMaxAge) => {
    cache.set(key, data, customMaxAge)
  }

  // 删除缓存数据
  const remove = (key) => {
    cache.delete(key)
  }

  // 清空缓存
  const clear = () => {
    cache.clear()
    hitCount.value = 0
    missCount.value = 0
  }

  // 批量设置
  const setMultiple = (items) => {
    for (const [key, data, maxAge] of items) {
      set(key, data, maxAge)
    }
  }

  // 批量获取
  const getMultiple = (keys) => {
    const results = {}
    for (const key of keys) {
      results[key] = get(key)
    }
    return results
  }

  // 获取或设置（如果不存在则设置）
  const getOrSet = async (key, factory, customMaxAge) => {
    let data = get(key)
    
    if (data === null) {
      try {
        data = await factory()
        set(key, data, customMaxAge)
      } catch (error) {
        console.error('缓存工厂函数执行失败:', error)
        throw error
      }
    }
    
    return data
  }

  // 手动清理过期项
  const cleanup = () => {
    const deletedCount = cache.cleanup()
    return deletedCount
  }

  // 启动自动清理
  const startAutoCleanup = () => {
    if (autoCleanup && !cleanupTimer.value) {
      cleanupTimer.value = setInterval(() => {
        cleanup()
      }, cleanupInterval)
    }
  }

  // 停止自动清理
  const stopAutoCleanup = () => {
    if (cleanupTimer.value) {
      clearInterval(cleanupTimer.value)
      cleanupTimer.value = null
    }
  }

  // 预热缓存
  const warmup = async (entries) => {
    const promises = entries.map(async ({ key, factory, maxAge }) => {
      try {
        const data = await factory()
        set(key, data, maxAge)
        return { key, success: true }
      } catch (error) {
        console.error(`预热缓存失败: ${key}`, error)
        return { key, success: false, error }
      }
    })

    return Promise.allSettled(promises)
  }

  // 启动自动清理
  startAutoCleanup()

  // 组件卸载时清理
  onUnmounted(() => {
    stopAutoCleanup()
  })

  return {
    get,
    set,
    remove,
    clear,
    setMultiple,
    getMultiple,
    getOrSet,
    cleanup,
    warmup,
    stats,
    startAutoCleanup,
    stopAutoCleanup
  }
}

// 图表缓存专用
export function useChartCache(taskId, options = {}) {
  const {
    maxCharts = 50,
    chartMaxAge = 10 * 60 * 1000, // 图表缓存10分钟
    ...cacheOptions
  } = options

  const cache = useCache({
    maxSize: maxCharts,
    maxAge: chartMaxAge,
    ...cacheOptions
  })

  // 生成图表缓存键
  const getChartKey = (chartName) => {
    return `chart:${taskId}:${chartName}`
  }

  // 缓存图表
  const cacheChart = (chartName, chartData) => {
    const key = getChartKey(chartName)
    cache.set(key, chartData)
  }

  // 获取图表
  const getChart = (chartName) => {
    const key = getChartKey(chartName)
    return cache.get(key)
  }

  // 移除图表
  const removeChart = (chartName) => {
    const key = getChartKey(chartName)
    cache.remove(key)
  }

  // 批量缓存图表
  const cacheCharts = (chartsData) => {
    const items = Object.entries(chartsData).map(([chartName, data]) => [
      getChartKey(chartName),
      data,
      chartMaxAge
    ])
    cache.setMultiple(items)
  }

  // 获取任务的所有图表
  const getTaskCharts = () => {
    const prefix = `chart:${taskId}:`
    const charts = {}
    
    for (const key of cache.stats.value.keys || []) {
      if (key.startsWith(prefix)) {
        const chartName = key.replace(prefix, '')
        const data = cache.get(key)
        if (data) {
          charts[chartName] = data
        }
      }
    }
    
    return charts
  }

  // 清理任务图表
  const clearTaskCharts = () => {
    const prefix = `chart:${taskId}:`
    const keysToRemove = []
    
    for (const key of cache.stats.value.keys || []) {
      if (key.startsWith(prefix)) {
        keysToRemove.push(key)
      }
    }
    
    keysToRemove.forEach(key => cache.remove(key))
  }

  // 预加载图表
  const preloadCharts = async (chartNames, chartLoader) => {
    const entries = chartNames.map(chartName => ({
      key: getChartKey(chartName),
      factory: () => chartLoader(chartName),
      maxAge: chartMaxAge
    }))

    return cache.warmup(entries)
  }

  return {
    ...cache,
    cacheChart,
    getChart,
    removeChart,
    cacheCharts,
    getTaskCharts,
    clearTaskCharts,
    preloadCharts
  }
}

// 分析结果缓存
export function useResultsCache(options = {}) {
  const {
    maxResults = 20,
    resultMaxAge = 30 * 60 * 1000, // 结果缓存30分钟
    ...cacheOptions
  } = options

  const cache = useCache({
    maxSize: maxResults,
    maxAge: resultMaxAge,
    ...cacheOptions
  })

  // 缓存分析结果
  const cacheResults = (taskId, results) => {
    const key = `results:${taskId}`
    cache.set(key, results)
  }

  // 获取分析结果
  const getResults = (taskId) => {
    const key = `results:${taskId}`
    return cache.get(key)
  }

  // 缓存AI分析
  const cacheAIAnalysis = (taskId, analysis) => {
    const key = `ai:${taskId}`
    cache.set(key, analysis)
  }

  // 获取AI分析
  const getAIAnalysis = (taskId) => {
    const key = `ai:${taskId}`
    return cache.get(key)
  }

  // 移除任务相关缓存
  const removeTaskCache = (taskId) => {
    cache.remove(`results:${taskId}`)
    cache.remove(`ai:${taskId}`)
  }

  return {
    ...cache,
    cacheResults,
    getResults,
    cacheAIAnalysis,
    getAIAnalysis,
    removeTaskCache
  }
}

// 内存监控
export function useMemoryMonitor() {
  const memoryInfo = ref({})
  const isSupported = ref(false)

  const updateMemoryInfo = () => {
    if (performance.memory) {
      isSupported.value = true
      memoryInfo.value = {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
        usagePercent: (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit * 100).toFixed(2)
      }
    } else {
      isSupported.value = false
    }
  }

  const startMonitoring = (interval = 5000) => {
    updateMemoryInfo()
    return setInterval(updateMemoryInfo, interval)
  }

  const getMemoryPressure = () => {
    if (!isSupported.value) return 'unknown'
    
    const usage = parseFloat(memoryInfo.value.usagePercent)
    if (usage < 50) return 'low'
    if (usage < 80) return 'medium'
    return 'high'
  }

  return {
    memoryInfo,
    isSupported,
    updateMemoryInfo,
    startMonitoring,
    getMemoryPressure
  }
} 
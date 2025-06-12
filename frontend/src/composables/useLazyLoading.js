import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// 懒加载观察器
export function useLazyLoading(options = {}) {
  const {
    threshold = 0.1,
    rootMargin = '50px',
    triggerOnce = true
  } = options

  const isIntersecting = ref(false)
  const targetRef = ref(null)
  let observer = null

  const startObserving = () => {
    if (!targetRef.value || !window.IntersectionObserver) {
      // 如果不支持 IntersectionObserver，则立即触发
      isIntersecting.value = true
      return
    }

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            isIntersecting.value = true
            
            if (triggerOnce && observer) {
              observer.unobserve(entry.target)
            }
          } else if (!triggerOnce) {
            isIntersecting.value = false
          }
        })
      },
      {
        threshold,
        rootMargin
      }
    )

    observer.observe(targetRef.value)
  }

  const stopObserving = () => {
    if (observer && targetRef.value) {
      observer.unobserve(targetRef.value)
      observer.disconnect()
      observer = null
    }
  }

  onMounted(() => {
    startObserving()
  })

  onUnmounted(() => {
    stopObserving()
  })

  return {
    targetRef,
    isIntersecting,
    startObserving,
    stopObserving
  }
}

// 图表懒加载
export function useChartLazyLoading(chartLoader, options = {}) {
  const { 
    placeholder = null,
    errorRetry = true,
    retryDelay = 1000,
    maxRetries = 3
  } = options

  const isLoading = ref(false)
  const isLoaded = ref(false)
  const error = ref(null)
  const retryCount = ref(0)
  const chartData = ref(null)

  const { targetRef, isIntersecting } = useLazyLoading({
    threshold: 0.1,
    rootMargin: '100px',
    triggerOnce: true
  })

  // 监听可视状态变化
  watch(isIntersecting, (visible) => {
    if (visible && !isLoaded.value && !isLoading.value) {
      loadChart()
    }
  })

  const loadChart = async () => {
    if (isLoading.value || isLoaded.value) return

    isLoading.value = true
    error.value = null

    try {
      const result = await chartLoader()
      chartData.value = result
      isLoaded.value = true
      retryCount.value = 0
    } catch (err) {
      error.value = err
      
      if (errorRetry && retryCount.value < maxRetries) {
        retryCount.value++
        setTimeout(() => {
          if (!isLoaded.value) {
            loadChart()
          }
        }, retryDelay * retryCount.value)
      }
    } finally {
      isLoading.value = false
    }
  }

  const retry = () => {
    retryCount.value = 0
    error.value = null
    loadChart()
  }

  const reset = () => {
    isLoading.value = false
    isLoaded.value = false
    error.value = null
    retryCount.value = 0
    chartData.value = null
  }

  return {
    targetRef,
    isLoading,
    isLoaded,
    error,
    chartData,
    retryCount,
    retry,
    reset,
    loadChart
  }
}

// 列表项懒加载
export function useListLazyLoading(items = [], batchSize = 20) {
  const visibleItems = ref([])
  const hasMore = ref(true)
  const isLoadingMore = ref(false)

  // 初始化
  const initializeItems = () => {
    const initialBatch = items.slice(0, batchSize)
    visibleItems.value = initialBatch
    hasMore.value = items.length > batchSize
  }

  // 加载更多
  const loadMore = () => {
    if (isLoadingMore.value || !hasMore.value) return

    isLoadingMore.value = true

    // 模拟异步加载
    setTimeout(() => {
      const currentLength = visibleItems.value.length
      const nextBatch = items.slice(currentLength, currentLength + batchSize)
      
      visibleItems.value.push(...nextBatch)
      hasMore.value = visibleItems.value.length < items.length
      isLoadingMore.value = false
    }, 300)
  }

  // 重置
  const reset = () => {
    visibleItems.value = []
    hasMore.value = true
    isLoadingMore.value = false
    initializeItems()
  }

  // 监听数据变化
  watch(() => items, () => {
    reset()
  }, { immediate: true })

  return {
    visibleItems,
    hasMore,
    isLoadingMore,
    loadMore,
    reset
  }
}

// 虚拟滚动
export function useVirtualScroll(options = {}) {
  const {
    itemHeight = 100,
    containerHeight = 400,
    overscan = 5
  } = options

  const scrollTop = ref(0)
  const containerRef = ref(null)

  const visibleRange = computed(() => {
    const start = Math.floor(scrollTop.value / itemHeight)
    const end = Math.min(
      start + Math.ceil(containerHeight / itemHeight),
      items.value.length
    )

    return {
      start: Math.max(0, start - overscan),
      end: Math.min(items.value.length, end + overscan)
    }
  })

  const visibleItems = computed(() => {
    const { start, end } = visibleRange.value
    return items.value.slice(start, end).map((item, index) => ({
      ...item,
      index: start + index
    }))
  })

  const totalHeight = computed(() => {
    return items.value.length * itemHeight
  })

  const offsetY = computed(() => {
    return visibleRange.value.start * itemHeight
  })

  const handleScroll = (event) => {
    scrollTop.value = event.target.scrollTop
  }

  return {
    containerRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  }
}

// 预加载管理
export function usePreloader() {
  const preloadQueue = ref(new Map())
  const preloadCache = ref(new Map())
  const isPreloading = ref(false)

  // 添加预加载任务
  const addPreloadTask = (key, loader, priority = 0) => {
    if (preloadCache.value.has(key)) {
      return Promise.resolve(preloadCache.value.get(key))
    }

    if (preloadQueue.value.has(key)) {
      return preloadQueue.value.get(key).promise
    }

    const promise = new Promise(async (resolve, reject) => {
      try {
        const result = await loader()
        preloadCache.value.set(key, result)
        preloadQueue.value.delete(key)
        resolve(result)
      } catch (error) {
        preloadQueue.value.delete(key)
        reject(error)
      }
    })

    preloadQueue.value.set(key, { promise, priority })
    return promise
  }

  // 执行预加载
  const startPreloading = async (concurrency = 3) => {
    if (isPreloading.value) return

    isPreloading.value = true

    try {
      const tasks = Array.from(preloadQueue.value.entries())
        .sort(([, a], [, b]) => b.priority - a.priority)
        .map(([key, task]) => task.promise)

      // 限制并发数
      for (let i = 0; i < tasks.length; i += concurrency) {
        const batch = tasks.slice(i, i + concurrency)
        await Promise.allSettled(batch)
      }
    } finally {
      isPreloading.value = false
    }
  }

  // 获取缓存数据
  const getCachedData = (key) => {
    return preloadCache.value.get(key)
  }

  // 清理缓存
  const clearCache = (keys) => {
    if (keys) {
      keys.forEach(key => preloadCache.value.delete(key))
    } else {
      preloadCache.value.clear()
    }
  }

  // 获取缓存统计
  const getCacheStats = () => {
    return {
      cacheSize: preloadCache.value.size,
      queueSize: preloadQueue.value.size,
      isPreloading: isPreloading.value
    }
  }

  return {
    addPreloadTask,
    startPreloading,
    getCachedData,
    clearCache,
    getCacheStats,
    isPreloading
  }
} 
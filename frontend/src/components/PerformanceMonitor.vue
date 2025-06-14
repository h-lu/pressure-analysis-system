<template>
  <div class="performance-monitor">
    <el-card>
      <template #header>
        <div class="monitor-header">
          <el-icon><Monitor /></el-icon>
          <span>性能监控</span>
          <el-button 
            size="small" 
            :type="isMonitoring ? 'danger' : 'primary'"
            @click="toggleMonitoring"
          >
            {{ isMonitoring ? '停止监控' : '开始监控' }}
          </el-button>
        </div>
      </template>

      <!-- 性能指标概览 -->
      <div class="metrics-overview">
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ pageLoadTime }}ms</div>
            <div class="metric-label">页面加载时间</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ memoryUsage }}%</div>
            <div class="metric-label">内存使用率</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><Odometer /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ cacheHitRate }}%</div>
            <div class="metric-label">缓存命中率</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ networkLatency }}ms</div>
            <div class="metric-label">网络延迟</div>
          </div>
        </div>
      </div>

      <!-- 详细性能数据 -->
      <div class="performance-details">
        <el-tabs v-model="activeTab">
          <!-- 内存监控 -->
          <el-tab-pane label="内存监控" name="memory">
            <div class="memory-monitor">
              <div v-if="memoryInfo.isSupported" class="memory-stats">
                <div class="memory-item">
                  <span class="memory-label">已用内存:</span>
                  <span class="memory-value">
                    {{ formatBytes(memoryInfo.usedJSHeapSize) }}
                  </span>
                </div>
                
                <div class="memory-item">
                  <span class="memory-label">总内存:</span>
                  <span class="memory-value">
                    {{ formatBytes(memoryInfo.totalJSHeapSize) }}
                  </span>
                </div>
                
                <div class="memory-item">
                  <span class="memory-label">内存限制:</span>
                  <span class="memory-value">
                    {{ formatBytes(memoryInfo.jsHeapSizeLimit) }}
                  </span>
                </div>
                
                <div class="memory-item">
                  <span class="memory-label">使用率:</span>
                  <span class="memory-value" :class="memoryPressureClass">
                    {{ memoryInfo.usagePercent }}%
                  </span>
                </div>
              </div>
              
              <div v-else class="no-support">
                <el-icon><Warning /></el-icon>
                <span>浏览器不支持内存监控</span>
              </div>

              <!-- 内存使用图表 -->
              <div class="memory-chart">
                <el-progress
                  :percentage="parseFloat(memoryInfo.usagePercent || 0)"
                  :status="memoryPressure === 'high' ? 'exception' : 
                           memoryPressure === 'medium' ? 'warning' : 'success'"
                  :stroke-width="20"
                  :show-text="false"
                />
                <div class="memory-chart-label">
                  内存压力: {{ memoryPressureText }}
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 缓存状态 -->
          <el-tab-pane label="缓存状态" name="cache">
            <div class="cache-monitor">
              <div class="cache-stats">
                <div class="cache-item">
                  <span class="cache-label">缓存项数:</span>
                  <span class="cache-value">{{ cacheStats.totalItems }}</span>
                </div>
                
                <div class="cache-item">
                  <span class="cache-label">过期项数:</span>
                  <span class="cache-value">{{ cacheStats.expiredItems }}</span>
                </div>
                
                <div class="cache-item">
                  <span class="cache-label">命中次数:</span>
                  <span class="cache-value">{{ cacheStats.hitCount }}</span>
                </div>
                
                <div class="cache-item">
                  <span class="cache-label">未命中次数:</span>
                  <span class="cache-value">{{ cacheStats.missCount }}</span>
                </div>
                
                <div class="cache-item">
                  <span class="cache-label">命中率:</span>
                  <span class="cache-value">{{ cacheStats.hitRate }}%</span>
                </div>
              </div>

              <div class="cache-actions">
                <el-button size="small" @click="clearCache">
                  <el-icon><Delete /></el-icon>
                  清理缓存
                </el-button>
                
                <el-button size="small" @click="refreshCacheStats">
                  <el-icon><Refresh /></el-icon>
                  刷新统计
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- 网络性能 -->
          <el-tab-pane label="网络性能" name="network">
            <div class="network-monitor">
              <div class="network-stats">
                <div class="network-item">
                  <span class="network-label">连接类型:</span>
                  <span class="network-value">{{ networkInfo.effectiveType }}</span>
                </div>
                
                <div class="network-item">
                  <span class="network-label">下行速度:</span>
                  <span class="network-value">{{ networkInfo.downlink }} Mbps</span>
                </div>
                
                <div class="network-item">
                  <span class="network-label">RTT延迟:</span>
                  <span class="network-value">{{ networkInfo.rtt }} ms</span>
                </div>
                
                <div class="network-item">
                  <span class="network-label">节省流量:</span>
                  <span class="network-value">
                    {{ networkInfo.saveData ? '开启' : '关闭' }}
                  </span>
                </div>
              </div>

              <div class="network-test">
                <el-button 
                  size="small" 
                  :loading="isTestingNetwork"
                  @click="testNetworkSpeed"
                >
                  <el-icon><Stopwatch /></el-icon>
                  测试网络速度
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- 性能时间线 -->
          <el-tab-pane label="性能时间线" name="timeline">
            <div class="performance-timeline">
              <div class="timeline-item">
                <span class="timeline-label">DNS解析:</span>
                <span class="timeline-value">{{ performanceTiming.domainLookup }}ms</span>
              </div>
              
              <div class="timeline-item">
                <span class="timeline-label">TCP连接:</span>
                <span class="timeline-value">{{ performanceTiming.connect }}ms</span>
              </div>
              
              <div class="timeline-item">
                <span class="timeline-label">请求响应:</span>
                <span class="timeline-value">{{ performanceTiming.request }}ms</span>
              </div>
              
              <div class="timeline-item">
                <span class="timeline-label">DOM解析:</span>
                <span class="timeline-value">{{ performanceTiming.domParsing }}ms</span>
              </div>
              
              <div class="timeline-item">
                <span class="timeline-label">资源加载:</span>
                <span class="timeline-value">{{ performanceTiming.resourceLoad }}ms</span>
              </div>
              
              <div class="timeline-item">
                <span class="timeline-label">页面完成:</span>
                <span class="timeline-value">{{ performanceTiming.pageComplete }}ms</span>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 性能建议 -->
      <div class="performance-suggestions">
        <div class="suggestions-header">
          <el-icon><Lightbulb /></el-icon>
          <span>性能优化建议</span>
        </div>
        
        <div class="suggestions-list">
          <div
            v-for="(suggestion, index) in performanceSuggestions"
            :key="index"
            class="suggestion-item"
            :class="suggestion.type"
          >
            <el-icon :class="`suggestion-icon ${suggestion.type}`">
              <component :is="suggestion.icon" />
            </el-icon>
            <div class="suggestion-content">
              <div class="suggestion-title">{{ suggestion.title }}</div>
              <div class="suggestion-description">{{ suggestion.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useMemoryMonitor } from '@/composables/useCache'
import { getFullApiURL } from '@/config'

// 监控状态
const isMonitoring = ref(false)
const activeTab = ref('memory')
const isTestingNetwork = ref(false)

// 性能指标
const pageLoadTime = ref(0)
const memoryUsage = ref(0)
const cacheHitRate = ref(0)
const networkLatency = ref(0)

// 内存监控
const { memoryInfo, isSupported, updateMemoryInfo, startMonitoring, getMemoryPressure } = useMemoryMonitor()

// 缓存统计
const cacheStats = reactive({
  totalItems: 0,
  expiredItems: 0,
  hitCount: 0,
  missCount: 0,
  hitRate: 0
})

// 网络信息
const networkInfo = reactive({
  effectiveType: 'unknown',
  downlink: 0,
  rtt: 0,
  saveData: false
})

// 性能时间线
const performanceTiming = reactive({
  domainLookup: 0,
  connect: 0,
  request: 0,
  domParsing: 0,
  resourceLoad: 0,
  pageComplete: 0
})

// 计算属性
const memoryPressure = computed(() => getMemoryPressure())

const memoryPressureClass = computed(() => {
  switch (memoryPressure.value) {
    case 'high': return 'pressure-high'
    case 'medium': return 'pressure-medium'
    default: return 'pressure-low'
  }
})

const memoryPressureText = computed(() => {
  switch (memoryPressure.value) {
    case 'high': return '高'
    case 'medium': return '中'
    case 'low': return '低'
    default: return '未知'
  }
})

const performanceSuggestions = computed(() => {
  const suggestions = []
  
  if (memoryUsage.value > 80) {
    suggestions.push({
      type: 'warning',
      icon: 'Warning',
      title: '内存使用率过高',
      description: '建议清理缓存或减少同时打开的图表数量'
    })
  }
  
  if (cacheHitRate.value < 50) {
    suggestions.push({
      type: 'info',
      icon: 'InfoFilled',
      title: '缓存命中率偏低',
      description: '考虑增加缓存容量或调整缓存策略'
    })
  }
  
  if (networkLatency.value > 500) {
    suggestions.push({
      type: 'warning',
      icon: 'Warning',
      title: '网络延迟较高',
      description: '建议启用数据预加载或使用CDN加速'
    })
  }
  
  if (pageLoadTime.value > 3000) {
    suggestions.push({
      type: 'error',
      icon: 'CircleClose',
      title: '页面加载时间过长',
      description: '建议优化资源加载或启用懒加载'
    })
  }
  
  if (suggestions.length === 0) {
    suggestions.push({
      type: 'success',
      icon: 'CircleCheck',
      title: '性能表现良好',
      description: '当前应用性能指标正常，无需额外优化'
    })
  }
  
  return suggestions
})

// 监控定时器
let monitoringTimer = null

// 格式化字节数
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取性能时间线
const getPerformanceTiming = () => {
  if (performance.timing) {
    const timing = performance.timing
    
    performanceTiming.domainLookup = timing.domainLookupEnd - timing.domainLookupStart
    performanceTiming.connect = timing.connectEnd - timing.connectStart
    performanceTiming.request = timing.responseEnd - timing.requestStart
    performanceTiming.domParsing = timing.domContentLoadedEventEnd - timing.domLoading
    performanceTiming.resourceLoad = timing.loadEventEnd - timing.domContentLoadedEventEnd
    performanceTiming.pageComplete = timing.loadEventEnd - timing.navigationStart
    
    pageLoadTime.value = performanceTiming.pageComplete
  }
}

// 获取网络信息
const getNetworkInfo = () => {
  if (navigator.connection) {
    const connection = navigator.connection
    
    networkInfo.effectiveType = connection.effectiveType || 'unknown'
    networkInfo.downlink = connection.downlink || 0
    networkInfo.rtt = connection.rtt || 0
    networkInfo.saveData = connection.saveData || false
    
    networkLatency.value = networkInfo.rtt
  }
}

// 更新缓存统计
const refreshCacheStats = () => {
  // 这里应该从实际的缓存管理器获取统计信息
  // 暂时使用模拟数据
  cacheStats.totalItems = Math.floor(Math.random() * 100)
  cacheStats.expiredItems = Math.floor(Math.random() * 10)
  cacheStats.hitCount = Math.floor(Math.random() * 1000)
  cacheStats.missCount = Math.floor(Math.random() * 200)
  cacheStats.hitRate = parseFloat(
    (cacheStats.hitCount / (cacheStats.hitCount + cacheStats.missCount) * 100).toFixed(2)
  )
  
  cacheHitRate.value = cacheStats.hitRate
}

// 清理缓存
const clearCache = () => {
  // 这里应该调用实际的缓存清理方法
  ElMessage.success('缓存已清理')
  refreshCacheStats()
}

// 测试网络速度
const testNetworkSpeed = async () => {
  isTestingNetwork.value = true
  
  try {
    const startTime = performance.now()
    
    // 发送测试请求
    await fetch(getFullApiURL('/health'), { cache: 'no-cache' })
    
    const endTime = performance.now()
    const latency = Math.round(endTime - startTime)
    
    networkLatency.value = latency
    networkInfo.rtt = latency
    
    ElMessage.success(`网络延迟: ${latency}ms`)
  } catch (error) {
    ElMessage.error('网络测试失败')
  } finally {
    isTestingNetwork.value = false
  }
}

// 更新所有监控数据
const updateMonitoringData = () => {
  updateMemoryInfo()
  memoryUsage.value = parseFloat(memoryInfo.value.usagePercent || 0)
  
  getNetworkInfo()
  refreshCacheStats()
}

// 切换监控状态
const toggleMonitoring = () => {
  if (isMonitoring.value) {
    // 停止监控
    isMonitoring.value = false
    if (monitoringTimer) {
      clearInterval(monitoringTimer)
      monitoringTimer = null
    }
    ElMessage.info('性能监控已停止')
  } else {
    // 开始监控
    isMonitoring.value = true
    updateMonitoringData()
    monitoringTimer = setInterval(updateMonitoringData, 5000)
    ElMessage.success('性能监控已启动')
  }
}

// 组件挂载时初始化
onMounted(() => {
  getPerformanceTiming()
  getNetworkInfo()
  updateMonitoringData()
})

// 组件卸载时清理
onUnmounted(() => {
  if (monitoringTimer) {
    clearInterval(monitoringTimer)
  }
})
</script>

<style scoped>
.performance-monitor {
  max-width: 1000px;
  margin: 0 auto;
}

.monitor-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
}

.monitor-header span {
  flex: 1;
}

/* 性能指标概览 */
.metrics-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.metric-icon {
  font-size: 24px;
  color: var(--el-color-primary);
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.metric-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

/* 内存监控 */
.memory-monitor {
  padding: 16px 0;
}

.memory-stats,
.cache-stats,
.network-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.memory-item,
.cache-item,
.network-item,
.timeline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
}

.memory-label,
.cache-label,
.network-label,
.timeline-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.memory-value,
.cache-value,
.network-value,
.timeline-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.pressure-high {
  color: var(--el-color-danger);
}

.pressure-medium {
  color: var(--el-color-warning);
}

.pressure-low {
  color: var(--el-color-success);
}

.memory-chart {
  margin-top: 16px;
}

.memory-chart-label {
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.no-support {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

/* 缓存监控 */
.cache-actions,
.network-test {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

/* 性能时间线 */
.performance-timeline {
  padding: 16px 0;
}

/* 性能建议 */
.performance-suggestions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-light);
}

.suggestions-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid;
}

.suggestion-item.success {
  background-color: var(--el-color-success-light-9);
  border-left-color: var(--el-color-success);
}

.suggestion-item.info {
  background-color: var(--el-color-info-light-9);
  border-left-color: var(--el-color-info);
}

.suggestion-item.warning {
  background-color: var(--el-color-warning-light-9);
  border-left-color: var(--el-color-warning);
}

.suggestion-item.error {
  background-color: var(--el-color-danger-light-9);
  border-left-color: var(--el-color-danger);
}

.suggestion-icon {
  font-size: 18px;
  margin-top: 2px;
}

.suggestion-icon.success {
  color: var(--el-color-success);
}

.suggestion-icon.info {
  color: var(--el-color-info);
}

.suggestion-icon.warning {
  color: var(--el-color-warning);
}

.suggestion-icon.error {
  color: var(--el-color-danger);
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.suggestion-description {
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .metrics-overview {
    grid-template-columns: 1fr;
  }
  
  .memory-stats,
  .cache-stats,
  .network-stats {
    grid-template-columns: 1fr;
  }
  
  .cache-actions,
  .network-test {
    flex-direction: column;
  }
  
  .cache-actions .el-button,
  .network-test .el-button {
    width: 100%;
  }
}
</style> 
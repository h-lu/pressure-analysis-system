<template>
  <el-card class="chart-container" :class="containerClass">
    <template #header>
      <div class="chart-header">
        <div class="chart-title-area">
          <span class="chart-title">{{ displayTitle }}</span>
          <el-tag v-if="chartConfig?.complexity" :type="complexityType" size="small">
            {{ complexityText }}
          </el-tag>
        </div>
        <div class="chart-actions">
          <el-button 
            size="small" 
            :icon="Refresh" 
            circle 
            @click="reloadChart"
            :loading="loading"
            title="重新加载"
          />
          <el-button 
            size="small" 
            :icon="Download" 
            circle 
            @click="downloadChart"
            :disabled="!chartUrl"
            title="下载图表"
          />
          <el-button 
            size="small" 
            :icon="FullScreen" 
            circle 
            @click="viewFullscreen"
            :disabled="!chartUrl"
            title="全屏查看"
          />
        </div>
      </div>
    </template>
    
    <div class="chart-content" :style="contentStyle">
      <!-- 加载状态 -->
      <div v-if="loading" class="chart-loading">
        <el-icon class="is-loading loading-icon"><Loading /></el-icon>
        <span class="loading-text">{{ loadingText }}</span>
        <el-progress 
          v-if="loadingProgress > 0" 
          :percentage="loadingProgress" 
          :show-text="false"
          :stroke-width="4"
          class="loading-progress"
        />
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="chart-error">
        <el-icon class="error-icon"><Warning /></el-icon>
        <span class="error-message">{{ error.message || '图表加载失败' }}</span>
        <div class="error-actions">
          <el-button size="small" @click="reloadChart">重试</el-button>
          <el-button size="small" type="info" @click="showErrorDetails">详情</el-button>
        </div>
      </div>
      
      <!-- 图表显示 -->
      <div v-else-if="chartUrl" class="chart-display">
        <img 
          :src="chartUrl" 
          :alt="chartName"
          class="chart-image"
          @click="showLightbox"
          @load="onImageLoad"
          @error="onImageError"
        />
        
        <!-- 图表信息浮层 -->
        <div v-if="showInfo" class="chart-info-overlay">
          <div class="chart-info">
            <h4>{{ displayTitle }}</h4>
            <p v-if="chartConfig?.description" class="chart-description">
              {{ chartConfig.description }}
            </p>
            <div v-if="chartConfig?.insights" class="chart-insights">
              <h5>关键洞察：</h5>
              <ul>
                <li v-for="insight in chartConfig.insights" :key="insight">
                  {{ insight }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 占位符 -->
      <div v-else class="chart-placeholder">
        <el-icon class="placeholder-icon"><Picture /></el-icon>
        <span class="placeholder-text">暂无图表数据</span>
        <el-button size="small" @click="reloadChart">加载图表</el-button>
      </div>
    </div>

    <!-- 图表信息 -->
    <template #footer v-if="chartConfig">
      <div class="chart-footer">
        <div class="chart-meta">
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ formatLoadTime }}
          </span>
          <span v-if="imageSize" class="meta-item">
            <el-icon><Document /></el-icon>
            {{ imageSize }}
          </span>
        </div>
        <div class="chart-tags">
          <el-tag 
            v-for="tag in chartConfig.keywords" 
            :key="tag" 
            size="small" 
            effect="plain"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </template>
  </el-card>

  <!-- 灯箱模态框 -->
  <el-dialog
    v-model="lightboxVisible"
    :title="displayTitle"
    width="90%"
    :show-close="true"
    destroy-on-close
    class="chart-lightbox"
  >
    <div class="lightbox-content">
      <img 
        v-if="chartUrl" 
        :src="chartUrl" 
        :alt="chartName"
        class="lightbox-image"
      />
    </div>
    <template #footer>
      <div class="lightbox-actions">
        <el-button @click="downloadChart">
          <el-icon><Download /></el-icon>
          下载图表
        </el-button>
        <el-button @click="lightboxVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Download, 
  FullScreen, 
  Loading, 
  Warning, 
  Picture,
  Clock,
  Document
} from '@element-plus/icons-vue'
import { useSpecificErrorHandler } from '@/composables/useSpecificErrorHandler'

const props = defineProps({
  chartName: {
    type: String,
    required: true
  },
  chartUrl: {
    type: String,
    default: ''
  },
  taskId: {
    type: String,
    required: true
  },
  chartConfig: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: [String, Number],
    default: 300
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['reload', 'download', 'error'])

const { handleSpecificError } = useSpecificErrorHandler()

// 响应式数据
const lightboxVisible = ref(false)
const showInfo = ref(false)
const loadingProgress = ref(0)
const imageSize = ref('')
const loadTime = ref(null)

// 计算属性
const displayTitle = computed(() => {
  const chineseNames = {
    'force_time_series': '力值时间序列图',
    'force_distribution': '力值分布图', 
    'force_boxplot': '力值箱线图',
    'absolute_deviation_boxplot': '绝对偏差箱线图',
    'percentage_deviation_boxplot': '百分比偏差箱线图',
    'interactive_3d_scatter': '交互式3D散点图',
    'scatter_matrix': '散点矩阵图',
    'correlation_matrix': '相关性矩阵图',
    'shewhart_control': 'Shewhart控制图',
    'moving_average': '移动平均控制图',
    'xbar_r_control': 'X-R控制图',
    'cusum_control': 'CUSUM控制图',
    'ewma_control': 'EWMA控制图',
    'imr_control': 'IMR控制图',
    'run_chart': '趋势图',
    'process_capability': '过程能力分析',
    'pareto_chart': '帕雷托图',
    'residual_analysis': '残差分析图',
    'qq_normality': 'Q-Q正态性检验图',
    'radar_chart': '雷达图',
    'heatmap': '热力图',
    'success_rate_trend': '成功率趋势图',
    'capability_index': '能力指数图',
    'quality_dashboard': '质量仪表盘',
    'waterfall_chart': '瀑布图',
    'spatial_clustering': '空间聚类图',
    'parallel_coordinates': '平行坐标图',
    'xy_heatmap': 'XY位置热力图',
    'projection_2d': '2D投影图',
    'position_anomaly_heatmap': '位置异常热力图',
    'spatial_density': '空间密度图',
    'multivariate_relations': '多元关系图',
    'anomaly_patterns': '异常模式图',
    'quality_distribution_map': '质量分布图',
    'comprehensive_assessment': '综合评估图'
  }
  return chineseNames[props.chartName] || props.chartConfig?.title || props.chartName
})

const complexityType = computed(() => {
  if (!props.chartConfig?.complexity) return 'info'
  switch (props.chartConfig.complexity) {
    case 'basic': return 'success'
    case 'intermediate': return 'warning' 
    case 'advanced': return 'danger'
    default: return 'info'
  }
})

const complexityText = computed(() => {
  if (!props.chartConfig?.complexity) return ''
  switch (props.chartConfig.complexity) {
    case 'basic': return '基础'
    case 'intermediate': return '中级'
    case 'advanced': return '高级'
    default: return ''
  }
})

const containerClass = computed(() => ({
  'chart-loading-state': props.loading,
  'chart-error-state': props.error,
  'chart-ready-state': props.chartUrl && !props.loading && !props.error
}))

const contentStyle = computed(() => ({
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  minHeight: '200px'
}))

const loadingText = computed(() => {
  if (loadingProgress.value > 0) {
    return `加载中... ${loadingProgress.value}%`
  }
  return '正在生成图表...'
})

const formatLoadTime = computed(() => {
  if (!loadTime.value) return '未知'
  return `${loadTime.value}ms`
})

// 方法
const reloadChart = async () => {
  loadTime.value = null
  const startTime = Date.now()
  
  try {
    emit('reload', props.chartName)
  } catch (error) {
    await handleSpecificError(error, '图表重新加载')
    emit('error', error)
  } finally {
    loadTime.value = Date.now() - startTime
  }
}

const downloadChart = async () => {
  if (!props.chartUrl) {
    ElMessage.warning('图表未加载完成')
    return
  }

  try {
    // 创建临时链接下载
    const link = document.createElement('a')
    link.href = props.chartUrl
    link.download = `${displayTitle.value}_${props.taskId}.png`
    link.click()
    
    ElMessage.success('图表下载成功')
    emit('download', props.chartName)
  } catch (error) {
    ElMessage.error('图表下载失败')
    await handleSpecificError(error, '图表下载')
  }
}

const viewFullscreen = () => {
  if (!props.chartUrl) {
    ElMessage.warning('图表未加载完成')
    return
  }
  lightboxVisible.value = true
}

const showLightbox = () => {
  lightboxVisible.value = true
}

const showErrorDetails = () => {
  if (!props.error) return
  
  ElMessageBox.alert(
    `错误类型: ${props.error.type || '未知'}\n错误信息: ${props.error.message || '未知错误'}\n发生时间: ${props.error.timestamp || '未知'}`,
    '错误详情',
    {
      confirmButtonText: '确定',
      type: 'error'
    }
  )
}

const onImageLoad = (event) => {
  const img = event.target
  const sizeKB = Math.round((img.naturalWidth * img.naturalHeight * 4) / 1024) // 估算大小
  imageSize.value = `${img.naturalWidth}x${img.naturalHeight} (~${sizeKB}KB)`
  
  if (!loadTime.value) {
    loadTime.value = 'unknown'
  }
}

const onImageError = (event) => {
  const error = new Error('图片加载失败')
  error.type = 'IMAGE_LOAD_ERROR'
  error.timestamp = new Date().toISOString()
  
  emit('error', error)
}

// 监听器
watch(() => props.loading, (newLoading) => {
  if (newLoading) {
    // 模拟加载进度
    loadingProgress.value = 0
    const interval = setInterval(() => {
      loadingProgress.value += Math.random() * 20
      if (loadingProgress.value >= 90) {
        clearInterval(interval)
      }
    }, 500)
    
    // 5秒后停止进度条
    setTimeout(() => {
      clearInterval(interval)
      if (newLoading) {
        loadingProgress.value = 95
      }
    }, 5000)
  } else {
    loadingProgress.value = 100
    setTimeout(() => {
      loadingProgress.value = 0
    }, 500)
  }
})
</script>

<style scoped>
.chart-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.chart-container.chart-loading-state {
  opacity: 0.8;
}

.chart-container.chart-error-state {
  border-color: var(--el-color-danger-light-5);
}

.chart-container.chart-ready-state {
  border-color: var(--el-color-success-light-5);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.chart-title-area {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chart-actions {
  display: flex;
  gap: 4px;
}

.chart-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 4px;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--el-text-color-secondary);
}

.loading-icon {
  font-size: 32px;
  color: var(--el-color-primary);
}

.loading-text {
  font-size: 14px;
}

.loading-progress {
  width: 200px;
}

.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--el-color-danger);
  text-align: center;
}

.error-icon {
  font-size: 32px;
}

.error-message {
  font-size: 14px;
  margin-bottom: 8px;
}

.error-actions {
  display: flex;
  gap: 8px;
}

.chart-display {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.chart-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 4px;
  transition: transform 0.2s ease;
}

.chart-image:hover {
  transform: scale(1.02);
}

.chart-info-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 4px;
}

.chart-display:hover .chart-info-overlay {
  opacity: 1;
}

.chart-info {
  text-align: center;
  padding: 20px;
  max-width: 80%;
}

.chart-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.chart-description {
  font-size: 14px;
  margin: 8px 0;
  line-height: 1.5;
}

.chart-insights h5 {
  margin: 12px 0 8px 0;
  font-size: 14px;
}

.chart-insights ul {
  margin: 0;
  padding-left: 20px;
  text-align: left;
}

.chart-insights li {
  font-size: 13px;
  margin-bottom: 4px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--el-text-color-secondary);
}

.placeholder-icon {
  font-size: 48px;
  color: var(--el-color-info-light-5);
}

.placeholder-text {
  font-size: 14px;
}

.chart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
}

.chart-meta {
  display: flex;
  gap: 12px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.chart-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* 灯箱样式 */
.chart-lightbox .el-dialog__body {
  padding: 0;
}

.lightbox-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  background: #f5f5f5;
}

.lightbox-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.lightbox-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .chart-title-area {
    justify-content: center;
  }
  
  .chart-actions {
    justify-content: center;
  }
  
  .chart-footer {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .chart-meta {
    justify-content: center;
  }
  
  .chart-tags {
    justify-content: center;
  }
}
</style> 
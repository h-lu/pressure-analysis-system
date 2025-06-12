<template>
  <div 
    class="chart-thumbnail"
    :class="{
      'loading': loading,
      'error': error,
      'selected': selected
    }"
    @click="handleClick"
  >
    <!-- 选择框 -->
    <div class="selection-area">
      <el-checkbox
        :model-value="selected"
        @change="handleSelect"
        @click.stop
      />
    </div>

    <!-- 图表内容 -->
    <div class="thumbnail-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <el-icon><Warning /></el-icon>
        <span>加载失败</span>
        <el-button size="small" @click.stop="handleRetry">重试</el-button>
      </div>

      <!-- 图表图片 -->
      <div v-else-if="chartUrl" class="chart-image-container">
        <img 
          :src="chartUrl" 
          :alt="chartConfig?.title"
          class="chart-image"
          @error="handleImageError"
        />
        <div class="image-overlay">
          <div class="overlay-actions">
            <el-button 
              size="small" 
              circle
              @click.stop="handleFullscreen"
              title="全屏查看"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
            <el-button 
              size="small" 
              circle
              @click.stop="handleDownload"
              title="下载图表"
            >
              <el-icon><Download /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 占位符 -->
      <div v-else class="placeholder-state">
        <el-icon><Picture /></el-icon>
        <span>暂无预览</span>
        <el-button size="small" @click.stop="handleLoad">加载</el-button>
      </div>
    </div>

    <!-- 图表信息 -->
    <div class="chart-info">
      <h4 class="chart-title">{{ chartConfig?.title || chartName }}</h4>
      <p class="chart-description">{{ chartConfig?.description }}</p>
      
      <!-- 标签和复杂度 -->
      <div class="chart-meta">
        <el-tag 
          v-if="chartConfig?.complexity" 
          :type="complexityType" 
          size="small"
        >
          {{ complexityText }}
        </el-tag>
        <div class="chart-keywords">
          <el-tag
            v-for="keyword in displayKeywords"
            :key="keyword"
            size="small"
            effect="plain"
            class="keyword-tag"
          >
            {{ keyword }}
          </el-tag>
          <span v-if="remainingKeywords > 0" class="keywords-more">
            +{{ remainingKeywords }}
          </span>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-button 
        size="small" 
        type="text"
        @click.stop="handleQuickView"
        title="快速查看"
      >
        <el-icon><View /></el-icon>
      </el-button>
      <el-button 
        size="small" 
        type="text"
        @click.stop="handleQuickDownload"
        title="快速下载"
      >
        <el-icon><Download /></el-icon>
      </el-button>
      <el-button 
        size="small" 
        type="text"
        @click.stop="handleShowInfo"
        title="详细信息"
      >
        <el-icon><InfoFilled /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading,
  Warning,
  Picture,
  FullScreen,
  Download,
  View,
  InfoFilled
} from '@element-plus/icons-vue'

const props = defineProps({
  chartName: {
    type: String,
    required: true
  },
  chartConfig: {
    type: Object,
    default: () => ({})
  },
  taskId: {
    type: String,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'select', 'download', 'error', 'load'])

// 响应式数据
const loading = ref(false)
const error = ref(null)
const chartUrl = ref('')

// 计算属性
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

const displayKeywords = computed(() => {
  const keywords = props.chartConfig?.keywords || []
  return keywords.slice(0, 2)
})

const remainingKeywords = computed(() => {
  const keywords = props.chartConfig?.keywords || []
  return Math.max(0, keywords.length - 2)
})

// 方法
const loadChart = async () => {
  if (!props.taskId || !props.chartName) return

  loading.value = true
  error.value = null

  try {
    // 构建图表URL
    const url = `http://localhost:8000/api/chart/${props.taskId}/${props.chartName}`
    
    // 验证图表是否存在
    const response = await fetch(url, { method: 'HEAD' })
    
    if (response.ok) {
      chartUrl.value = `${url}?t=${Date.now()}` // 添加时间戳避免缓存
      emit('load', props.chartName)
    } else {
      throw new Error(`图表不存在: ${response.status}`)
    }
  } catch (err) {
    error.value = err
    emit('error', props.chartName, err)
  } finally {
    loading.value = false
  }
}

const handleClick = () => {
  emit('click', props.chartName)
}

const handleSelect = (selected) => {
  emit('select', props.chartName, selected)
}

const handleLoad = () => {
  loadChart()
}

const handleRetry = () => {
  loadChart()
}

const handleImageError = () => {
  const err = new Error('图片加载失败')
  error.value = err
  emit('error', props.chartName, err)
}

const handleFullscreen = () => {
  if (!chartUrl.value) {
    ElMessage.warning('图表未加载完成')
    return
  }
  // 实现全屏查看逻辑
  emit('click', props.chartName)
}

const handleDownload = () => {
  if (!chartUrl.value) {
    ElMessage.warning('图表未加载完成')
    return
  }
  
  try {
    const link = document.createElement('a')
    link.href = chartUrl.value
    link.download = `${props.chartConfig?.title || props.chartName}_${props.taskId}.png`
    link.click()
    
    ElMessage.success('图表下载成功')
    emit('download', props.chartName)
  } catch (error) {
    ElMessage.error('图表下载失败')
  }
}

const handleQuickView = () => {
  emit('click', props.chartName)
}

const handleQuickDownload = () => {
  handleDownload()
}

const handleShowInfo = () => {
  // 显示图表详细信息
  emit('click', props.chartName)
}

// 生命周期
onMounted(() => {
  if (props.autoLoad) {
    loadChart()
  }
})
</script>

<style scoped>
.chart-thumbnail {
  position: relative;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-thumbnail:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.chart-thumbnail.selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
}

.chart-thumbnail.loading {
  opacity: 0.8;
}

.chart-thumbnail.error {
  border-color: var(--el-color-danger-light-5);
}

.selection-area {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 2px;
}

.thumbnail-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 150px;
  position: relative;
}

.loading-state,
.error-state,
.placeholder-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  text-align: center;
  padding: 16px;
}

.loading-state .el-icon {
  font-size: 24px;
  color: var(--el-color-primary);
}

.error-state .el-icon {
  font-size: 24px;
  color: var(--el-color-danger);
}

.placeholder-state .el-icon {
  font-size: 32px;
  color: var(--el-color-info-light-5);
}

.chart-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.chart-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.2s ease;
}

.chart-image:hover {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chart-image-container:hover .image-overlay {
  opacity: 1;
}

.overlay-actions {
  display: flex;
  gap: 8px;
}

.chart-info {
  padding: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.chart-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chart-description {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chart-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.chart-keywords {
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: wrap;
  flex: 1;
}

.keyword-tag {
  font-size: 11px;
  height: 20px;
  line-height: 18px;
  padding: 0 6px;
}

.keywords-more {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.quick-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 2px;
}

.chart-thumbnail:hover .quick-actions {
  opacity: 1;
}

.quick-actions .el-button {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
}

.quick-actions .el-button:hover {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-info {
    padding: 8px;
  }
  
  .chart-title {
    font-size: 13px;
  }
  
  .chart-description {
    font-size: 11px;
  }
  
  .chart-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .quick-actions {
    opacity: 1; /* 在移动端始终显示 */
  }
}
</style> 
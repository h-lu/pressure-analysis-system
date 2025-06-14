<template>
  <div 
    class="chart-list-item"
    :class="{ 'selected': selected, 'loading': loading, 'error': error }"
    @click="handleClick"
  >
    <!-- 选择框 -->
    <div class="item-checkbox">
      <el-checkbox
        :model-value="selected"
        @change="handleSelect"
        @click.stop
      />
    </div>

    <!-- 图表缩略图 -->
    <div class="item-thumbnail">
      <div v-if="loading" class="thumbnail-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
      </div>
      <div v-else-if="error" class="thumbnail-error">
        <el-icon><Warning /></el-icon>
      </div>
      <img 
        v-else-if="chartUrl"
        :src="chartUrl" 
        :alt="chartConfig?.title"
        class="thumbnail-image"
        @error="handleImageError"
      />
      <div v-else class="thumbnail-placeholder">
        <el-icon><Picture /></el-icon>
      </div>
    </div>

    <!-- 图表信息 -->
    <div class="item-content">
      <div class="content-header">
        <h4 class="chart-title">{{ chartConfig?.title || chartName }}</h4>
        <div class="title-badges">
          <el-tag 
            v-if="chartConfig?.complexity" 
            :type="complexityType" 
            size="small"
          >
            {{ complexityText }}
          </el-tag>
          <el-tag 
            v-if="chartConfig?.category"
            :color="categoryColor"
            size="small"
            effect="light"
          >
            {{ categoryLabel }}
          </el-tag>
        </div>
      </div>

      <p class="chart-description">{{ chartConfig?.description }}</p>

      <!-- 关键词和分析类型 -->
      <div class="content-meta">
        <div class="meta-section">
          <span class="meta-label">关键词:</span>
          <div class="keywords-list">
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
              +{{ remainingKeywords }}个
            </span>
          </div>
        </div>

        <div class="meta-section" v-if="chartConfig?.analysisTypes?.length">
          <span class="meta-label">分析类型:</span>
          <div class="analysis-types">
            <el-tag
              v-for="type in chartConfig.analysisTypes.slice(0, 2)"
              :key="type"
              size="small"
              type="info"
              effect="plain"
            >
              {{ type }}
            </el-tag>
            <span v-if="chartConfig.analysisTypes.length > 2" class="types-more">
              +{{ chartConfig.analysisTypes.length - 2 }}个
            </span>
          </div>
        </div>
      </div>

      <!-- 洞察要点 -->
      <div class="content-insights" v-if="chartConfig?.insights?.length">
        <span class="meta-label">洞察要点:</span>
        <ul class="insights-list">
          <li v-for="insight in chartConfig.insights.slice(0, 2)" :key="insight">
            {{ insight }}
          </li>
          <li v-if="chartConfig.insights.length > 2" class="insights-more">
            还有 {{ chartConfig.insights.length - 2 }} 个洞察...
          </li>
        </ul>
      </div>
    </div>

    <!-- 状态和操作 -->
    <div class="item-actions">
      <div class="status-info">
        <el-tag v-if="loading" type="info" size="small">
          <el-icon class="is-loading"><Loading /></el-icon>
          加载中
        </el-tag>
        <el-tag v-else-if="error" type="danger" size="small">
          <el-icon><Warning /></el-icon>
          加载失败
        </el-tag>
        <el-tag v-else-if="chartUrl" type="success" size="small">
          <el-icon><CircleCheck /></el-icon>
          已加载
        </el-tag>
        <el-tag v-else type="info" size="small">
          <el-icon><Clock /></el-icon>
          待加载
        </el-tag>
      </div>

      <div class="action-buttons">
        <el-button 
          size="small" 
          @click.stop="handleQuickView"
          title="快速查看"
        >
          <el-icon><View /></el-icon>
        </el-button>
        <el-button 
          size="small" 
          @click.stop="handleDownload"
          :disabled="!chartUrl"
          title="下载图表"
        >
          <el-icon><Download /></el-icon>
        </el-button>
        <el-button 
          size="small" 
          @click.stop="handleRefresh"
          :loading="refreshing"
          title="刷新图表"
        >
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-dropdown @command="handleMenuAction" trigger="click" @click.stop>
          <el-button size="small">
            <el-icon><More /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="detail">
                <el-icon><InfoFilled /></el-icon>详细信息
              </el-dropdown-item>
              <el-dropdown-item command="fullscreen">
                <el-icon><FullScreen /></el-icon>全屏查看
              </el-dropdown-item>
              <el-dropdown-item command="copy-link">
                <el-icon><Link /></el-icon>复制链接
              </el-dropdown-item>
              <el-dropdown-item divided command="report-issue">
                <el-icon><Warning /></el-icon>报告问题
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
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
  CircleCheck,
  Clock,
  View,
  Download,
  Refresh,
  More,
  InfoFilled,
  FullScreen,
  Link
} from '@element-plus/icons-vue'
import { chartCategories } from '@/config/chartConfig'
import { getFullApiURL } from '@/config'

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

const emit = defineEmits(['click', 'select', 'download', 'error', 'refresh'])

// 响应式数据
const loading = ref(false)
const error = ref(null)
const refreshing = ref(false)
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

const categoryLabel = computed(() => {
  const category = props.chartConfig?.category
  return category ? chartCategories[category]?.label || category : ''
})

const categoryColor = computed(() => {
  const category = props.chartConfig?.category
  return category ? chartCategories[category]?.color || '#909399' : '#909399'
})

const displayKeywords = computed(() => {
  const keywords = props.chartConfig?.keywords || []
  return keywords.slice(0, 3)
})

const remainingKeywords = computed(() => {
  const keywords = props.chartConfig?.keywords || []
  return Math.max(0, keywords.length - 3)
})

// 方法
const loadChart = async () => {
  if (!props.taskId || !props.chartName) return

  loading.value = true
  error.value = null

  try {
    const url = getFullApiURL(`/api/chart/${props.taskId}/${props.chartName}`)
    
    const response = await fetch(url, { method: 'HEAD' })
    
    if (response.ok) {
      chartUrl.value = `${url}?t=${Date.now()}`
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

const handleQuickView = () => {
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

const handleRefresh = async () => {
  refreshing.value = true
  try {
    await loadChart()
    ElMessage.success('图表刷新成功')
    emit('refresh', props.chartName)
  } catch (error) {
    ElMessage.error('图表刷新失败')
  } finally {
    refreshing.value = false
  }
}

const handleImageError = () => {
  const err = new Error('图片加载失败')
  error.value = err
  emit('error', props.chartName, err)
}

const handleMenuAction = (command) => {
  switch (command) {
    case 'detail':
      emit('click', props.chartName)
      break
    case 'fullscreen':
      if (chartUrl.value) {
        emit('click', props.chartName)
      } else {
        ElMessage.warning('图表未加载完成')
      }
      break
    case 'copy-link':
      if (chartUrl.value) {
        navigator.clipboard.writeText(chartUrl.value).then(() => {
          ElMessage.success('链接已复制到剪贴板')
        }).catch(() => {
          ElMessage.error('复制失败')
        })
      } else {
        ElMessage.warning('图表未加载完成')
      }
      break
    case 'report-issue':
      ElMessage.info('问题报告功能开发中...')
      break
  }
}

// 生命周期
onMounted(() => {
  if (props.autoLoad) {
    loadChart()
  }
})
</script>

<style scoped>
.chart-list-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 120px;
}

.chart-list-item:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.chart-list-item.selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
  background: var(--el-color-primary-light-9);
}

.chart-list-item.loading {
  opacity: 0.8;
}

.chart-list-item.error {
  border-color: var(--el-color-danger-light-5);
}

.item-checkbox {
  flex-shrink: 0;
  padding-top: 2px;
}

.item-thumbnail {
  flex-shrink: 0;
  width: 80px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--el-bg-color-page);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--el-border-color-lighter);
}

.thumbnail-loading,
.thumbnail-error,
.thumbnail-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--el-text-color-secondary);
}

.thumbnail-loading .el-icon {
  font-size: 18px;
  color: var(--el-color-primary);
}

.thumbnail-error .el-icon {
  font-size: 18px;
  color: var(--el-color-danger);
}

.thumbnail-placeholder .el-icon {
  font-size: 20px;
  color: var(--el-color-info-light-5);
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.3;
  flex: 1;
  min-width: 0;
}

.title-badges {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-shrink: 0;
}

.chart-description {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.content-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-section {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.meta-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
  flex-shrink: 0;
  min-width: 60px;
}

.keywords-list,
.analysis-types {
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: wrap;
}

.keyword-tag {
  font-size: 11px;
  height: 20px;
  line-height: 18px;
  padding: 0 6px;
}

.keywords-more,
.types-more {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.content-insights {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.insights-list {
  margin: 0;
  padding: 0;
  list-style: none;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.insights-list li {
  position: relative;
  padding-left: 12px;
  margin-bottom: 2px;
}

.insights-list li:before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--el-color-primary);
}

.insights-more {
  font-style: italic;
  color: var(--el-text-color-placeholder);
}

.item-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
  min-width: 120px;
}

.status-info {
  display: flex;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  gap: 4px;
  align-items: center;
}

.action-buttons .el-button {
  padding: 6px;
  width: 32px;
  height: 32px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-list-item {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }
  
  .item-thumbnail {
    width: 100%;
    height: 80px;
  }
  
  .content-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .title-badges {
    align-self: flex-start;
  }
  
  .content-meta {
    gap: 4px;
  }
  
  .meta-section {
    flex-direction: column;
    gap: 4px;
  }
  
  .meta-label {
    min-width: auto;
  }
  
  .item-actions {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    min-width: auto;
  }
  
  .action-buttons {
    flex-shrink: 0;
  }
}

@media (max-width: 480px) {
  .chart-list-item {
    padding: 8px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: flex-end;
  }
  
  .action-buttons .el-button {
    width: 28px;
    height: 28px;
    padding: 4px;
  }
}
</style> 
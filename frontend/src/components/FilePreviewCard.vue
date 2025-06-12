<template>
  <el-card shadow="hover" class="preview-card">
    <template #header>
      <div class="card-header">
        <el-icon><View /></el-icon>
        <span>数据预览</span>
        <div class="header-info" v-if="filename">
          <el-tag size="small">{{ filename }}</el-tag>
        </div>
      </div>
    </template>

    <div v-if="data" class="preview-content">
      <!-- 数据统计摘要 -->
      <div class="data-stats">
        <el-row :gutter="16">
          <el-col :span="4">
            <el-statistic title="总行数" :value="data.stats?.total_rows || 0" />
          </el-col>
          <el-col :span="4">
            <el-statistic title="列数" :value="data.columns?.length || 0" />
          </el-col>
          <el-col :span="4">
            <el-statistic title="数值列" :value="numericColumns" />
          </el-col>
          <el-col :span="4">
            <el-statistic title="文本列" :value="textColumns" />
          </el-col>
          <el-col :span="4">
            <el-statistic title="文件大小" :value="formatFileSize(estimatedFileSize)" />
          </el-col>
          <el-col :span="4">
            <el-statistic title="数据质量" :value="dataQualityScore + '%'" />
          </el-col>
        </el-row>
      </div>

      <!-- 列信息详情 -->
      <div class="column-details">
        <el-divider content-position="left">
          <span>列信息</span>
          <el-button size="small" @click="showColumnDetails = !showColumnDetails" type="text">
            {{ showColumnDetails ? '收起' : '展开' }}
          </el-button>
        </el-divider>
        
        <el-collapse v-model="showColumnDetails" v-if="showColumnDetails">
          <el-collapse-item name="columns">
            <el-table :data="columnInfo" size="small" style="width: 100%">
              <el-table-column prop="name" label="列名" width="120" />
              <el-table-column prop="type" label="数据类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getTypeTagType(row.type)" size="small">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="nullCount" label="缺失值" width="80" />
              <el-table-column prop="uniqueCount" label="唯一值" width="80" />
              <el-table-column prop="sampleValues" label="示例值" min-width="200">
                <template #default="{ row }">
                  <span class="sample-values">{{ row.sampleValues.join(', ') }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 数据表格 -->
      <div class="data-table">
        <div class="table-toolbar">
          <div class="toolbar-left">
            <span>数据预览 (前 {{ displayedRows }} 行)</span>
          </div>
          <div class="toolbar-right">
            <el-button size="small" @click="refreshPreview" :loading="refreshing">
              <el-icon><Refresh /></el-icon>
            </el-button>
            <el-button size="small" @click="exportPreview">
              <el-icon><Download /></el-icon>
            </el-button>
          </div>
        </div>

        <el-table
          :data="paginatedData"
          stripe
          border
          size="small"
          max-height="400"
          style="width: 100%"
          :loading="loading"
          @sort-change="handleSortChange"
        >
          <el-table-column
            v-for="column in data.columns"
            :key="column"
            :prop="column"
            :label="column"
            :width="getColumnWidth(column)"
            :sortable="isNumericColumn(column) ? 'custom' : false"
            show-overflow-tooltip
          >
            <template #default="{ row, $index }">
              <span 
                :class="getCellClass(row[column], column)" 
                :title="getCellTooltip(row[column], column)"
              >
                {{ formatCellValue(row[column], column) }}
              </span>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页器 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalRows"
            layout="total, sizes, prev, pager, next, jumper"
            small
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 数据质量详情 -->
      <div class="quality-details">
        <el-divider content-position="left">数据质量检查</el-divider>
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="quality-item">
              <span class="quality-label">缺失值:</span>
              <el-tag :type="getQualityTagType(data.stats?.missing_values)" size="small">
                {{ data.stats?.missing_values || 0 }} 个
              </el-tag>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="quality-item">
              <span class="quality-label">重复行:</span>
              <el-tag :type="getQualityTagType(data.stats?.duplicate_rows)" size="small">
                {{ data.stats?.duplicate_rows || 0 }} 行
              </el-tag>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="quality-item">
              <span class="quality-label">异常值:</span>
              <el-tag :type="getQualityTagType(data.stats?.outliers)" size="small">
                {{ data.stats?.outliers || 0 }} 个
              </el-tag>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="quality-item">
              <span class="quality-label">完整性:</span>
              <el-tag :type="getCompletenessTagType(completenessRatio)" size="small">
                {{ (completenessRatio * 100).toFixed(1) }}%
              </el-tag>
            </div>
          </el-col>
        </el-row>

        <!-- 数据范围信息 -->
        <div v-if="numericStats.length > 0" class="numeric-stats">
          <el-divider content-position="left">数值列统计</el-divider>
          <el-table :data="numericStats" size="small" style="width: 100%">
            <el-table-column prop="column" label="列名" width="120" />
            <el-table-column prop="min" label="最小值" width="100" />
            <el-table-column prop="max" label="最大值" width="100" />
            <el-table-column prop="mean" label="平均值" width="100" />
            <el-table-column prop="std" label="标准差" width="100" />
            <el-table-column prop="range" label="数据范围" min-width="150" />
          </el-table>
        </div>
      </div>

      <!-- 数据建议 -->
      <div v-if="dataRecommendations.length > 0" class="data-recommendations">
        <el-divider content-position="left">数据建议</el-divider>
        <el-alert
          v-for="(rec, index) in dataRecommendations"
          :key="index"
          :title="rec.title"
          :type="rec.type"
          :description="rec.description"
          show-icon
          :closable="false"
          style="margin-bottom: 8px;"
        />
      </div>
    </div>

    <el-empty v-else description="暂无数据预览" />
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Object,
    default: null
  },
  filename: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'export'])

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(20)
const showColumnDetails = ref(false)
const sortColumn = ref('')
const sortOrder = ref('')
const refreshing = ref(false)

// 计算属性
const totalRows = computed(() => props.data?.data?.length || 0)
const displayedRows = computed(() => Math.min(totalRows.value, pageSize.value))

const paginatedData = computed(() => {
  if (!props.data?.data) return []
  
  let data = [...props.data.data]
  
  // 排序
  if (sortColumn.value && sortOrder.value) {
    data.sort((a, b) => {
      const aVal = parseFloat(a[sortColumn.value]) || 0
      const bVal = parseFloat(b[sortColumn.value]) || 0
      return sortOrder.value === 'ascending' ? aVal - bVal : bVal - aVal
    })
  }
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  return data.slice(start, start + pageSize.value)
})

const numericColumns = computed(() => {
  if (!props.data?.columns) return 0
  return props.data.columns.filter(col => isNumericColumn(col)).length
})

const textColumns = computed(() => {
  if (!props.data?.columns) return 0
  return props.data.columns.length - numericColumns.value
})

const estimatedFileSize = computed(() => {
  const rows = props.data?.stats?.total_rows || 0
  const cols = props.data?.columns?.length || 0
  return rows * cols * 8 // bytes
})

const dataQualityScore = computed(() => {
  if (!props.data?.stats) return 100
  
  const totalCells = (props.data.stats.total_rows || 0) * (props.data.columns?.length || 1)
  const missingCells = props.data.stats.missing_values || 0
  const duplicateRows = props.data.stats.duplicate_rows || 0
  
  const completeness = totalCells > 0 ? (totalCells - missingCells) / totalCells : 1
  const uniqueness = props.data.stats.total_rows > 0 ? (props.data.stats.total_rows - duplicateRows) / props.data.stats.total_rows : 1
  
  return Math.round((completeness * 0.7 + uniqueness * 0.3) * 100)
})

const completenessRatio = computed(() => {
  if (!props.data?.stats) return 1
  
  const totalCells = (props.data.stats.total_rows || 0) * (props.data.columns?.length || 1)
  const missingCells = props.data.stats.missing_values || 0
  
  return totalCells > 0 ? (totalCells - missingCells) / totalCells : 1
})

const columnInfo = computed(() => {
  if (!props.data?.columns || !props.data?.data) return []
  
  return props.data.columns.map(col => {
    const values = props.data.data.map(row => row[col]).filter(val => val !== null && val !== undefined)
    const nullCount = props.data.data.length - values.length
    const uniqueValues = [...new Set(values)]
    const sampleValues = uniqueValues.slice(0, 3)
    
    return {
      name: col,
      type: detectColumnType(col),
      nullCount,
      uniqueCount: uniqueValues.length,
      sampleValues: sampleValues.map(val => String(val))
    }
  })
})

const numericStats = computed(() => {
  if (!props.data?.columns || !props.data?.data) return []
  
  return props.data.columns
    .filter(col => isNumericColumn(col))
    .map(col => {
      const values = props.data.data
        .map(row => parseFloat(row[col]))
        .filter(val => !isNaN(val))
      
      if (values.length === 0) return null
      
      const min = Math.min(...values)
      const max = Math.max(...values)
      const mean = values.reduce((a, b) => a + b, 0) / values.length
      const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length
      const std = Math.sqrt(variance)
      
      return {
        column: col,
        min: min.toFixed(3),
        max: max.toFixed(3),
        mean: mean.toFixed(3),
        std: std.toFixed(3),
        range: `${min.toFixed(2)} ~ ${max.toFixed(2)}`
      }
    })
    .filter(stat => stat !== null)
})

const dataRecommendations = computed(() => {
  const recommendations = []
  
  if (!props.data?.stats) return recommendations
  
  // 缺失值建议
  if (props.data.stats.missing_values > 0) {
    recommendations.push({
      type: 'warning',
      title: '发现缺失值',
      description: `数据中有 ${props.data.stats.missing_values} 个缺失值，建议检查数据完整性或考虑数据清洗。`
    })
  }
  
  // 重复数据建议
  if (props.data.stats.duplicate_rows > 0) {
    recommendations.push({
      type: 'warning',
      title: '发现重复数据',
      description: `数据中有 ${props.data.stats.duplicate_rows} 行重复数据，建议去重处理。`
    })
  }
  
  // 数据量建议
  if (props.data.stats.total_rows < 10) {
    recommendations.push({
      type: 'error',
      title: '数据量过少',
      description: '数据量过少可能影响分析结果的可靠性，建议增加数据样本。'
    })
  } else if (props.data.stats.total_rows > 10000) {
    recommendations.push({
      type: 'info',
      title: '数据量较大',
      description: '数据量较大，分析可能需要更长时间，建议合理设置分析参数。'
    })
  }
  
  // 数据质量建议
  if (dataQualityScore.value < 80) {
    recommendations.push({
      type: 'warning',
      title: '数据质量偏低',
      description: '当前数据质量评分较低，建议进行数据清洗后再进行分析。'
    })
  } else if (dataQualityScore.value >= 95) {
    recommendations.push({
      type: 'success',
      title: '数据质量优秀',
      description: '数据质量良好，可以直接进行分析。'
    })
  }
  
  return recommendations
})

// 方法
const isNumericColumn = (column) => {
  if (!props.data?.data) return false
  
  const sampleValues = props.data.data.slice(0, 10).map(row => row[column])
  const numericCount = sampleValues.filter(val => !isNaN(parseFloat(val))).length
  
  return numericCount >= sampleValues.length * 0.8
}

const detectColumnType = (column) => {
  if (isNumericColumn(column)) {
    return '数值'
  }
  
  if (!props.data?.data) return '未知'
  
  const sampleValues = props.data.data.slice(0, 10).map(row => row[column])
  const datePattern = /^\d{4}-\d{2}-\d{2}|\d{2}\/\d{2}\/\d{4}/
  const dateCount = sampleValues.filter(val => datePattern.test(String(val))).length
  
  if (dateCount >= sampleValues.length * 0.8) {
    return '日期'
  }
  
  return '文本'
}

const getColumnWidth = (column) => {
  const minWidth = 100
  const maxWidth = 200
  const headerWidth = column.length * 12 + 40
  return Math.min(Math.max(headerWidth, minWidth), maxWidth)
}

const formatCellValue = (value, column) => {
  if (value === null || value === undefined || value === '') return '-'
  
  if (isNumericColumn(column) && !isNaN(parseFloat(value))) {
    const num = parseFloat(value)
    return num % 1 === 0 ? num.toString() : num.toFixed(3)
  }
  
  return String(value)
}

const getCellClass = (value, column) => {
  if (value === null || value === undefined || value === '') return 'cell-null'
  if (isNumericColumn(column)) return 'cell-number'
  return 'cell-text'
}

const getCellTooltip = (value, column) => {
  if (value === null || value === undefined || value === '') return '缺失值'
  return `${column}: ${value}`
}

const getTypeTagType = (type) => {
  const typeMap = {
    '数值': 'primary',
    '文本': 'info',
    '日期': 'success',
    '未知': 'warning'
  }
  return typeMap[type] || 'info'
}

const getQualityTagType = (count) => {
  if (!count || count === 0) return 'success'
  if (count <= 5) return 'warning'
  return 'danger'
}

const getCompletenessTagType = (ratio) => {
  if (ratio >= 0.95) return 'success'
  if (ratio >= 0.8) return 'warning'
  return 'danger'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleSortChange = ({ column, prop, order }) => {
  sortColumn.value = order ? prop : ''
  sortOrder.value = order || ''
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}

const refreshPreview = async () => {
  refreshing.value = true
  try {
    emit('refresh')
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

const exportPreview = () => {
  emit('export')
}

// 监听数据变化，重置分页
watch(() => props.data, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.preview-card {
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-info {
  margin-left: auto;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.data-stats {
  padding: 20px;
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-color-success-light-9));
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.column-details {
  margin-top: 10px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
}

.toolbar-left {
  font-size: 14px;
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.data-table {
  border-radius: 8px;
  overflow: hidden;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.quality-details {
  margin-top: 10px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.quality-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  min-width: 60px;
}

.numeric-stats {
  margin-top: 16px;
}

.data-recommendations {
  margin-top: 10px;
}

.sample-values {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 单元格样式 */
.cell-null {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.cell-number {
  color: var(--el-color-primary);
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.cell-text {
  color: var(--el-text-color-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-stats .el-col {
    margin-bottom: 16px;
  }
  
  .table-toolbar {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .toolbar-right {
    justify-content: center;
  }
}
</style> 
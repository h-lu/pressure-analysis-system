<template>
  <div class="history-page">
    <el-page-header content="历史分析记录" />
    
    <div class="history-content">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索任务名称或文件名..."
            :prefix-icon="Search"
            style="width: 300px"
            @input="handleSearch"
          />
          <el-button 
            @click="refreshHistory" 
            :icon="Refresh"
            :loading="loading"
          >
            刷新
          </el-button>
        </div>
        
        <div class="toolbar-right">
          <el-button 
            type="danger" 
            :disabled="selectedRecords.length === 0"
            @click="batchDelete"
          >
            批量删除 ({{ selectedRecords.length }})
          </el-button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-cards" v-if="stats">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_tasks || 0 }}</div>
            <div class="stat-label">总记录数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.completed_tasks || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.success_rate || 0 }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </el-card>
      </div>

      <!-- 历史记录表格 -->
      <el-card class="table-card">
        <el-table 
          :data="paginatedRecords" 
          v-loading="loading"
          @selection-change="handleSelectionChange"
          stripe
          empty-text="暂无历史记录"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column prop="name" label="记录名称" min-width="200">
            <template #default="{ row }">
              <div class="record-name">
                <span>{{ row.name }}</span>
                <el-button 
                  type="text" 
                  size="small" 
                  @click="renameRecord(row)"
                  style="margin-left: 8px"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="original_filename" label="原始文件" width="150">
            <template #default="{ row }">
              {{ row.original_filename || '未知' }}
            </template>
          </el-table-column>
          
          <el-table-column prop="successRate" label="成功率" width="100">
            <template #default="{ row }">
              <el-tag :type="getSuccessRateType(row.successRate)">
                {{ (row.successRate || 0).toFixed(1) }}%
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="date" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.date || row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="modified_at" label="修改时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.modified_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  type="primary"
                  @click="viewResults(row.id)"
                >
                  查看结果
                </el-button>
                <el-button 
                  size="small" 
                  type="danger"
                  @click="deleteRecord(row.id)"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredRecords.length"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handleCurrentPageChange"
          class="pagination"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Edit } from '@element-plus/icons-vue'
import { useAnalysisStore } from '@/stores/analysis'

const router = useRouter()
const analysisStore = useAnalysisStore()

// 数据状态
const loading = ref(false)
const records = ref([])
const selectedRecords = ref([])
const stats = ref({})

// 搜索和过滤
const searchQuery = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const filteredRecords = computed(() => {
  if (!searchQuery.value) return records.value
  
  const query = searchQuery.value.toLowerCase()
  return records.value.filter(record => 
    (record.name && record.name.toLowerCase().includes(query)) ||
    (record.original_filename && record.original_filename.toLowerCase().includes(query))
  )
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// 方法
const getSuccessRateType = (rate) => {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'danger'
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const history = await analysisStore.getHistory()
    records.value = history || []
  } catch (error) {
    console.error('获取历史记录失败:', error)
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const historyStats = await analysisStore.getHistoryStats()
    stats.value = historyStats || {}
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

const refreshHistory = async () => {
  await Promise.all([fetchHistory(), fetchStats()])
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSelectionChange = (selection) => {
  selectedRecords.value = selection
}

const handlePageSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentPageChange = () => {
  // 页面变化时的处理
}

const viewResults = (taskId) => {
  router.push(`/results/${taskId}`)
}

const renameRecord = async (record) => {
  try {
    const { value: newName } = await ElMessageBox.prompt(
      '请输入新的记录名称:',
      '重命名分析记录',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /\S+/,
        inputErrorMessage: '名称不能为空',
        inputValue: record.name
      }
    )
    
    if (newName && newName.trim()) {
      loading.value = true
      await analysisStore.updateAnalysisRecordName(record.id, newName.trim())
      ElMessage.success('记录名称更新成功')
      await fetchHistory()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重命名失败:', error)
      ElMessage.error('重命名失败')
    }
  } finally {
    loading.value = false
  }
}

const deleteRecord = async (taskId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个分析记录吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    loading.value = true
    await analysisStore.deleteAnalysisRecord(taskId)
    ElMessage.success('记录删除成功')
    await refreshHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除记录失败:', error)
      ElMessage.error('删除记录失败')
    }
  } finally {
    loading.value = false
  }
}

const batchDelete = async () => {
  if (selectedRecords.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 个分析记录吗？删除后无法恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    loading.value = true
    const taskIds = selectedRecords.value.map(record => record.id)
    
    const response = await analysisStore.batchDeleteAnalysisRecords(taskIds)
    
    if (response.success_count > 0) {
      ElMessage.success(`成功删除 ${response.success_count} 个记录`)
    }
    
    if (response.failed_count > 0) {
      ElMessage.warning(`${response.failed_count} 个记录删除失败`)
    }
    
    selectedRecords.value = []
    await refreshHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.history-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.history-content {
  margin-top: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.table-card {
  margin-bottom: 20px;
}

.record-name {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 12px;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style> 
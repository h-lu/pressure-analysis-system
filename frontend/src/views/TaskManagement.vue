<template>
  <div class="task-management-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">任务管理</h1>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <!-- 搜索和过滤器 -->
      <div class="search-filters">
        <div class="search-input">
          <el-icon><Search /></el-icon>
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索任务ID或文件名"
            clearable
            @input="handleSearch"
          />
        </div>
        <el-select 
          v-model="statusFilter" 
          placeholder="全部状态"
          clearable
          @change="handleStatusFilter"
        >
          <el-option label="全部状态" value="" />
          <el-option label="等待中" value="pending" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button 
          type="danger" 
          :disabled="selectedTasks.length === 0"
          @click="batchDelete"
        >
          批量删除 ({{ selectedTasks.length }})
        </el-button>
        <el-button @click="refreshTasks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 任务表格 -->
    <div class="tasks-table">
      <el-table 
        :data="filteredTasks" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="taskId" label="任务ID" width="120">
          <template #default="{ row }">
            <span class="task-id">{{ row.taskId.substring(0, 8) }}...</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="分析名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span :title="row.name">{{ row.name || row.fileName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fileName" label="原始文件名" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="120">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress 
                :percentage="row.progress" 
                :status="getProgressStatus(row.status)"
                :stroke-width="8"
                :show-text="false"
              />
              <span class="progress-text">{{ row.progress }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="180">
          <template #default="{ row }">
            {{ row.startTime || '未开始' }}
          </template>
        </el-table-column>
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="{ row }">
            <span>{{ row.successRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="modifiedAt" label="修改时间" width="180">
          <template #default="{ row }">
            <span>{{ row.modifiedAt || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                size="small" 
                type="primary"
                @click="viewResults(row.taskId)"
              >
                查看结果
              </el-button>
              <el-button 
                size="small" 
                type="success"
                @click="renameTask(row)"
              >
                重命名
              </el-button>
              <el-button 
                size="small" 
                type="danger"
                @click="deleteTask(row.taskId)"
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
        :total="totalTasks"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handleCurrentPageChange"
        class="pagination"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { useAnalysisStore } from '@/stores/analysis'

const analysisStore = useAnalysisStore()

const router = useRouter()

// 数据状态
const loading = ref(false)
const tasks = ref([])
const selectedTasks = ref([])

// 搜索和过滤
const searchQuery = ref('')
const statusFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const totalTasks = ref(0)

// 计算属性
const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(task => 
      task.taskId.toLowerCase().includes(query) ||
      task.fileName.toLowerCase().includes(query)
    )
  }
  
  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(task => task.status === statusFilter.value)
  }
  
  totalTasks.value = filtered.length
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

// 方法
const getStatusType = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'running': return 'warning'
    case 'failed': return 'danger'
    case 'pending': return 'info'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'running': return '运行中'
    case 'failed': return '失败'
    case 'pending': return '等待中'
    default: return status
  }
}

const getProgressStatus = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'exception'
    default: return null
  }
}

const fetchTasks = async () => {
  loading.value = true
  try {
    console.log('获取任务列表...')
    // 使用历史记录API而不是tasks API，确保获取最新的数据包括修改后的名称
    const response = await fetch('http://localhost:8000/api/history/')
    
    if (!response.ok) {
      throw new Error(`API返回错误: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('历史记录API返回:', data)
    
    if (data.success && data.history) {
      tasks.value = data.history.map(task => ({
        taskId: task.id || task.task_id,
        fileName: task.original_filename || task.filename || 'unknown.csv',
        name: task.name, // 包含用户自定义的名称
        status: 'completed', // 历史记录都是已完成的
        progress: 100,
        startTime: task.date || task.created_at ? formatDateTime(task.date || task.created_at) : '',
        dataPoints: task.data_points || 0,
        successRate: task.successRate || 0,
        modifiedAt: task.modified_at ? formatDateTime(task.modified_at) : null
      }))
    } else {
      console.warn('历史记录格式不正确:', data)
      tasks.value = []
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
    ElMessage.error('获取历史记录失败')
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const viewResults = (taskId) => {
  router.push(`/results/${taskId}`)
}

const deleteTask = async (taskId) => {
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
    
    await analysisStore.deleteAnalysisRecord(taskId)
    ElMessage.success('分析记录删除成功')
    await fetchTasks() // 重新获取任务列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除分析记录失败:', error)
      ElMessage.error('删除分析记录失败')
    }
  }
}

const batchDelete = async () => {
  if (selectedTasks.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTasks.value.length} 个分析记录吗？删除后无法恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    loading.value = true
    const taskIds = selectedTasks.value.map(task => task.taskId)
    
    const response = await analysisStore.batchDeleteAnalysisRecords(taskIds)
    
    if (response.success_count > 0) {
      ElMessage.success(`成功删除 ${response.success_count} 个分析记录`)
    }
    
    if (response.failed_count > 0) {
      ElMessage.warning(`${response.failed_count} 个记录删除失败`)
    }
    
    selectedTasks.value = []
    await fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value = false
  }
}

const refreshTasks = () => {
  fetchTasks()
}

const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
}

const handleStatusFilter = () => {
  currentPage.value = 1 // 重置到第一页
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

// 重命名分析记录
const renameTask = async (task) => {
  try {
    const { value: newName } = await ElMessageBox.prompt(
      '请输入新的分析记录名称:',
      '重命名分析记录',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /\S+/,
        inputErrorMessage: '名称不能为空',
        inputValue: task.name || task.fileName
      }
    )
    
    if (newName && newName.trim()) {
      loading.value = true
      await analysisStore.updateAnalysisRecordName(task.taskId, newName.trim())
      ElMessage.success('分析记录名称更新成功')
      await fetchTasks() // 重新获取任务列表
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

const handlePageSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentPageChange = () => {
  // 页面变化时可以做一些操作
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.task-management-page {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  color: #303133;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.search-filters {
  display: flex;
  gap: 15px;
  flex: 1;
}

.search-input {
  position: relative;
  width: 300px;
}

.search-input .el-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  z-index: 1;
}

.search-input .el-input {
  padding-left: 35px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.tasks-table {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.task-id {
  font-family: 'Courier New', monospace;
  color: #409EFF;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style> 
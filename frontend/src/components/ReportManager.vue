<template>
  <div class="report-manager">
    <el-card class="manager-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="manager-icon"><FolderOpened /></el-icon>
            <span class="header-title">报告管理中心</span>
          </div>
          <div class="header-right">
            <el-badge :value="totalReports" class="reports-badge" type="primary">
              <el-button size="small" @click="refreshReports">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </el-badge>
          </div>
        </div>
      </template>

      <!-- 工具栏 -->
      <div class="manager-toolbar">
        <div class="toolbar-left">
          <!-- 搜索框 -->
          <el-input
            v-model="searchKeyword"
            placeholder="搜索报告..."
            size="small"
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <!-- 状态筛选 -->
          <el-select
            v-model="statusFilter"
            placeholder="状态筛选"
            size="small"
            clearable
          >
            <el-option label="已完成" value="completed" />
            <el-option label="生成中" value="generating" />
            <el-option label="失败" value="failed" />
          </el-select>

          <!-- 时间筛选 -->
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            size="small"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY/MM/DD"
          />
        </div>

        <div class="toolbar-right">
          <!-- 批量操作 -->
          <el-dropdown @command="handleBatchAction" trigger="click">
            <el-button size="small" :disabled="selectedReports.length === 0">
              批量操作 ({{ selectedReports.length }})
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="download">批量下载</el-dropdown-item>
                <el-dropdown-item command="delete" divided>批量删除</el-dropdown-item>
                <el-dropdown-item command="export">导出列表</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- 新建报告 -->
          <el-button type="primary" size="small" @click="createNewReport">
            <el-icon><Plus /></el-icon>
            新建报告
          </el-button>
        </div>
      </div>

      <!-- 报告列表 -->
      <div class="reports-table">
        <el-table
          :data="filteredReports"
          v-loading="loading"
          stripe
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
          row-class-name="report-row"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="报告信息" min-width="250">
            <template #default="{ row }">
              <div class="report-info">
                <div class="report-title">
                  <el-icon class="report-type-icon">
                    <Document v-if="row.format === 'docx'" />
                    <DocumentCopy v-else />
                  </el-icon>
                  <span class="title-text">{{ row.title || getDefaultTitle(row) }}</span>
                </div>
                <div class="report-meta">
                  <span class="meta-item">任务ID: {{ row.task_id }}</span>
                  <span class="meta-item">模板: {{ getTemplateName(row.template) }}</span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="生成时间" width="180" sortable>
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="文件大小" width="100" sortable>
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>

          <el-table-column label="图表数量" width="100">
            <template #default="{ row }">
              {{ row.charts_count || 0 }}张
            </template>
          </el-table-column>

          <el-table-column label="下载次数" width="100">
            <template #default="{ row }">
              {{ row.download_count || 0 }}次
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button
                  size="small"
                  type="primary"
                  :disabled="row.status !== 'completed'"
                  :loading="downloadingReports[row.id]"
                  @click.stop="downloadReport(row)"
                >
                  下载
                </el-button>
                
                <el-dropdown @command="(cmd) => handleRowAction(cmd, row)" trigger="click">
                  <el-button size="small">
                    更多
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="preview">预览</el-dropdown-item>
                      <el-dropdown-item command="rename">重命名</el-dropdown-item>
                      <el-dropdown-item command="duplicate">复制</el-dropdown-item>
                      <el-dropdown-item command="details">详情</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="filteredReports.length"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 报告模板管理 -->
      <div class="template-management">
        <el-divider content-position="left">
          <el-icon><Setting /></el-icon>
          模板管理
        </el-divider>
        
        <div class="template-list">
          <div
            v-for="template in reportTemplates"
            :key="template.id"
            class="template-item"
            @click="editTemplate(template)"
          >
            <div class="template-preview">
              <el-icon class="template-icon"><DocumentCopy /></el-icon>
            </div>
            <div class="template-info">
              <h5 class="template-name">{{ template.name }}</h5>
              <p class="template-description">{{ template.description }}</p>
              <div class="template-meta">
                <span class="usage-count">使用: {{ template.usage_count }}次</span>
                <span class="last-modified">更新: {{ formatDate(template.updated_at) }}</span>
              </div>
            </div>
            <div class="template-actions">
              <el-button size="small" @click.stop="useTemplate(template)">使用</el-button>
              <el-button size="small" @click.stop="duplicateTemplate(template)">复制</el-button>
              <el-button size="small" type="danger" @click.stop="deleteTemplate(template)">删除</el-button>
            </div>
          </div>
        </div>

        <div class="template-controls">
          <el-button @click="createTemplate">
            <el-icon><Plus /></el-icon>
            创建模板
          </el-button>
          <el-button @click="importTemplate">
            <el-icon><Upload /></el-icon>
            导入模板
          </el-button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="statistics-panel">
        <el-divider content-position="left">
          <el-icon><DataAnalysis /></el-icon>
          统计信息
        </el-divider>
        
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ statistics.totalReports }}</div>
            <div class="stat-label">总报告数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ statistics.totalDownloads }}</div>
            <div class="stat-label">总下载次数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ formatFileSize(statistics.totalSize) }}</div>
            <div class="stat-label">总存储大小</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ statistics.avgGenerationTime }}s</div>
            <div class="stat-label">平均生成时间</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 报告详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="selectedReport?.title || '报告详情'"
      width="60%"
      center
    >
      <div v-if="selectedReport" class="report-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报告ID">{{ selectedReport.id }}</el-descriptions-item>
          <el-descriptions-item label="任务ID">{{ selectedReport.task_id }}</el-descriptions-item>
          <el-descriptions-item label="模板">{{ getTemplateName(selectedReport.template) }}</el-descriptions-item>
          <el-descriptions-item label="格式">{{ selectedReport.format?.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="生成时间">{{ formatTime(selectedReport.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(selectedReport.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="图表数量">{{ selectedReport.charts_count }}张</el-descriptions-item>
          <el-descriptions-item label="下载次数">{{ selectedReport.download_count }}次</el-descriptions-item>
          <el-descriptions-item label="包含组件" :span="2">
            <el-tag
              v-for="component in selectedReport.components"
              :key="component"
              size="small"
              class="component-tag"
            >
              {{ getComponentName(component) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-actions">
          <el-button type="primary" @click="downloadReport(selectedReport)">
            <el-icon><Download /></el-icon>
            下载报告
          </el-button>
          <el-button @click="regenerateReport(selectedReport)">
            <el-icon><Refresh /></el-icon>
            重新生成
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名报告" width="400px">
      <el-form :model="renameForm" label-width="80px">
        <el-form-item label="报告名称">
          <el-input v-model="renameForm.title" placeholder="请输入报告名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import {
  FolderOpened, Refresh, Search, ArrowDown, Plus, Document, DocumentCopy,
  Setting, DataAnalysis, Download, Upload
} from '@element-plus/icons-vue'

const props = defineProps({
  taskId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['report-selected', 'new-report'])

// 响应式状态
const loading = ref(false)
const reports = ref([])
const selectedReports = ref([])
const downloadingReports = ref({})
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选和搜索
const searchKeyword = ref('')
const statusFilter = ref('')
const dateRange = ref([])

// 对话框状态
const detailDialogVisible = ref(false)
const renameDialogVisible = ref(false)
const selectedReport = ref(null)
const renameForm = ref({ title: '' })

// 模板管理
const reportTemplates = ref([
  {
    id: 1,
    name: '标准质量报告',
    description: '包含基础分析、图表和AI建议的标准模板',
    usage_count: 25,
    updated_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    name: '技术详细报告',
    description: '面向技术人员的详细分析报告',
    usage_count: 12,
    updated_at: '2024-01-10T14:20:00Z'
  },
  {
    id: 3,
    name: '管理摘要报告',
    description: '面向管理层的简洁摘要报告',
    usage_count: 18,
    updated_at: '2024-01-08T09:15:00Z'
  }
])

// 计算属性
const totalReports = computed(() => reports.value.length)

const filteredReports = computed(() => {
  let filtered = reports.value

  // 搜索筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(report =>
      (report.title || '').toLowerCase().includes(keyword) ||
      report.task_id.toLowerCase().includes(keyword)
    )
  }

  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter(report => report.status === statusFilter.value)
  }

  // 时间筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const [startDate, endDate] = dateRange.value
    filtered = filtered.filter(report => {
      const reportDate = new Date(report.created_at)
      return reportDate >= startDate && reportDate <= endDate
    })
  }

  return filtered
})

const statistics = computed(() => {
  const stats = {
    totalReports: reports.value.length,
    totalDownloads: 0,
    totalSize: 0,
    avgGenerationTime: 0
  }

  reports.value.forEach(report => {
    stats.totalDownloads += report.download_count || 0
    stats.totalSize += report.file_size || 0
    stats.avgGenerationTime += report.generation_time || 0
  })

  if (reports.value.length > 0) {
    stats.avgGenerationTime = Math.round(stats.avgGenerationTime / reports.value.length)
  }

  return stats
})

// 生命周期
onMounted(() => {
  loadReports()
})

// 方法
const loadReports = async () => {
  loading.value = true
  
  try {
    // 模拟API调用加载报告列表
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟报告数据
    reports.value = [
      {
        id: 'report_001',
        task_id: 'task_123',
        title: '压力测试分析报告',
        template: 'comprehensive',
        format: 'docx',
        status: 'completed',
        created_at: '2024-01-15T10:30:00Z',
        file_size: 2500000, // 2.5MB
        charts_count: 15,
        download_count: 3,
        generation_time: 45,
        components: ['cover', 'summary', 'charts', 'ai_analysis']
      },
      {
        id: 'report_002',
        task_id: 'task_124',
        title: '质量能力评估报告',
        template: 'technical',
        format: 'docx',
        status: 'completed',
        created_at: '2024-01-14T15:45:00Z',
        file_size: 3200000, // 3.2MB
        charts_count: 22,
        download_count: 1,
        generation_time: 52,
        components: ['cover', 'data_overview', 'charts', 'recommendations']
      },
      {
        id: 'report_003',
        task_id: 'task_125',
        title: null, // 使用默认标题
        template: 'summary',
        format: 'docx',
        status: 'generating',
        created_at: '2024-01-14T09:20:00Z',
        file_size: 0,
        charts_count: 8,
        download_count: 0,
        generation_time: 0,
        components: ['summary', 'charts']
      }
    ]
  } catch (error) {
    console.error('加载报告列表失败:', error)
    ElMessage.error('加载报告列表失败')
  } finally {
    loading.value = false
  }
}

const refreshReports = () => {
  loadReports()
  ElMessage.success('报告列表已刷新')
}

const handleSelectionChange = (selection) => {
  selectedReports.value = selection
}

const handleRowClick = (row) => {
  selectedReport.value = row
  emit('report-selected', row)
}

const downloadReport = async (report) => {
  if (report.status !== 'completed') {
    ElMessage.warning('报告尚未生成完成')
    return
  }

  downloadingReports.value[report.id] = true

  try {
    const response = await fetch(`http://localhost:8000/api/download-comprehensive-report/${report.task_id}?report_id=${report.id}`)
    
    if (!response.ok) {
      throw new Error('下载失败')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${report.title || getDefaultTitle(report)}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    // 更新下载次数
    report.download_count = (report.download_count || 0) + 1

    ElMessage.success('报告下载成功')
  } catch (error) {
    console.error('下载报告失败:', error)
    ElMessage.error('下载失败')
  } finally {
    downloadingReports.value[report.id] = false
  }
}

const handleBatchAction = async (command) => {
  if (selectedReports.value.length === 0) {
    ElMessage.warning('请先选择报告')
    return
  }

  switch (command) {
    case 'download':
      await batchDownload()
      break
    case 'delete':
      await batchDelete()
      break
    case 'export':
      exportReportsList()
      break
  }
}

const batchDownload = async () => {
  const completedReports = selectedReports.value.filter(r => r.status === 'completed')
  
  if (completedReports.length === 0) {
    ElMessage.warning('没有可下载的报告')
    return
  }

  ElNotification({
    title: '批量下载',
    message: `开始下载 ${completedReports.length} 个报告...`,
    type: 'info'
  })

  for (const report of completedReports) {
    try {
      await downloadReport(report)
      await new Promise(resolve => setTimeout(resolve, 500)) // 避免请求过快
    } catch (error) {
      console.error(`下载报告 ${report.id} 失败:`, error)
    }
  }

  ElNotification({
    title: '批量下载完成',
    message: `已完成 ${completedReports.length} 个报告的下载`,
    type: 'success'
  })
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedReports.value.length} 个报告吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 模拟删除操作
    const idsToDelete = selectedReports.value.map(r => r.id)
    reports.value = reports.value.filter(r => !idsToDelete.includes(r.id))
    selectedReports.value = []

    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const exportReportsList = () => {
  const exportData = {
    exportTime: new Date().toISOString(),
    totalReports: reports.value.length,
    reports: reports.value.map(report => ({
      id: report.id,
      task_id: report.task_id,
      title: report.title || getDefaultTitle(report),
      template: getTemplateName(report.template),
      status: getStatusText(report.status),
      created_at: report.created_at,
      file_size: formatFileSize(report.file_size),
      charts_count: report.charts_count,
      download_count: report.download_count
    }))
  }

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
    type: 'application/json' 
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `reports_list_${Date.now()}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('报告列表导出成功')
}

const handleRowAction = async (command, row) => {
  switch (command) {
    case 'preview':
      // 实现报告预览
      ElMessage.info('预览功能开发中...')
      break
    case 'rename':
      renameForm.value.title = row.title || getDefaultTitle(row)
      selectedReport.value = row
      renameDialogVisible.value = true
      break
    case 'duplicate':
      await duplicateReport(row)
      break
    case 'details':
      selectedReport.value = row
      detailDialogVisible.value = true
      break
    case 'delete':
      await deleteReport(row)
      break
  }
}

const duplicateReport = async (report) => {
  try {
    // 模拟复制报告
    const newReport = {
      ...report,
      id: `report_${Date.now()}`,
      title: `${report.title || getDefaultTitle(report)} - 副本`,
      created_at: new Date().toISOString(),
      download_count: 0
    }
    
    reports.value.unshift(newReport)
    ElMessage.success('报告复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const deleteReport = async (report) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告 "${report.title || getDefaultTitle(report)}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    reports.value = reports.value.filter(r => r.id !== report.id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const confirmRename = () => {
  if (selectedReport.value) {
    selectedReport.value.title = renameForm.value.title
    ElMessage.success('重命名成功')
  }
  renameDialogVisible.value = false
}

const regenerateReport = async (report) => {
  try {
    await ElMessageBox.confirm(
      '确定要重新生成此报告吗？',
      '确认重新生成',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 设置状态为生成中
    report.status = 'generating'
    
    ElMessage.success('已启动重新生成')
    detailDialogVisible.value = false
  } catch {
    // 用户取消
  }
}

const createNewReport = () => {
  emit('new-report')
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}

// 模板管理方法
const editTemplate = (template) => {
  ElMessage.info('模板编辑功能开发中...')
}

const useTemplate = (template) => {
  emit('template-selected', template)
  ElMessage.success(`已选择模板: ${template.name}`)
}

const duplicateTemplate = (template) => {
  const newTemplate = {
    ...template,
    id: Date.now(),
    name: `${template.name} - 副本`,
    usage_count: 0,
    updated_at: new Date().toISOString()
  }
  reportTemplates.value.push(newTemplate)
  ElMessage.success('模板复制成功')
}

const deleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    reportTemplates.value = reportTemplates.value.filter(t => t.id !== template.id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const createTemplate = () => {
  ElMessage.info('创建模板功能开发中...')
}

const importTemplate = () => {
  ElMessage.info('导入模板功能开发中...')
}

// 工具方法
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN')
  } catch (e) {
    return timeStr
  }
}

const formatDate = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleDateString('zh-CN')
  } catch (e) {
    return timeStr
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const getDefaultTitle = (report) => {
  return `分析报告_${report.task_id}_${formatDate(report.created_at)}`
}

const getStatusType = (status) => {
  const types = {
    'completed': 'success',
    'generating': 'warning',
    'failed': 'danger',
    'pending': 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'completed': '已完成',
    'generating': '生成中',
    'failed': '失败',
    'pending': '等待中'
  }
  return texts[status] || status
}

const getTemplateName = (template) => {
  const names = {
    'comprehensive': '综合报告',
    'summary': '摘要报告',
    'technical': '技术报告',
    'executive': '管理报告'
  }
  return names[template] || template
}

const getComponentName = (component) => {
  const names = {
    'cover': '封面',
    'summary': '摘要',
    'data_overview': '数据概览',
    'charts': '图表',
    'ai_analysis': 'AI分析',
    'recommendations': '建议',
    'appendix': '附录'
  }
  return names[component] || component
}
</script>

<style scoped>
.report-manager {
  height: 100%;
}

.manager-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.manager-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.reports-badge {
  margin-right: 8px;
}

/* 工具栏样式 */
.manager-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--el-border-color-light);
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 200px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 表格样式 */
.reports-table {
  flex: 1;
  overflow: hidden;
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.report-type-icon {
  color: var(--el-color-primary);
}

.title-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.report-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.meta-item {
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

/* 模板管理样式 */
.template-management {
  margin-top: 24px;
}

.template-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.template-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition: all 0.2s;
}

.template-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.template-preview {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary-light-8);
  border-radius: 6px;
}

.template-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.template-description {
  margin: 0 0 4px 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.template-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.template-actions {
  display: flex;
  gap: 4px;
}

.template-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 统计信息样式 */
.statistics-panel {
  margin-top: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-card {
  text-align: center;
  padding: 16px;
  background: var(--el-bg-color);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-light);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--el-color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 对话框样式 */
.report-details {
  padding: 16px 0;
}

.component-tag {
  margin: 2px 4px 2px 0;
}

.detail-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .manager-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .template-list {
    grid-template-columns: 1fr;
  }
  
  .template-item {
    flex-direction: column;
    text-align: center;
  }
  
  .template-actions {
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style> 
<template>
  <div class="reports-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分析报告管理</span>
        </div>
      </template>
      
      <el-button type="primary" @click="generateAIReport" :loading="generatingReport">
        生成AI分析报告
      </el-button>
      
      <el-table :data="reports" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="title" label="报告标题" min-width="200">
          <template #default="scope">
            <el-link type="primary" @click="viewReport(scope.row)">
              {{ scope.row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="filename" label="源文件" width="180"></el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewReport(scope.row)">
              查看
            </el-button>
            <el-button type="success" size="small" @click="downloadReport(scope.row)">
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 报告查看器 -->
    <el-dialog v-model="reportViewVisible" :title="currentReport?.title" width="90%">
      <div class="report-viewer" v-if="currentReport">
        <div class="report-content" v-html="currentReport.content"></div>
      </div>
      
      <template #footer>
        <el-button @click="reportViewVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- AI报告生成对话框 -->
    <el-dialog v-model="aiReportDialogVisible" title="生成AI分析报告" width="50%">
      <el-form :model="aiReportForm" label-width="120px">
        <el-form-item label="选择数据文件">
          <el-select v-model="aiReportForm.fileId" placeholder="请选择数据文件" style="width: 100%">
            <el-option
              v-for="file in uploadedFiles"
              :key="file.id"
              :label="file.filename"
              :value="file.id"
            >
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="aiReportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmGenerateAIReport" :loading="generatingReport">
          生成报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'Reports',
  data() {
    return {
      reports: [],
      loading: false,
      reportViewVisible: false,
      currentReport: null,
      aiReportDialogVisible: false,
      generatingReport: false,
      aiReportForm: {
        fileId: ''
      },
      uploadedFiles: []
    }
  },
  methods: {
    async loadReports() {
      this.loading = true
      try {
        const response = await axios.get('/api/deepseek/reports')
        this.reports = response.data.reports || []
      } catch (error) {
        console.error('Failed to load reports:', error)
        ElMessage.error('加载报告列表失败')
      } finally {
        this.loading = false
      }
    },
    
    async loadUploadedFiles() {
      try {
        const response = await axios.get('/api/files/list')
        this.uploadedFiles = response.data.files || []
      } catch (error) {
        console.error('Failed to load files:', error)
      }
    },
    
    generateAIReport() {
      this.aiReportDialogVisible = true
    },
    
    async confirmGenerateAIReport() {
      if (!this.aiReportForm.fileId) {
        ElMessage.warning('请选择数据文件')
        return
      }
      
      this.generatingReport = true
      try {
        const response = await axios.post('/api/deepseek/generate', {
          file_id: this.aiReportForm.fileId
        })
        
        ElMessage.success('AI报告生成任务已启动')
        this.aiReportDialogVisible = false
        this.aiReportForm.fileId = ''
        
        setTimeout(() => {
          this.loadReports()
        }, 2000)
        
      } catch (error) {
        console.error('Generate report error:', error)
        ElMessage.error('生成报告失败')
      } finally {
        this.generatingReport = false
      }
    },
    
    async viewReport(report) {
      try {
        const response = await axios.get(`/api/deepseek/report/${report.id}`)
        this.currentReport = response.data
        this.reportViewVisible = true
      } catch (error) {
        console.error('Failed to load report:', error)
        ElMessage.error('加载报告详情失败')
      }
    },
    
    async downloadReport(report) {
      try {
        const response = await axios.get(`/api/deepseek/download/${report.id}`, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${report.title}.html`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('报告下载开始')
      } catch (error) {
        console.error('Download error:', error)
        ElMessage.error('下载失败')
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  },
  
  mounted() {
    this.loadReports()
    this.loadUploadedFiles()
  }
}
</script>

<style scoped>
.reports-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.report-content {
  line-height: 1.8;
  color: #606266;
  padding: 20px;
}
</style> 
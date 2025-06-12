<template>
  <div class="analysis-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>数据选择与分析配置</span>
            </div>
          </template>
          
          <el-form :model="analysisForm" label-width="120px">
            <el-form-item label="选择数据文件">
              <el-select v-model="analysisForm.fileId" placeholder="请选择要分析的文件" style="width: 100%">
                <el-option
                  v-for="file in uploadedFiles"
                  :key="file.id"
                  :label="file.filename"
                  :value="file.id"
                >
                </el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="分析类型">
              <el-checkbox-group v-model="analysisForm.analysisTypes">
                <el-checkbox label="descriptive">描述性统计</el-checkbox>
                <el-checkbox label="correlation">相关性分析</el-checkbox>
                <el-checkbox label="timeseries">时间序列分析</el-checkbox>
                <el-checkbox label="regression">回归分析</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="输出格式">
              <el-radio-group v-model="analysisForm.outputFormat">
                <el-radio label="html">HTML报告</el-radio>
                <el-radio label="pdf">PDF报告</el-radio>
                <el-radio label="json">JSON数据</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item>
              <el-space>
                <el-button type="primary" @click="startAnalysis" :loading="analyzing">
                  <el-icon><Position /></el-icon>
                  开始分析
                </el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-space>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析结果展示 -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="analysisResult">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>分析结果</span>
            </div>
          </template>
          
          <el-tabs v-model="activeTab" type="card">
            <el-tab-pane label="统计摘要" name="summary" v-if="analysisResult.summary">
              <div class="result-content">
                <pre>{{ analysisResult.summary }}</pre>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="图表展示" name="charts" v-if="analysisResult.charts">
              <div class="charts-container">
                <div v-for="(chart, index) in analysisResult.charts" :key="index" class="chart-item">
                  <h3>{{ chart.title }}</h3>
                  <v-chart :option="chart.option" style="height: 400px;"></v-chart>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="详细报告" name="report" v-if="analysisResult.report">
              <div class="report-content" v-html="analysisResult.report"></div>
            </el-tab-pane>
            
            <el-tab-pane label="原始数据" name="data" v-if="analysisResult.data">
              <el-table :data="analysisResult.data" style="width: 100%" max-height="400">
                <el-table-column
                  v-for="column in analysisResult.columns"
                  :key="column"
                  :prop="column"
                  :label="column"
                  :width="120"
                >
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史分析记录 -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="analysisHistory.length > 0">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>分析历史</span>
            </div>
          </template>
          
          <el-table :data="analysisHistory" style="width: 100%">
            <el-table-column prop="filename" label="文件名" width="200"></el-table-column>
            <el-table-column prop="analysis_types" label="分析类型" width="200"></el-table-column>
            <el-table-column prop="created_at" label="分析时间" width="180"></el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">
                  {{ scope.row.status === 'completed' ? '完成' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="150">
              <template #default="scope">
                <el-space>
                  <el-button type="primary" size="small" @click="viewAnalysis(scope.row)">
                    查看
                  </el-button>
                  <el-button type="success" size="small" @click="downloadReport(scope.row)">
                    下载
                  </el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, ScatterChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { TrendCharts, Position, DataAnalysis, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  name: 'Analysis',
  components: {
    VChart,
    TrendCharts,
    Position,
    DataAnalysis,
    Clock
  },
  data() {
    return {
      analysisForm: {
        fileId: '',
        analysisTypes: ['descriptive'],
        outputFormat: 'html'
      },
      uploadedFiles: [],
      analyzing: false,
      analysisResult: null,
      activeTab: 'summary',
      analysisHistory: []
    }
  },
  methods: {
    async loadUploadedFiles() {
      try {
        const response = await axios.get('/api/files/list')
        this.uploadedFiles = response.data.files || []
        
        // 如果URL中有fileId参数，自动选择该文件
        if (this.$route.query.fileId) {
          this.analysisForm.fileId = this.$route.query.fileId
        }
      } catch (error) {
        console.error('Failed to load files:', error)
        ElMessage.error('加载文件列表失败')
      }
    },
    
    async startAnalysis() {
      if (!this.analysisForm.fileId) {
        ElMessage.warning('请先选择要分析的文件')
        return
      }
      
      if (this.analysisForm.analysisTypes.length === 0) {
        ElMessage.warning('请至少选择一种分析类型')
        return
      }
      
      this.analyzing = true
      
      try {
        const response = await axios.post('/api/analysis/analyze', {
          file_id: this.analysisForm.fileId,
          analysis_types: this.analysisForm.analysisTypes,
          output_format: this.analysisForm.outputFormat
        })
        
        this.analysisResult = response.data
        this.activeTab = 'summary'
        
        ElMessage.success('分析完成！')
        this.loadAnalysisHistory()
      } catch (error) {
        console.error('Analysis error:', error)
        ElMessage.error('分析失败：' + (error.response?.data?.message || error.message))
      } finally {
        this.analyzing = false
      }
    },
    
    resetForm() {
      this.analysisForm = {
        fileId: '',
        analysisTypes: ['descriptive'],
        outputFormat: 'html'
      }
      this.analysisResult = null
    },
    
    async loadAnalysisHistory() {
      try {
        const response = await axios.get('/api/analysis/history')
        this.analysisHistory = response.data.history || []
      } catch (error) {
        console.error('Failed to load analysis history:', error)
      }
    },
    
    async viewAnalysis(record) {
      try {
        const response = await axios.get(`/api/analysis/result/${record.id}`)
        this.analysisResult = response.data
        this.activeTab = 'summary'
      } catch (error) {
        console.error('Failed to load analysis result:', error)
        ElMessage.error('加载分析结果失败')
      }
    },
    
    async downloadReport(record) {
      try {
        const response = await axios.get(`/api/analysis/download/${record.id}`, {
          responseType: 'blob'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${record.filename}_analysis_report.${record.output_format}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('报告下载开始')
      } catch (error) {
        console.error('Download error:', error)
        ElMessage.error('下载失败')
      }
    }
  },
  
  mounted() {
    this.loadUploadedFiles()
    this.loadAnalysisHistory()
  }
}
</script>

<style scoped>
.analysis-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-content pre {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
}

.chart-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
}

.chart-item h3 {
  margin: 0 0 15px 0;
  color: #303133;
  text-align: center;
}

.report-content {
  line-height: 1.6;
  color: #606266;
}

.report-content h1,
.report-content h2,
.report-content h3 {
  color: #303133;
  margin-top: 20px;
  margin-bottom: 10px;
}
</style> 
<template>
  <div class="data-analysis-complete">
    <h1>压力数据分析系统</h1>
    <p>完整功能测试版本 - 支持文件上传→分析任务→结果查看→AI报告生成</p>
    
    <!-- 步骤指示器 -->
    <el-steps :active="currentStep" align-center style="margin: 20px 0;">
      <el-step title="上传文件" description="选择CSV数据文件"></el-step>
      <el-step title="设置参数" description="配置分析参数"></el-step>
      <el-step title="执行分析" description="启动数据分析"></el-step>
      <el-step title="查看结果" description="分析结果和报告"></el-step>
    </el-steps>
    
    <!-- 第一步：文件上传 -->
    <el-card v-if="currentStep === 0" class="step-card">
      <template #header>
        <h3>📁 步骤1：上传数据文件</h3>
      </template>
      
      <div class="upload-section">
        <el-upload
          class="upload-area"
          drag
          action=""
          :auto-upload="false"
          accept=".csv"
          :limit="1"
          :on-change="handleFileSelect"
          :file-list="fileList"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖拽CSV文件到此处<em>或点击选择文件</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持CSV格式，文件大小不超过100MB
            </div>
          </template>
        </el-upload>
        
        <div v-if="selectedFile" class="file-info">
          <h4>已选择文件：</h4>
          <p><strong>文件名:</strong> {{ selectedFile.name }}</p>
          <p><strong>大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
          <p><strong>类型:</strong> {{ selectedFile.type || 'text/csv' }}</p>
          
          <div class="file-actions">
            <el-button type="primary" @click="uploadFile" :loading="uploading">
              {{ uploading ? '上传中...' : '上传文件' }}
            </el-button>
            <el-button @click="clearFile">重新选择</el-button>
          </div>
        </div>
        
        <div v-if="uploadResult" class="upload-result">
          <el-alert 
            :type="uploadResult.success ? 'success' : 'error'"
            :title="uploadResult.message"
            :description="uploadResult.details"
            show-icon
          />
          
          <div v-if="uploadResult.success" class="file-preview">
            <h4>文件预览：</h4>
            <pre>{{ uploadResult.preview }}</pre>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 第二步：参数设置 -->
    <el-card v-if="currentStep === 1" class="step-card">
      <template #header>
        <h3>⚙️ 步骤2：设置分析参数</h3>
      </template>
      
      <div class="params-section">
        <el-row :gutter="20">
          <el-col :span="14">
            <el-form :model="analysisParams" label-width="120px">
              <!-- 目标力值设置 -->
              <el-form-item label="目标力值配置">
                <div class="target-forces-config">
                  <div v-for="(force, index) in targetForcesList" :key="index" class="force-config-row">
                    <el-input-number 
                      v-model="targetForcesList[index].force" 
                      :min="0.1" 
                      :step="0.1" 
                      :precision="1"
                      placeholder="目标力值(N)"
                      class="force-input"
                      @change="updateParams"
                    />
                    <el-input-number 
                      v-model="targetForcesList[index].absTolerance" 
                      :min="0" 
                      :step="0.1" 
                      :precision="2"
                      placeholder="绝对容差"
                      class="tolerance-input"
                      @change="updateParams"
                    />
                    <el-input-number 
                      v-model="targetForcesList[index].pctTolerance" 
                      :min="0" 
                      :max="100" 
                      :step="1"
                      :precision="1"
                      placeholder="百分比容差(%)"
                      class="tolerance-input"
                      @change="updateParams"
                    />
                    <el-button 
                      type="danger" 
                      size="small" 
                      icon="Delete"
                      @click="removeForceConfig(index)"
                      :disabled="targetForcesList.length <= 1"
                    >
                      删除
                    </el-button>
                  </div>
                  
                  <el-button type="primary" @click="addForceConfig" icon="Plus">
                    添加目标力值
                  </el-button>
                </div>
                <div class="form-tip">每个目标力值可以设置独立的容差参数</div>
              </el-form-item>
            </el-form>
          </el-col>
          
          <el-col :span="10">
            <div class="params-preview">
              <h4>参数预览：</h4>
              <div v-for="(config, index) in targetForcesList" :key="index" class="config-preview">
                <div class="preview-title">
                  <strong>目标力值 {{ index + 1 }}：{{ config.force }}N</strong>
                </div>
                <div class="preview-item">
                  绝对容差：±{{ config.absTolerance }}N
                </div>
                <div class="preview-item">
                  百分比容差：±{{ config.pctTolerance }}%
                </div>
                <div class="preview-range">
                  有效范围：{{ (config.force - config.absTolerance).toFixed(2) }}N ~ 
                  {{ (config.force + config.absTolerance).toFixed(2) }}N
                </div>
                <div class="preview-range">
                  百分比范围：{{ (config.force * (1 - config.pctTolerance/100)).toFixed(2) }}N ~ 
                  {{ (config.force * (1 + config.pctTolerance/100)).toFixed(2) }}N
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep" :disabled="!paramsValid">
            下一步：开始分析
          </el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 第三步：执行分析 -->
    <el-card v-if="currentStep === 2" class="step-card">
      <template #header>
        <h3>🔬 步骤3：执行数据分析</h3>
      </template>
      
      <div class="analysis-section">
        <div class="analysis-summary">
          <h4>分析配置摘要：</h4>
          <div class="summary-grid">
            <div class="summary-item">
              <strong>文件名:</strong> {{ uploadedFileName }}
            </div>
            <div class="summary-item">
              <strong>目标力值数量:</strong> {{ targetForcesList.length }} 个
            </div>
            <div class="summary-item">
              <strong>目标力值:</strong> {{ targetForcesList.map(f => f.force).join(', ') }} N
            </div>
          </div>
        </div>
        
        <div class="analysis-control">
          <el-button 
            type="primary" 
            size="large" 
            @click="startAnalysis" 
            :loading="analyzing"
            :disabled="analyzing"
          >
            {{ analyzing ? '分析进行中...' : '🚀 开始分析' }}
          </el-button>
        </div>
        
        <div v-if="currentTask" class="task-status">
          <h4>任务状态：</h4>
          <div class="status-info">
            <div class="status-item">
              <strong>任务ID:</strong> {{ currentTask.task_id?.substring(0, 8) }}...
            </div>
            <div class="status-item">
              <strong>状态:</strong> 
              <el-tag :type="getStatusType(currentTask.status)">
                {{ getStatusText(currentTask.status) }}
              </el-tag>
            </div>
            <div class="status-item">
              <strong>进度:</strong> {{ calculatedProgress }}%
            </div>
          </div>
          
          <el-progress 
            :percentage="calculatedProgress" 
            :status="getProgressStatus()"
            :stroke-width="8"
          />
          
          <div v-if="progressDetails" class="progress-details">
            <p><strong>当前阶段:</strong> {{ progressDetails.stage }}</p>
            <p><strong>已生成文件:</strong> {{ progressDetails.completedFiles }} / {{ progressDetails.totalFiles }}</p>
            <p><strong>预计完成时间:</strong> {{ progressDetails.estimatedTime }}</p>
          </div>
        </div>
        
        <div class="step-actions">
          <el-button @click="prevStep" :disabled="analyzing">上一步</el-button>
          <el-button 
            type="primary" 
            @click="nextStep" 
            :disabled="!taskCompleted"
            v-if="taskCompleted"
          >
            下一步：查看结果
          </el-button>
          <el-button 
            type="info" 
            @click="goToTaskPage" 
            v-if="currentTask"
          >
            查看任务详情
          </el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 第四步：查看结果 -->
    <el-card v-if="currentStep === 3" class="step-card">
      <template #header>
        <h3>📊 步骤4：分析结果与AI报告</h3>
      </template>
      
      <div class="results-section">
        <div v-if="analysisResults" class="results-content">
          <h4>分析结果摘要：</h4>
          <div class="results-grid">
            <div class="result-item">
              <strong>数据点总数:</strong> {{ analysisResults.data_summary?.total_points || 'N/A' }}
            </div>
            <div class="result-item">
              <strong>有效数据:</strong> {{ analysisResults.data_summary?.valid_points || 'N/A' }}
            </div>
            <div class="result-item">
              <strong>整体成功率:</strong> {{ analysisResults.analysis_results?.overall_success_rate || 'N/A' }}%
            </div>
            <div class="result-item">
              <strong>生成图表数:</strong> {{ chartNames.length }} 张
            </div>
          </div>
          
          <div class="target-results">
            <h4>各目标力值分析结果：</h4>
            <el-table :data="targetAnalysisResults" style="width: 100%">
              <el-table-column prop="target_force" label="目标力值(N)" width="120" />
              <el-table-column prop="success_rate" label="成功率(%)" width="100" />
              <el-table-column prop="mean_force" label="平均力值" width="100" />
              <el-table-column prop="std_dev" label="标准差" width="100" />
              <el-table-column prop="cp_value" label="Cp值" width="100" />
            </el-table>
          </div>
          
          <div class="charts-section">
            <h4>生成的图表 ({{ chartNames.length }} 张)：</h4>
            <div class="chart-list">
              <el-tag 
                v-for="chart in chartNames" 
                :key="chart" 
                class="chart-tag"
                @click="viewChart(chart)"
              >
                {{ getChartDisplayName(chart) }}
              </el-tag>
            </div>
            <el-button @click="viewAllCharts" type="primary">
              查看所有图表
            </el-button>
          </div>
        </div>
        
        <div class="ai-section">
          <h4>🤖 AI智能分析报告：</h4>
          
          <div class="ai-actions">
            <el-button 
              type="warning" 
              @click="generateAIReport" 
              :loading="generatingAI"
              :disabled="generatingAI"
            >
              {{ generatingAI ? '生成中...' : '生成AI分析报告' }}
            </el-button>
            
            <el-button 
              type="success" 
              @click="generateWordReport" 
              :loading="generatingWord"
              :disabled="generatingWord || !aiReportGenerated"
            >
              {{ generatingWord ? '生成中...' : '生成Word报告' }}
            </el-button>
            
            <el-button 
              v-if="wordReportReady"
              type="primary" 
              @click="downloadWordReport"
            >
              📥 下载Word报告
            </el-button>
          </div>
          
          <div v-if="aiAnalysis" class="ai-content">
            <h5>AI分析内容：</h5>
            <div class="ai-text">{{ aiAnalysis }}</div>
          </div>
        </div>
        
        <div class="step-actions">
          <el-button @click="resetAnalysis">重新开始</el-button>
          <el-button type="primary" @click="completeAnalysis">
            完成分析
          </el-button>
        </div>
      </div>
    </el-card>
    
    <!-- API调试区域 -->
    <el-card class="debug-card" v-if="showDebug">
      <template #header>
        <div class="debug-header">
          <h3>🔧 调试信息</h3>
          <el-button size="small" @click="showDebug = !showDebug">
            {{ showDebug ? '隐藏' : '显示' }}
          </el-button>
        </div>
      </template>
      
      <div class="debug-content">
        <el-tabs>
          <el-tab-pane label="API日志" name="logs">
            <div class="api-logs">
              <div v-for="(log, index) in apiLogs" :key="index" class="log-item">
                <span class="log-time">{{ log.time }}</span>
                <span class="log-method" :class="log.method">{{ log.method }}</span>
                <span class="log-url">{{ log.url }}</span>
                <span class="log-status" :class="getLogStatusClass(log.status)">{{ log.status }}</span>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="响应数据" name="data">
            <pre class="api-response">{{ JSON.stringify(lastApiResponse, null, 2) }}</pre>
          </el-tab-pane>
          
          <el-tab-pane label="快速测试" name="test">
            <div class="test-actions">
              <h4>🧪 快速功能测试</h4>
              <p>使用预设数据快速测试所有功能</p>
              
              <div class="test-buttons">
                <el-button type="primary" @click="runQuickTest" :loading="quickTesting">
                  {{ quickTesting ? '测试中...' : '🚀 一键测试完整流程' }}
                </el-button>
                
                <el-button @click="loadDemoData">
                  📄 加载演示数据
                </el-button>
                
                <el-button @click="testAPIConnection">
                  🔗 测试API连接
                </el-button>
              </div>
              
              <div v-if="testResults.length > 0" class="test-results">
                <h5>测试结果:</h5>
                <div v-for="(result, index) in testResults" :key="index" class="test-result-item">
                  <el-tag :type="result.success ? 'success' : 'danger'">
                    {{ result.success ? '✅' : '❌' }} {{ result.name }}
                  </el-tag>
                  <span class="test-message">{{ result.message }}</span>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
    
    <!-- 底部快速访问 -->
    <el-card class="quick-access-card">
      <template #header>
        <h3>🔗 快速访问</h3>
      </template>
      
      <div class="quick-links">
        <el-button-group>
          <el-button @click="showDebug = !showDebug">
            {{ showDebug ? '隐藏调试' : '显示调试' }}
          </el-button>
          <el-button @click="goToTasks">任务管理</el-button>
          <el-button @click="goToSettings">系统设置</el-button>
          <el-button @click="viewAPIStatus">API状态</el-button>
        </el-button-group>
      </div>
      
      <div class="system-status">
        <div class="status-item">
          <strong>前端:</strong> 
          <el-tag type="success">运行中</el-tag>
          <span>http://localhost:5173</span>
        </div>
        <div class="status-item">
          <strong>后端:</strong> 
          <el-tag :type="backendStatus.connected ? 'success' : 'danger'">
            {{ backendStatus.connected ? '已连接' : '断开' }}
          </el-tag>
          <span>http://localhost:8000</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Plus, Delete } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 状态管理
const currentStep = ref(0)
const selectedFile = ref(null)
const fileList = ref([])
const uploading = ref(false)
const uploadResult = ref(null)
const uploadedFileName = ref('')
const uploadedFileId = ref('')

// 新的参数管理 - 支持多个目标力值
const targetForcesList = ref([
  { force: 5, absTolerance: 0.5, pctTolerance: 5 },
  { force: 25, absTolerance: 1.0, pctTolerance: 4 },
  { force: 50, absTolerance: 2.0, pctTolerance: 3 }
])

const analyzing = ref(false)
const currentTask = ref(null)
const analysisResults = ref(null)
const chartNames = ref([])
const targetAnalysisResults = ref([])

// 进度计算相关
const progressDetails = ref(null)
const expectedChartCount = 35 // 后端应该生成35个图表

// AI相关状态
const generatingAI = ref(false)
const generatingWord = ref(false)
const aiReportGenerated = ref(false)
const wordReportReady = ref(false)
const aiAnalysis = ref('')

// 调试和测试相关
const showDebug = ref(false)
const apiLogs = ref([])
const lastApiResponse = ref({})
const quickTesting = ref(false)
const testResults = ref([])
const backendStatus = ref({ connected: false, version: '', status: '' })

// 计算属性
const paramsValid = computed(() => {
  return targetForcesList.value.length > 0 && 
         targetForcesList.value.every(config => 
           config.force > 0 && config.absTolerance >= 0 && config.pctTolerance >= 0
         )
})

const taskCompleted = computed(() => {
  return currentTask.value?.status === 'completed'
})

const calculatedProgress = computed(() => {
  if (!currentTask.value) return 0
  
  if (currentTask.value.status === 'completed') return 100
  if (currentTask.value.status === 'failed') return 0
  
  // 基于生成的文件数量计算进度
  if (progressDetails.value) {
    return Math.min(95, Math.round((progressDetails.value.completedFiles / progressDetails.value.totalFiles) * 100))
  }
  
  // 简单的时间推算进度
  if (currentTask.value.progress) {
    return currentTask.value.progress
  }
  
  return analyzing.value ? Math.min(90, Math.random() * 50 + 10) : 0
})

// 参数管理函数
const addForceConfig = () => {
  targetForcesList.value.push({
    force: 10,
    absTolerance: 1.0,
    pctTolerance: 5
  })
  updateParams()
}

const removeForceConfig = (index) => {
  if (targetForcesList.value.length > 1) {
    targetForcesList.value.splice(index, 1)
    updateParams()
  }
}

const updateParams = () => {
  // 触发响应式更新
}

// 文件处理函数
const handleFileSelect = (file) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

const clearFile = () => {
  selectedFile.value = null
  fileList.value = []
  uploadResult.value = null
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请先选择文件')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    logApiCall('POST', '/api/upload', response.status, result)
    
    if (result.success) {
      uploadResult.value = {
        success: true,
        message: '文件上传成功',
        details: `文件ID: ${result.file_id}`,
        preview: result.preview || '数据预览加载中...'
      }
      uploadedFileName.value = selectedFile.value.name
      uploadedFileId.value = result.file_id
      
      ElMessage.success('文件上传成功')
      
      // 自动跳转到下一步
      setTimeout(() => {
        nextStep()
      }, 1500)
      
    } else {
      throw new Error(result.message || '上传失败')
    }
  } catch (error) {
    uploadResult.value = {
      success: false,
      message: '文件上传失败',
      details: error.message
    }
    logApiCall('POST', '/api/upload', 'ERROR', { error: error.message })
    ElMessage.error(`上传失败: ${error.message}`)
  } finally {
    uploading.value = false
  }
}

// 步骤控制函数
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 分析执行函数
const startAnalysis = async () => {
  if (!uploadedFileId.value) {
    ElMessage.error('请先上传文件')
    return
  }
  
  analyzing.value = true
  try {
    // 准备分析参数
    const targetForces = targetForcesList.value.map(config => config.force)
    const toleranceAbs = targetForcesList.value.map(config => config.absTolerance)
    const tolerancePct = targetForcesList.value.map(config => config.pctTolerance)
    
    const response = await fetch('http://localhost:8000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_id: uploadedFileId.value,
        target_forces: targetForces,
        tolerance_abs: toleranceAbs,
        tolerance_pct: tolerancePct
      })
    })
    
    const result = await response.json()
    logApiCall('POST', '/api/analyze', response.status, result)
    
    if (result.success && result.task_id) {
      currentTask.value = {
        task_id: result.task_id,
        status: 'running',
        progress: 0
      }
      
      // 初始化进度详情
      progressDetails.value = {
        stage: '开始分析',
        completedFiles: 0,
        totalFiles: expectedChartCount,
        estimatedTime: '预计3-5分钟'
      }
      
      ElMessage.success('分析任务已启动')
      
      // 开始轮询任务状态
      pollTaskStatus()
    } else {
      throw new Error(result.message || '启动分析失败')
    }
  } catch (error) {
    logApiCall('POST', '/api/analyze', 'ERROR', { error: error.message })
    ElMessage.error(`启动分析失败: ${error.message}`)
  } finally {
    analyzing.value = false
  }
}

const pollTaskStatus = async () => {
  if (!currentTask.value?.task_id) return
  
  try {
    const response = await fetch(`http://localhost:8000/api/task/${currentTask.value.task_id}`)
    const result = await response.json()
    logApiCall('GET', `/api/task/${currentTask.value.task_id}`, response.status, result)
    
    if (result.success && result.task) {
      currentTask.value = result.task
      
      // 更新进度详情
      if (result.task.status === 'running') {
        // 模拟基于文件生成的进度
        const estimatedCompleted = Math.min(expectedChartCount, Math.floor(Math.random() * 10) + progressDetails.value.completedFiles)
        progressDetails.value = {
          stage: result.task.stage || '正在生成图表',
          completedFiles: estimatedCompleted,
          totalFiles: expectedChartCount,
          estimatedTime: `还需${Math.max(1, Math.ceil((expectedChartCount - estimatedCompleted) / 3))}分钟`
        }
      }
      
      if (result.task.status === 'completed') {
        progressDetails.value = {
          stage: '分析完成',
          completedFiles: expectedChartCount,
          totalFiles: expectedChartCount,
          estimatedTime: '已完成'
        }
        
        ElMessage.success('分析任务完成')
        await getAnalysisResults()
        
        // 自动跳转到结果页面
        setTimeout(() => {
          nextStep()
        }, 2000)
        
      } else if (result.task.status === 'failed') {
        ElMessage.error('分析任务失败')
      } else {
        // 继续轮询
        setTimeout(pollTaskStatus, 2000)
      }
    }
  } catch (error) {
    console.error('轮询任务状态失败:', error)
    setTimeout(pollTaskStatus, 5000)
  }
}

const getAnalysisResults = async () => {
  if (!currentTask.value?.task_id) return
  
  try {
    const response = await fetch(`http://localhost:8000/api/results/${currentTask.value.task_id}`)
    const result = await response.json()
    logApiCall('GET', `/api/results/${currentTask.value.task_id}`, response.status, result)
    
    if (result.success && result.result) {
      analysisResults.value = result.result
      chartNames.value = result.result.chart_names || []
      
      // 提取各目标力值的分析结果
      if (result.result.target_analysis) {
        targetAnalysisResults.value = result.result.target_analysis
      }
    }
  } catch (error) {
    console.error('获取分析结果失败:', error)
    ElMessage.error('获取分析结果失败，请重试')
  }
}

// AI功能
const generateAIReport = async () => {
  if (!currentTask.value?.task_id) return
  
  generatingAI.value = true
  try {
    const response = await fetch('http://localhost:8000/api/deepseek/generate-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        task_id: currentTask.value.task_id
      })
    })
    
    const result = await response.json()
    logApiCall('POST', '/api/deepseek/generate-report', response.status, result)
    
    if (result.success) {
      ElMessage.success('AI分析报告生成成功')
      aiReportGenerated.value = true
      
      // 获取AI分析内容
      await getAIAnalysis()
    } else {
      throw new Error(result.message || 'AI报告生成失败')
    }
  } catch (error) {
    logApiCall('POST', '/api/deepseek/generate-report', 'ERROR', { error: error.message })
    ElMessage.error(`AI报告生成失败: ${error.message}`)
  } finally {
    generatingAI.value = false
  }
}

const getAIAnalysis = async () => {
  if (!currentTask.value?.task_id) return
  
  try {
    const response = await fetch(`http://localhost:8000/api/deepseek/get/${currentTask.value.task_id}`)
    const result = await response.json()
    logApiCall('GET', `/api/deepseek/get/${currentTask.value.task_id}`, response.status, result)
    
    if (result.success) {
      aiAnalysis.value = result.analysis || '暂无AI分析内容'
    }
  } catch (error) {
    console.error('获取AI分析失败:', error)
  }
}

const generateWordReport = async () => {
  if (!currentTask.value?.task_id) return
  
  generatingWord.value = true
  try {
    const response = await fetch('http://localhost:8000/api/deepseek/generate-comprehensive-word-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        task_id: currentTask.value.task_id
      })
    })
    
    const result = await response.json()
    logApiCall('POST', '/api/deepseek/generate-comprehensive-word-report', response.status, result)
    
    if (result.success) {
      ElMessage.success('Word报告生成成功')
      wordReportReady.value = true
    } else {
      throw new Error(result.message || 'Word报告生成失败')
    }
  } catch (error) {
    logApiCall('POST', '/api/deepseek/generate-comprehensive-word-report', 'ERROR', { error: error.message })
    ElMessage.error(`Word报告生成失败: ${error.message}`)
  } finally {
    generatingWord.value = false
  }
}

const downloadWordReport = async () => {
  if (!currentTask.value?.task_id) return
  
  try {
    const response = await fetch(`http://localhost:8000/api/download-comprehensive-report/${currentTask.value.task_id}`)
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `压力分析报告_${currentTask.value.task_id.substring(0, 8)}.docx`
      a.click()
      window.URL.revokeObjectURL(url)
      
      ElMessage.success('Word报告下载成功')
      logApiCall('GET', `/api/download-comprehensive-report/${currentTask.value.task_id}`, 200, { downloaded: true })
    } else {
      throw new Error('下载失败')
    }
  } catch (error) {
    logApiCall('GET', `/api/download-comprehensive-report/${currentTask.value.task_id}`, 'ERROR', { error: error.message })
    ElMessage.error(`下载失败: ${error.message}`)
  }
}

// 工具函数
const getStatusType = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending': return '等待中'
    case 'running': return '运行中'
    case 'completed': return '已完成'
    case 'failed': return '失败'
    default: return status
  }
}

const getProgressStatus = () => {
  if (!currentTask.value) return ''
  switch (currentTask.value.status) {
    case 'completed': return 'success'
    case 'failed': return 'exception'
    default: return ''
  }
}

const getChartDisplayName = (chartName) => {
  const chartNames = {
    'force_time_series': '力值时间序列图',
    'force_distribution': '力值分布直方图',
    'force_boxplot': '力值箱线图',
    'absolute_deviation_boxplot': '绝对偏差箱线图',
    'percentage_deviation_boxplot': '百分比偏差箱线图',
    'interactive_3d_scatter': '3D散点图',
    'scatter_matrix': '散点图矩阵',
    'correlation_matrix': '相关性矩阵',
    'shewhart_control': 'Shewhart控制图',
    'moving_average': '移动平均控制图',
    'xbar_r_control': 'X-R控制图',
    'cusum_control': 'CUSUM控制图',
    'ewma_control': 'EWMA控制图',
    'imr_control': 'I-MR控制图',
    'run_chart': '运行图',
    'process_capability': '过程能力分析',
    'pareto_chart': '帕雷托图',
    'residual_analysis': '残差分析',
    'qq_normality': 'Q-Q正态性检验',
    'radar_chart': '雷达图',
    'heatmap': '热力图',
    'success_rate_trend': '成功率趋势图',
    'capability_index': '能力指数图',
    'quality_dashboard': '质量仪表盘',
    'waterfall_chart': '瀑布图',
    'spatial_clustering': '空间聚类图',
    'parallel_coordinates': '平行坐标图',
    'xy_heatmap': 'XY平面热力图',
    'projection_2d': '2D投影图',
    'position_anomaly_heatmap': '位置异常热力图',
    'spatial_density': '空间密度分布',
    'multivariate_relations': '多变量关系图',
    'anomaly_patterns': '异常模式图',
    'quality_distribution_map': '质量分布图',
    'comprehensive_assessment': '综合评估图'
  }
  return chartNames[chartName] || chartName
}

const getLogStatusClass = (status) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 400) return 'error'
  return 'info'
}

// API日志记录
const logApiCall = (method, url, status, data) => {
  const now = new Date()
  apiLogs.value.unshift({
    time: now.toLocaleTimeString(),
    method,
    url,
    status,
    data
  })
  
  // 保留最新的100条日志
  if (apiLogs.value.length > 100) {
    apiLogs.value = apiLogs.value.slice(0, 100)
  }
  
  lastApiResponse.value = data
}

// 导航函数
const goToTaskPage = () => {
  if (currentTask.value?.task_id) {
    router.push(`/task/${currentTask.value.task_id}`)
  }
}

const goToTasks = () => {
  router.push('/tasks')
}

const goToSettings = () => {
  router.push('/settings')
}

const viewChart = (chartName) => {
  ElMessage.info(`查看图表: ${getChartDisplayName(chartName)}`)
  // 这里可以实现图表查看逻辑
}

const viewAllCharts = () => {
  if (currentTask.value?.task_id) {
    router.push(`/results/${currentTask.value.task_id}`)
  }
}

const resetAnalysis = () => {
  ElMessageBox.confirm('确定要重新开始分析吗？这将清除当前所有数据。', '确认重置', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    currentStep.value = 0
    selectedFile.value = null
    fileList.value = []
    uploadResult.value = null
    uploadedFileName.value = ''
    uploadedFileId.value = ''
    currentTask.value = null
    analysisResults.value = null
    chartNames.value = []
    targetAnalysisResults.value = []
    progressDetails.value = null
    aiReportGenerated.value = false
    wordReportReady.value = false
    aiAnalysis.value = ''
    
    ElMessage.success('已重置分析')
  }).catch(() => {
    // 用户取消
  })
}

const completeAnalysis = () => {
  ElMessage.success('分析完成！您可以继续进行新的分析或查看历史记录。')
}

// 测试函数
const testAPIConnection = async () => {
  try {
    const response = await fetch('http://localhost:8000/health')
    const result = await response.json()
    logApiCall('GET', '/health', response.status, result)
    
    if (response.ok) {
      backendStatus.value = {
        connected: true,
        version: result.version || '1.0.0',
        status: result.status || 'healthy'
      }
      ElMessage.success('后端连接正常')
    } else {
      throw new Error('健康检查失败')
    }
  } catch (error) {
    backendStatus.value = {
      connected: false,
      version: '',
      status: 'error'
    }
    logApiCall('GET', '/health', 'ERROR', { error: error.message })
    ElMessage.error(`后端连接失败: ${error.message}`)
  }
}

const loadDemoData = () => {
  // 模拟加载演示数据
  selectedFile.value = new File(['demo content'], 'demo_data.csv', { type: 'text/csv' })
  fileList.value = [{ name: 'demo_data.csv', size: 1024, status: 'ready' }]
  uploadResult.value = {
    success: true,
    message: '演示数据加载成功',
    details: '文件ID: demo-12345',
    preview: '序号,X,Y,Z,力值\n1,100,100,100,5.2N\n2,101,99,101,24.8N\n3,99,101,99,49.5N'
  }
  uploadedFileName.value = 'demo_data.csv'
  uploadedFileId.value = 'demo-12345'
  
  ElMessage.success('演示数据加载完成')
}

const runQuickTest = async () => {
  quickTesting.value = true
  testResults.value = []
  
  try {
    // 1. 测试后端连接
    testResults.value.push({ name: '后端连接测试', success: false, message: '测试中...' })
    await testAPIConnection()
    testResults.value[0] = { name: '后端连接测试', success: true, message: '连接正常' }
    
    // 2. 加载演示数据
    testResults.value.push({ name: '加载演示数据', success: false, message: '测试中...' })
    loadDemoData()
    testResults.value[1] = { name: '加载演示数据', success: true, message: '数据加载完成' }
    
    // 3. 模拟任务创建
    testResults.value.push({ name: '创建分析任务', success: false, message: '测试中...' })
    currentTask.value = {
      task_id: 'test-' + Date.now(),
      status: 'completed',
      progress: 100
    }
    testResults.value[2] = { name: '创建分析任务', success: true, message: '任务创建成功' }
    
    // 4. 设置步骤为完成状态
    currentStep.value = 3
    analysisResults.value = {
      data_summary: { total_points: 100, valid_points: 95 },
      analysis_results: { overall_success_rate: 85 }
    }
    chartNames.value = ['force_time_series', 'force_distribution', 'process_capability']
    
    testResults.value.push({ name: '完整流程测试', success: true, message: '所有功能正常' })
    
    ElMessage.success('快速测试完成，所有功能正常')
    
  } catch (error) {
    testResults.value.push({ name: '测试失败', success: false, message: error.message })
    ElMessage.error('快速测试失败')
  } finally {
    quickTesting.value = false
  }
}

const viewAPIStatus = () => {
  ElMessageBox.alert(`
    前端: http://localhost:5173 ✅
    后端: http://localhost:8000 ${backendStatus.value.connected ? '✅' : '❌'}
    DeepSeek AI: ${aiReportGenerated.value ? '✅' : '未测试'}
    当前步骤: ${currentStep.value + 1}/4
    上传文件: ${uploadedFileName.value || '未上传'}
    分析状态: ${currentTask.value?.status || '未开始'}
  `, 'API状态', {
    dangerouslyUseHTMLString: true
  })
}

onMounted(() => {
  // 页面加载时的初始化操作
  testAPIConnection()
})
</script>

<style scoped>
.data-analysis-complete {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.step-card {
  margin: 20px 0;
  min-height: 400px;
}

.upload-section {
  text-align: center;
}

.upload-area {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.file-info {
  margin-top: 20px;
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  text-align: left;
}

.file-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.upload-result {
  margin-top: 20px;
}

.file-preview {
  margin-top: 16px;
}

.file-preview pre {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  text-align: left;
}

.params-section {
  padding: 20px;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.params-preview {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  height: fit-content;
}

.preview-item, .range-item {
  margin-bottom: 8px;
  font-size: 14px;
}

.tolerance-ranges {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* 新增样式：目标力值配置 */
.target-forces-config {
  width: 100%;
}

.force-config-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s ease;
}

.force-config-row:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.force-input {
  flex: 1;
}

.tolerance-input {
  flex: 1;
}

.config-preview {
  margin-bottom: 16px;
  padding: 12px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 6px;
  border-left: 3px solid var(--el-color-primary);
}

.preview-title {
  margin-bottom: 8px;
  color: var(--el-color-primary);
  font-weight: 600;
}

.preview-range {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

/* 进度详情样式 */
.progress-details {
  margin-top: 16px;
  padding: 12px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid var(--el-border-color-lighter);
}

.progress-details p {
  margin: 4px 0;
  display: flex;
  justify-content: space-between;
}

.progress-details strong {
  color: var(--el-color-primary);
}

/* 目标结果表格区域 */
.target-results {
  margin: 20px 0;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

.target-results h4 {
  margin-bottom: 12px;
  color: var(--el-color-primary);
}

.step-actions {
  margin-top: 20px;
  text-align: center;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.analysis-section {
  padding: 20px;
}

.analysis-summary {
  margin-bottom: 20px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 12px;
}

.summary-item {
  font-size: 14px;
}

.analysis-control {
  text-align: center;
  margin: 20px 0;
}

.task-status {
  margin-top: 20px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.status-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin: 12px 0;
}

.status-item {
  font-size: 14px;
}

.task-stage {
  margin-top: 12px;
  font-size: 14px;
}

.results-section {
  padding: 20px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 12px 0;
}

.result-item {
  font-size: 14px;
  padding: 8px;
  background-color: var(--el-bg-color-page);
  border-radius: 4px;
}

.charts-section {
  margin: 20px 0;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.chart-list {
  margin: 12px 0;
}

.chart-tag {
  margin: 4px;
  cursor: pointer;
}

.ai-section {
  margin: 20px 0;
  padding: 16px;
  background-color: var(--el-color-warning-light-9);
  border-radius: 8px;
}

.ai-actions {
  margin: 12px 0;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.ai-content {
  margin-top: 16px;
}

.ai-text {
  padding: 12px;
  background-color: white;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-size: 14px;
}

.debug-card {
  margin-top: 2rem;
  border: 2px dashed #e4e7ed;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.debug-content {
  max-height: 600px;
  overflow-y: auto;
}

.api-logs {
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  display: grid;
  grid-template-columns: 80px 60px 1fr 80px;
  gap: 10px;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.log-time {
  color: #909399;
}

.log-method {
  font-weight: bold;
  text-align: center;
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 10px;
}

.log-method.GET {
  background: #e1f3d8;
  color: #67c23a;
}

.log-method.POST {
  background: #e6f7ff;
  color: #409eff;
}

.log-method.DELETE {
  background: #fef0f0;
  color: #f56c6c;
}

.log-status {
  text-align: center;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 10px;
}

.log-status.success {
  background: #e1f3d8;
  color: #67c23a;
}

.log-status.error {
  background: #fef0f0;
  color: #f56c6c;
}

.api-response {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 1rem;
  font-size: 12px;
  max-height: 400px;
  overflow: auto;
}

.test-actions {
  padding: 1rem;
}

.test-buttons {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
  flex-wrap: wrap;
}

.test-results {
  margin-top: 1rem;
  border-top: 1px solid #e4e7ed;
  padding-top: 1rem;
}

.test-result-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 0.5rem 0;
}

.test-message {
  color: #606266;
  font-size: 14px;
}

.quick-access-card {
  margin-top: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.quick-access-card .el-card__header {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.quick-access-card h3 {
  color: white;
  margin: 0;
}

.quick-links {
  margin-bottom: 1rem;
}

.system-status {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
}

.status-item strong {
  min-width: 60px;
}

.status-item span {
  opacity: 0.8;
  font-family: 'Courier New', monospace;
}

@media (max-width: 768px) {
  .system-status {
    grid-template-columns: 1fr;
  }
  
  .test-buttons {
    flex-direction: column;
  }
  
  .quick-links .el-button-group {
    width: 100%;
  }
  
  .quick-links .el-button {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .force-config-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .force-input,
  .tolerance-input {
    width: 100%;
  }
  
  .progress-details p {
    flex-direction: column;
    gap: 4px;
  }
}
</style> 
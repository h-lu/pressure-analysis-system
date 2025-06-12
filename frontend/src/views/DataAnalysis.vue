<template>
  <div class="data-analysis-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">数据分析 / {{ currentStepTitle }}</h1>
    </div>

    <!-- 步骤1: 文件上传 -->
    <div v-if="currentStep === 1" class="step-container">
      <!-- 文件上传卡片 -->
      <div class="upload-card-container">
        <div class="function-card upload-card">
          <div class="card-header">
            <h3 class="card-title">📁 上传文件</h3>
          </div>
          <div class="card-content">
            <!-- 拖拽上传区域 -->
            <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
              <div class="upload-content">
                <div class="upload-text">拖拽文件到此处</div>
                <div class="upload-subtext">或点击选择文件</div>
                <div class="upload-tip">支持CSV格式，最大100MB</div>
              </div>
            </div>
            <input ref="fileInput" type="file" accept=".csv" @change="handleFileSelect" style="display: none;">
            <!-- 浏览按钮 -->
            <el-button type="primary" class="browse-btn" @click="triggerFileInput">浏览文件</el-button>
          </div>
        </div>
      </div>

      <!-- 文件预览区域 -->
      <div class="file-preview-card" v-if="fileUploaded">
        <div class="card-header">
          <h3 class="card-title">📋 文件预览</h3>
        </div>
        <div class="card-content">
          <!-- 文件信息 -->
          <div class="file-info-bar">
            <div class="file-info-item">
              <span class="info-label">文件名:</span>
              <span class="info-value">{{ fileInfo.name }}</span>
            </div>
            <div class="file-info-item">
              <span class="info-label">大小:</span>
              <span class="info-value">{{ fileInfo.size }}</span>
            </div>
            <div class="file-info-item">
              <span class="info-label">数据点:</span>
              <span class="info-value">{{ fileInfo.rows }}</span>
            </div>
            <div class="file-info-item">
              <span class="validation-status success">✓ 格式验证通过</span>
            </div>
          </div>

          <!-- 数据表格预览 -->
          <div class="data-preview">
            <div class="preview-title">数据预览 (前10行):</div>
            
            <!-- 表格 -->
            <div class="data-table">
              <!-- 表格头部 -->
              <div class="table-header">
                <div class="th">序号</div>
                <div class="th">X</div>
                <div class="th">Y</div>
                <div class="th">Z</div>
                <div class="th">力值</div>
              </div>
              
              <!-- 数据行 -->
              <div class="table-row" v-for="(row, index) in previewData" :key="index">
                <div class="td">{{ row.sequence }}</div>
                <div class="td">{{ row.x }}</div>
                <div class="td">{{ row.y }}</div>
                <div class="td">{{ row.z }}</div>
                <div class="td">{{ row.force }}</div>
              </div>
              
              <!-- 省略号 -->
              <div class="table-ellipsis">
                <div class="ellipsis-text">...</div>
                <div class="ellipsis-detail">显示前10行，完整数据包含{{ fileInfo.rows }}行</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 下一步按钮 -->
      <div class="step-actions" v-if="fileUploaded">
        <el-button type="primary" size="large" @click="nextStep">下一步：配置参数</el-button>
      </div>
    </div>

    <!-- 步骤2: 配置分析参数 -->
    <div v-if="currentStep === 2" class="step-container">
      <div class="params-config-card">
        <div class="card-header">
          <h3 class="card-title">⚙️ 配置分析参数</h3>
        </div>
        <div class="card-content">
          <!-- 参数配置表单 -->
          <div class="params-form">
            <div class="param-section">
              <div class="section-header">
                <h4 class="section-title">目标力值配置</h4>
                <el-button type="primary" size="small" @click="addForceConfig">
                  <el-icon><Plus /></el-icon>
                  添加目标力值
                </el-button>
              </div>
              <div class="force-configs">
                <div class="force-config" v-for="(force, index) in forceConfigs" :key="index">
                  <div class="force-header">
                    <span class="force-label">目标力值</span>
                    <el-button 
                      type="danger" 
                      size="small" 
                      circle 
                      @click="removeForceConfig(index)"
                      v-if="forceConfigs.length > 1"
                    >
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                  <div class="config-row">
                    <div class="config-item">
                      <label>目标力值 (N):</label>
                      <el-input-number 
                        v-model="force.target" 
                        :min="0" 
                        :step="1" 
                        :precision="1"
                      />
                    </div>
                    <div class="config-item">
                      <label>绝对容差:</label>
                      <el-input-number 
                        v-model="force.absoluteTolerance" 
                        :min="0" 
                        :step="0.1" 
                        :precision="2"
                      />
                    </div>
                    <div class="config-item">
                      <label>百分比容差:</label>
                      <el-input-number 
                        v-model="force.percentageTolerance" 
                        :min="0" 
                        :max="100" 
                        :step="1" 
                        :precision="1"
                      />
                    </div>
                  </div>
                  <div class="tolerance-range">
                    有效范围: {{ calculateRange(force.target, force.absoluteTolerance, force.percentageTolerance) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 参数预览 -->
            <div class="params-preview">
              <h4 class="section-title">参数预览</h4>
              <div class="preview-content">
                <div v-for="(force, index) in forceConfigs" :key="index" class="preview-item">
                  <strong>{{ force.target }}N:</strong> 
                  绝对容差 ±{{ force.absoluteTolerance }}, 
                  百分比容差 ±{{ force.percentageTolerance }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤导航 -->
      <div class="step-actions">
        <el-button @click="prevStep">上一步：文件上传</el-button>
        <el-button type="primary" size="large" @click="nextStep">下一步：开始分析</el-button>
      </div>
    </div>

    <!-- 步骤3: 执行分析 -->
    <div v-if="currentStep === 3" class="step-container">
      <div class="execute-analysis-card">
        <div class="card-header">
          <h3 class="card-title">🚀 执行数据分析</h3>
        </div>
        <div class="card-content">
          <!-- 分析配置摘要 -->
          <div class="analysis-summary">
            <h4 class="section-title">分析配置摘要</h4>
            <div class="summary-grid">
              <div class="summary-item">
                <span class="label">文件名:</span>
                <span class="value">{{ fileInfo.name }}</span>
              </div>
              <div class="summary-item">
                <span class="label">数据点数:</span>
                <span class="value">{{ fileInfo.rows }}</span>
              </div>
              <div class="summary-item">
                <span class="label">目标力值:</span>
                <span class="value">{{ forceConfigs.map(f => f.target + 'N').join(', ') }}</span>
              </div>
            </div>
          </div>

          <!-- 开始分析按钮 -->
          <div class="start-analysis">
            <el-button 
              type="success" 
              size="large" 
              class="analysis-btn"
              :loading="analysisRunning"
              @click="startAnalysis"
            >
              🚀 开始分析
            </el-button>
            <div class="analysis-info">
              <div>• 预计分析时间: 3-5分钟</div>
              <div>• 将生成35个专业图表和分析报告</div>
              <div>• 包含DeepSeek AI智能分析</div>
            </div>
          </div>

          <!-- 分析进度 -->
          <div v-if="analysisRunning" class="analysis-progress">
            <div class="progress-info">
              <span class="progress-label">分析进度</span>
              <span class="progress-percentage">{{ progressPercentage }}%</span>
            </div>
            <el-progress 
              :percentage="progressPercentage" 
              :status="progressStatus"
              :stroke-width="12"
            />
            <div class="progress-details">
              <div class="detail-item">
                <span class="label">当前阶段:</span>
                <span class="value">{{ currentStage }}</span>
              </div>
              <div class="detail-item">
                <span class="label">已生成文件:</span>
                <span class="value">{{ generatedFiles }} / 35</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤导航 -->
      <div class="step-actions" v-if="!analysisRunning">
        <el-button @click="prevStep">上一步：配置参数</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const fileInput = ref(null)

// 当前步骤
const currentStep = ref(1)
const currentStepTitle = computed(() => {
  const titles = {
    1: '步骤1: 文件上传',
    2: '步骤2: 配置参数',
    3: '步骤3: 开始分析'
  }
  return titles[currentStep.value]
})

// 文件上传状态
const fileUploaded = ref(false)
const fileInfo = ref({
  name: '',
  size: '',
  rows: ''
})
const currentFile = ref(null)

// 力值配置
const forceConfigs = ref([
  { target: 5, absoluteTolerance: 0.5, percentageTolerance: 5 },
  { target: 25, absoluteTolerance: 1.0, percentageTolerance: 4 },
  { target: 50, absoluteTolerance: 2.0, percentageTolerance: 3 }
])

// 分析状态
const analysisRunning = ref(false)
const progressPercentage = ref(0)
const progressStatus = ref('success')
const currentStage = ref('准备开始')
const generatedFiles = ref(0)

// 预览数据
const previewData = ref([])

// 方法
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    handleFile(file)
  }
}

const handleFileDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file) {
    handleFile(file)
  }
}

const handleFile = async (file) => {
  try {
    // 保存文件引用
    currentFile.value = file
    
    const text = await file.text()
    const lines = text.trim().split('\n')
    const rows = lines.length - 1 // 减去标题行
    
    // 解析CSV数据
    const data = []
    for (let i = 1; i < Math.min(11, lines.length); i++) { // 取前10行数据
      const cols = lines[i].split(',')
      if (cols.length >= 5) {
        data.push({
          sequence: cols[0],
          x: cols[1],
          y: cols[2], 
          z: cols[3],
          force: cols[4].replace('N', '') // 移除N单位
        })
      }
    }
    
    fileInfo.value = {
      name: file.name,
      size: formatFileSize(file.size),
      rows: `${rows}个`
    }
    previewData.value = data
    fileUploaded.value = true
    ElMessage.success('文件上传成功！')
  } catch (error) {
    ElMessage.error('文件解析失败，请检查文件格式')
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}

const calculateRange = (target, absTolerance, pctTolerance) => {
  const absMin = target - absTolerance
  const absMax = target + absTolerance
  const pctMin = target * (1 - pctTolerance / 100)
  const pctMax = target * (1 + pctTolerance / 100)
  
  const min = Math.max(absMin, pctMin)
  const max = Math.min(absMax, pctMax)
  
  return `${min.toFixed(2)}N - ${max.toFixed(2)}N`
}

// 添加目标力值配置
const addForceConfig = () => {
  forceConfigs.value.push({
    target: 10,
    absoluteTolerance: 0.5,
    percentageTolerance: 5
  })
}

// 删除目标力值配置
const removeForceConfig = (index) => {
  if (forceConfigs.value.length > 1) {
    forceConfigs.value.splice(index, 1)
  }
}

const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const startAnalysis = async () => {
  analysisRunning.value = true
  currentStage.value = '准备上传文件'
  
  try {
    // 1. 先上传文件
    const formData = new FormData()
    if (currentFile.value) {
      formData.append('file', currentFile.value)
    } else {
      throw new Error('未选择文件')
    }
    
    currentStage.value = '上传文件中...'
    progressPercentage.value = 10
    
    const uploadResponse = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData
    })
    
    if (!uploadResponse.ok) {
      throw new Error('文件上传失败')
    }
    
    const uploadResult = await uploadResponse.json()
    currentStage.value = '文件上传成功'
    progressPercentage.value = 20
    
    // 2. 启动分析任务
    currentStage.value = '启动分析任务'
    progressPercentage.value = 30
    
    const analysisParams = {
      file_id: uploadResult.file_id,
      target_forces: forceConfigs.value.map(f => f.target),
      tolerance_abs: forceConfigs.value.map(f => f.absoluteTolerance),
      tolerance_pct: forceConfigs.value.map(f => f.percentageTolerance)
    }
    
    const analysisResponse = await fetch('http://localhost:8000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(analysisParams)
    })
    
    if (!analysisResponse.ok) {
      const errorText = await analysisResponse.text()
      console.error('分析请求失败:', {
        status: analysisResponse.status,
        statusText: analysisResponse.statusText,
        body: errorText
      })
      throw new Error(`分析任务启动失败: ${analysisResponse.status} ${errorText}`)
    }
    
    const analysisResult = await analysisResponse.json()
    progressPercentage.value = 50
    
    ElMessage.success('分析任务已启动！')
    
    // 跳转到任务状态页面
    setTimeout(() => {
      router.push(`/task/${analysisResult.task_id}`)
    }, 1000)
    
  } catch (error) {
    console.error('分析启动失败:', error)
    ElMessage.error(error.message || '启动分析失败')
    analysisRunning.value = false
    progressPercentage.value = 0
  }
}
</script>

<style scoped>
.data-analysis-page {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 20px;
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

.step-container {
  width: 100%;
}

/* 步骤1: 上传卡片区域 */
.upload-card-container {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.function-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  flex: 1;
  height: 180px;
}

.function-card.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.card-header {
  padding: 15px 15px 0 15px;
}

.card-title {
  color: #303133;
  font-size: 16px;
  font-weight: bold;
  margin: 0;
}

.card-content {
  padding: 15px;
  height: calc(100% - 45px);
  display: flex;
  flex-direction: column;
}

/* 文件上传卡片 */
.upload-area {
  background-color: #fafbfc;
  border: 2px dashed #d3d4d6;
  border-radius: 4px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.upload-content {
  text-align: center;
}

.upload-text {
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}

.upload-subtext {
  color: #c0c4cc;
  font-size: 12px;
  margin-bottom: 10px;
}

.upload-tip {
  color: #c0c4cc;
  font-size: 10px;
}

.browse-btn {
  width: 80px;
  height: 30px;
  align-self: flex-start;
}

/* 禁用状态的卡片内容 */
.disabled-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: center;
}

.param-preview {
  color: #c0c4cc;
  font-size: 12px;
  margin-bottom: 8px;
}

.step-info {
  color: #909399;
  font-size: 11px;
  text-align: center;
  margin-top: 15px;
  font-style: italic;
}

.analysis-btn-preview {
  background-color: #f0f0f0;
  color: #c0c4cc;
  text-align: center;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-weight: bold;
}

/* 文件预览卡片 */
.file-preview-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 20px;
}

.file-info-bar {
  background-color: #f9f9f9;
  border: 1px solid #e4e7ed;
  padding: 15px;
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.file-info-item {
  display: flex;
  gap: 8px;
}

.info-label {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
}

.info-value {
  color: #606266;
  font-size: 12px;
}

.validation-status.success {
  color: #67C23A;
  font-size: 12px;
}

.data-preview {
  margin-bottom: 20px;
}

.preview-title {
  color: #303133;
  font-size: 14px;
  margin-bottom: 15px;
}

.data-table {
  border: 1px solid #e4e7ed;
}

.table-header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  padding: 0;
}

.th {
  flex: 1;
  padding: 12px;
  color: #303133;
  font-size: 12px;
  font-weight: bold;
  border-right: 1px solid #e4e7ed;
}

.th:last-child {
  border-right: none;
}

.table-row {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
}

.table-row:nth-child(even) {
  background-color: #fafbfc;
}

.td {
  flex: 1;
  padding: 10px 12px;
  color: #606266;
  font-size: 11px;
  border-right: 1px solid #e4e7ed;
}

.td:last-child {
  border-right: none;
}

.status-normal {
  color: #67C23A;
}

.table-ellipsis {
  text-align: center;
  padding: 20px;
  color: #c0c4cc;
}

.ellipsis-text {
  font-size: 12px;
  margin-bottom: 5px;
}

.ellipsis-detail {
  font-size: 11px;
  color: #909399;
}

.data-statistics {
  background-color: #f9f9f9;
  border: 1px solid #e4e7ed;
  padding: 15px;
}

.stats-title {
  color: #303133;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.stats-item {
  color: #606266;
  font-size: 11px;
}

.quality-excellent {
  color: #67C23A;
}

/* 步骤2: 参数配置 */
.params-config-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 30px;
}

.params-form {
  padding: 20px;
}

.section-title {
  color: #303133;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
}

.force-configs {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.force-config {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
  background-color: #fafbfc;
}

.force-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.force-label {
  color: #409EFF;
  font-weight: bold;
  font-size: 14px;
}

.config-row {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.config-item {
  flex: 1;
}

.config-item label {
  display: block;
  color: #606266;
  font-size: 12px;
  margin-bottom: 5px;
}

.tolerance-range {
  color: #67C23A;
  font-size: 11px;
  font-weight: bold;
  text-align: center;
  padding: 5px;
  background-color: #f0f9ff;
  border-radius: 3px;
}

.params-preview {
  background-color: #f9f9f9;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  color: #606266;
  font-size: 12px;
}

/* 步骤3: 执行分析 */
.execute-analysis-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 30px;
}

.analysis-summary {
  margin-bottom: 30px;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 15px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.summary-item .label {
  color: #909399;
  font-size: 12px;
}

.summary-item .value {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
}

.start-analysis {
  text-align: center;
  margin-bottom: 30px;
}

.analysis-btn {
  width: 200px;
  height: 50px;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
}

.analysis-info {
  color: #606266;
  font-size: 12px;
}

.analysis-info div {
  margin-bottom: 5px;
}

.analysis-progress {
  margin-top: 30px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.progress-label {
  color: #303133;
  font-weight: bold;
}

.progress-percentage {
  color: #409EFF;
  font-weight: bold;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
}

.detail-item {
  display: flex;
  gap: 10px;
}

.detail-item .label {
  color: #909399;
  font-size: 12px;
}

.detail-item .value {
  color: #303133;
  font-size: 12px;
  font-weight: bold;
}

/* 步骤操作按钮 */
.step-actions {
  text-align: center;
  padding: 20px 0;
}

.step-actions .el-button {
  margin: 0 10px;
}
</style> 
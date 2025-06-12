<template>
  <div class="ai-settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon><Cpu /></el-icon>
          <span>DeepSeek AI 设置</span>
        </div>
      </template>

      <!-- 连接状态 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Connection /></el-icon>
          <span>连接状态</span>
        </div>
        
        <div class="connection-status">
          <div class="status-indicator" :class="connectionStatus.type">
            <el-icon>
              <component :is="connectionStatus.icon" />
            </el-icon>
            <span class="status-text">{{ connectionStatus.text }}</span>
          </div>
          
          <div class="status-details">
            <div class="detail-item">
              <span class="detail-label">API端点:</span>
              <span class="detail-value">{{ apiConfig.endpoint }}</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">最后测试:</span>
              <span class="detail-value">{{ lastTestTime || '未测试' }}</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">响应时间:</span>
              <span class="detail-value">{{ responseTime ? `${responseTime}ms` : '--' }}</span>
            </div>
          </div>
          
          <div class="connection-actions">
            <el-button 
              :loading="isTestingConnection"
              @click="testConnection"
              :type="connectionStatus.type === 'success' ? 'success' : 'primary'"
            >
              <el-icon><Refresh /></el-icon>
              测试连接
            </el-button>
          </div>
        </div>
      </div>

      <!-- API配置 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Setting /></el-icon>
          <span>API配置</span>
        </div>
        
        <el-form :model="apiConfig" label-width="120px">
          <el-form-item label="API端点">
            <el-input
              v-model="apiConfig.endpoint"
              placeholder="https://api.deepseek.com"
              :disabled="!editMode"
            />
          </el-form-item>
          
          <el-form-item label="API密钥">
            <el-input
              v-model="apiConfig.apiKey"
              type="password"
              placeholder="输入API密钥"
              :disabled="!editMode"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="超时时间">
            <el-input-number
              v-model="apiConfig.timeout"
              :min="5000"
              :max="60000"
              :step="1000"
              :disabled="!editMode"
            />
            <span class="unit-text">毫秒</span>
          </el-form-item>
          
          <el-form-item label="重试次数">
            <el-input-number
              v-model="apiConfig.retryCount"
              :min="0"
              :max="5"
              :disabled="!editMode"
            />
          </el-form-item>
        </el-form>
        
        <div class="config-actions">
          <el-button 
            v-if="!editMode"
            @click="enableEditMode"
            type="primary"
          >
            <el-icon><Edit /></el-icon>
            编辑配置
          </el-button>
          
          <template v-else>
            <el-button @click="cancelEdit">取消</el-button>
            <el-button 
              @click="saveConfig"
              type="primary"
              :loading="isSavingConfig"
            >
              保存配置
            </el-button>
          </template>
        </div>
      </div>

      <!-- 使用统计 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><DataAnalysis /></el-icon>
          <span>使用统计</span>
        </div>
        
        <div class="usage-stats">
          <div class="stat-grid">
            <div class="stat-item">
              <div class="stat-value">{{ usageStats.totalRequests }}</div>
              <div class="stat-label">总请求数</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ usageStats.successfulRequests }}</div>
              <div class="stat-label">成功请求</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ usageStats.failedRequests }}</div>
              <div class="stat-label">失败请求</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ usageStats.successRate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
          
          <div class="usage-chart">
            <el-progress
              :percentage="usageStats.successRate"
              :status="usageStats.successRate > 90 ? 'success' : 
                      usageStats.successRate > 70 ? '' : 'exception'"
              :stroke-width="20"
            />
            <div class="chart-label">API调用成功率</div>
          </div>
        </div>
      </div>

      <!-- 分析配置 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Document /></el-icon>
          <span>分析配置</span>
        </div>
        
        <el-form :model="analysisConfig" label-width="120px">
          <el-form-item label="分析深度">
            <el-radio-group v-model="analysisConfig.depth">
              <el-radio value="basic">基础分析</el-radio>
              <el-radio value="detailed">详细分析</el-radio>
              <el-radio value="comprehensive">综合分析</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="包含内容">
            <el-checkbox-group v-model="analysisConfig.includes">
              <el-checkbox value="data_summary">数据摘要</el-checkbox>
              <el-checkbox value="statistical_analysis">统计分析</el-checkbox>
              <el-checkbox value="quality_assessment">质量评估</el-checkbox>
              <el-checkbox value="recommendations">改进建议</el-checkbox>
              <el-checkbox value="charts_interpretation">图表解读</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <el-form-item label="语言风格">
            <el-select v-model="analysisConfig.language">
              <el-option label="专业技术" value="technical" />
              <el-option label="通俗易懂" value="popular" />
              <el-option label="简洁明了" value="concise" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="报告长度">
            <el-slider
              v-model="analysisConfig.reportLength"
              :min="500"
              :max="5000"
              :step="100"
              show-input
              input-size="small"
            />
            <span class="unit-text">字符</span>
          </el-form-item>
        </el-form>
        
        <div class="analysis-actions">
          <el-button @click="resetAnalysisConfig">重置配置</el-button>
          <el-button 
            @click="saveAnalysisConfig"
            type="primary"
            :loading="isSavingAnalysis"
          >
            保存配置
          </el-button>
        </div>
      </div>

      <!-- 模型信息 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Monitor /></el-icon>
          <span>模型信息</span>
        </div>
        
        <div class="model-info">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">当前模型:</span>
              <span class="info-value">{{ modelInfo.name }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">模型版本:</span>
              <span class="info-value">{{ modelInfo.version }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">上下文长度:</span>
              <span class="info-value">{{ modelInfo.contextLength }} tokens</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">支持语言:</span>
              <span class="info-value">{{ modelInfo.languages.join(', ') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 高级设置 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Tools /></el-icon>
          <span>高级设置</span>
        </div>
        
        <div class="advanced-settings">
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-name">启用缓存</span>
              <span class="setting-desc">缓存分析结果以提高响应速度</span>
            </div>
            <el-switch v-model="advancedSettings.enableCache" />
          </div>
          
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-name">自动重试</span>
              <span class="setting-desc">请求失败时自动重试</span>
            </div>
            <el-switch v-model="advancedSettings.autoRetry" />
          </div>
          
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-name">详细日志</span>
              <span class="setting-desc">记录详细的API调用日志</span>
            </div>
            <el-switch v-model="advancedSettings.verboseLogging" />
          </div>
          
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-name">实验性功能</span>
              <span class="setting-desc">启用实验性的AI分析功能</span>
            </div>
            <el-switch v-model="advancedSettings.experimentalFeatures" />
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式状态
const isTestingConnection = ref(false)
const editMode = ref(false)
const isSavingConfig = ref(false)
const isSavingAnalysis = ref(false)
const lastTestTime = ref('')
const responseTime = ref(0)

// API配置
const apiConfig = reactive({
  endpoint: 'https://api.deepseek.com',
  apiKey: '',
  timeout: 30000,
  retryCount: 3
})

// 原始配置备份
const originalApiConfig = reactive({})

// 分析配置
const analysisConfig = reactive({
  depth: 'detailed',
  includes: ['data_summary', 'statistical_analysis', 'quality_assessment', 'recommendations'],
  language: 'technical',
  reportLength: 2000
})

// 使用统计
const usageStats = reactive({
  totalRequests: 156,
  successfulRequests: 148,
  failedRequests: 8,
  successRate: 94.9
})

// 模型信息
const modelInfo = reactive({
  name: 'DeepSeek-Coder',
  version: 'v2.5',
  contextLength: 32768,
  languages: ['中文', '英文', 'Python', 'R', 'SQL']
})

// 高级设置
const advancedSettings = reactive({
  enableCache: true,
  autoRetry: true,
  verboseLogging: false,
  experimentalFeatures: false
})

// 连接状态
const connectionStatus = computed(() => {
  if (isTestingConnection.value) {
    return {
      type: 'warning',
      icon: 'Loading',
      text: '正在测试连接...'
    }
  }
  
  if (responseTime.value > 0) {
    return {
      type: 'success',
      icon: 'CircleCheck',
      text: '连接正常'
    }
  }
  
  return {
    type: 'info',
    icon: 'Warning',
    text: '未测试连接'
  }
})

// 测试连接
const testConnection = async () => {
  isTestingConnection.value = true
  
  try {
    const startTime = Date.now()
    
    // 这里应该调用实际的API测试接口
    // const response = await deepseekAPI.testConnection()
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    
    const endTime = Date.now()
    responseTime.value = endTime - startTime
    lastTestTime.value = new Date().toLocaleString()
    
    ElMessage.success(`连接测试成功，响应时间: ${responseTime.value}ms`)
    
  } catch (error) {
    responseTime.value = 0
    ElMessage.error('连接测试失败: ' + error.message)
  } finally {
    isTestingConnection.value = false
  }
}

// 启用编辑模式
const enableEditMode = () => {
  editMode.value = true
  Object.assign(originalApiConfig, { ...apiConfig })
}

// 取消编辑
const cancelEdit = () => {
  editMode.value = false
  Object.assign(apiConfig, originalApiConfig)
}

// 保存API配置
const saveConfig = async () => {
  if (!apiConfig.apiKey.trim()) {
    ElMessage.warning('请输入API密钥')
    return
  }
  
  isSavingConfig.value = true
  
  try {
    // 这里应该保存到后端或本地存储
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    editMode.value = false
    ElMessage.success('API配置已保存')
    
    // 自动测试连接
    testConnection()
    
  } catch (error) {
    ElMessage.error('保存配置失败: ' + error.message)
  } finally {
    isSavingConfig.value = false
  }
}

// 保存分析配置
const saveAnalysisConfig = async () => {
  isSavingAnalysis.value = true
  
  try {
    // 这里应该保存到后端或本地存储
    await new Promise(resolve => setTimeout(resolve, 500))
    
    ElMessage.success('分析配置已保存')
    
  } catch (error) {
    ElMessage.error('保存分析配置失败: ' + error.message)
  } finally {
    isSavingAnalysis.value = false
  }
}

// 重置分析配置
const resetAnalysisConfig = () => {
  ElMessageBox.confirm(
    '确定要重置分析配置吗？这将恢复到默认设置。',
    '重置确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    analysisConfig.depth = 'detailed'
    analysisConfig.includes = ['data_summary', 'statistical_analysis', 'quality_assessment', 'recommendations']
    analysisConfig.language = 'technical'
    analysisConfig.reportLength = 2000
    
    ElMessage.success('分析配置已重置')
  })
}

// 组件挂载时加载配置
onMounted(() => {
  // 这里应该从后端或本地存储加载配置
  // loadApiConfig()
  // loadAnalysisConfig()
})
</script>

<style scoped>
.ai-settings {
  max-width: 800px;
  margin: 0 auto;
}

.settings-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.setting-section {
  margin-bottom: 32px;
}

.setting-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
}

/* 连接状态 */
.connection-status {
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

.status-indicator.success {
  color: var(--el-color-success);
}

.status-indicator.warning {
  color: var(--el-color-warning);
}

.status-indicator.info {
  color: var(--el-color-info);
}

.status-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-label {
  color: var(--el-text-color-secondary);
}

.detail-value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.connection-actions {
  text-align: right;
}

/* 配置表单 */
.unit-text {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.config-actions,
.analysis-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 使用统计 */
.usage-stats {
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.usage-chart {
  margin-top: 16px;
}

.chart-label {
  text-align: center;
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

/* 模型信息 */
.model-info {
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.info-label {
  color: var(--el-text-color-secondary);
}

.info-value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

/* 高级设置 */
.advanced-settings {
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-info {
  flex: 1;
}

.setting-name {
  display: block;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .config-actions,
  .analysis-actions {
    flex-direction: column;
  }
  
  .config-actions .el-button,
  .analysis-actions .el-button {
    width: 100%;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-item {
    flex-direction: column;
    gap: 4px;
  }
}
</style> 
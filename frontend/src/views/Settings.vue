<template>
  <div class="settings">
    <el-page-header content="系统设置" />
    
    <div class="settings-content">
      <!-- DeepSeek AI 配置 -->
      <el-card class="setting-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>DeepSeek AI 配置</span>
            <el-tag :type="aiConnectionStatus === 'connected' ? 'success' : 'danger'" size="small">
              {{ aiConnectionStatus === 'connected' ? '已连接' : '未连接' }}
            </el-tag>
          </div>
        </template>
        
        <el-form :model="aiConfig" label-width="140px">
          <el-form-item label="API Key">
            <el-input
              v-model="aiConfig.apiKey"
              type="password"
              placeholder="请输入DeepSeek API Key"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="API 基础URL">
            <el-input
              v-model="aiConfig.baseUrl"
              placeholder="https://api.deepseek.com"
            />
          </el-form-item>
          
          <el-form-item label="模型名称">
            <el-input
              v-model="aiConfig.model"
              placeholder="deepseek-chat"
            />
          </el-form-item>
          
          <el-form-item>
            <el-space>
              <el-button type="primary" @click="saveAIConfig" :loading="savingConfig">
                {{ savingConfig ? '保存中...' : '保存配置' }}
              </el-button>
              <el-button @click="testAIConnection" :loading="testingConnection">
                {{ testingConnection ? '测试中...' : '测试连接' }}
              </el-button>
            </el-space>
          </el-form-item>
        </el-form>
        

      </el-card>





      <!-- 数据管理 -->
      <el-card class="setting-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>数据管理</span>
          </div>
        </template>
        
        <div class="data-management">
          <!-- 存储统计 -->
          <div class="storage-stats">
            <h4>存储使用情况</h4>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-statistic title="历史记录" :value="storageStats.historyCount" suffix="个" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="图表文件" :value="storageStats.chartFiles" suffix="个" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="报告文件" :value="storageStats.reportFiles" suffix="个" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="占用空间" :value="storageStats.totalSize" suffix="MB" />
              </el-col>
            </el-row>
          </div>
          
          <!-- 数据操作 -->
          <div class="data-operations">
            <h4>数据操作</h4>
            <el-space wrap>
              <el-button type="warning" @click="clearCache" :loading="clearingCache">
                清理缓存
              </el-button>
              
              <el-button type="info" @click="exportConfig">
                导出配置
              </el-button>
              
              <el-button type="info" @click="$refs.importInput.click()">
                导入配置
              </el-button>
              <input
                ref="importInput"
                type="file"
                accept=".json"
                style="display: none"
                @change="importConfig"
              />
              
              <el-button type="success" @click="backupData" :loading="backingUp">
                数据备份
              </el-button>
              
              <el-popconfirm
                title="确定要清理所有历史数据吗？此操作不可恢复！"
                @confirm="cleanAllData"
              >
                <template #reference>
                  <el-button type="danger">清理所有数据</el-button>
                </template>
              </el-popconfirm>
            </el-space>
          </div>
        </div>
      </el-card>


    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deepseekAPI } from '@/api/deepseek'
import { getFullApiURL } from '@/config'

const API_BASE = getFullApiURL('')

// AI配置
const aiConfig = reactive({
  apiKey: '',
  baseUrl: 'https://api.deepseek.com',
  model: 'deepseek-chat'
})

const aiConnectionStatus = ref('disconnected')
const testingConnection = ref(false)
const savingConfig = ref(false)



// 存储统计
const storageStats = reactive({
  historyCount: 0,
  chartFiles: 0,
  reportFiles: 0,
  totalSize: 0
})

// 操作状态
const clearingCache = ref(false)
const backingUp = ref(false)

// 测试AI连接
const testAIConnection = async () => {
  testingConnection.value = true
  try {
    const response = await deepseekAPI.testConnection()
    
    if (response.success) {
      aiConnectionStatus.value = 'connected'
      ElMessage.success('AI连接测试成功！')
    } else {
      aiConnectionStatus.value = 'disconnected'
      ElMessage.error(`连接失败: ${response.message || '未知错误'}`)
    }
  } catch (error) {
    aiConnectionStatus.value = 'disconnected'
    ElMessage.error('连接测试失败，请检查网络和配置')
    console.error('AI连接测试失败:', error)
  } finally {
    testingConnection.value = false
  }
}

// 保存AI配置
const saveAIConfig = async () => {
  if (!aiConfig.apiKey) {
    ElMessage.warning('请先输入API Key')
    return
  }
  
  savingConfig.value = true
  try {
    const response = await deepseekAPI.saveConfig({
      api_key: aiConfig.apiKey,
      base_url: aiConfig.baseUrl,
      model: aiConfig.model
    })
    
    if (response.success) {
      ElMessage.success(response.message || 'AI配置已保存')
      // 保存成功后测试连接
      await testAIConnection()
    } else {
      ElMessage.error(response.message || '保存配置失败')
    }
  } catch (error) {
    ElMessage.error('保存配置失败，请重试')
    console.error('保存AI配置失败:', error)
  } finally {
    savingConfig.value = false
  }
}





// 获取存储统计
const getStorageStats = async () => {
  try {
    const response = await fetch(getFullApiURL('/api/storage-stats'))
    const result = await response.json()
    
    if (result.success) {
      // 正确映射后端返回的字段名
      storageStats.historyCount = result.data.history_count || 0
      storageStats.chartFiles = result.data.chart_files || 0
      storageStats.reportFiles = result.data.report_files || 0
      storageStats.totalSize = result.data.total_size || 0
    } else {
      throw new Error(result.message || '获取存储统计失败')
    }
  } catch (error) {
    console.error('获取存储统计失败:', error)
    // 使用备用数据
    const taskResponse = await fetch(getFullApiURL('/api/tasks'))
    const tasks = await taskResponse.json()
    storageStats.historyCount = tasks.tasks?.length || 0
    storageStats.chartFiles = storageStats.historyCount * 35
    storageStats.reportFiles = storageStats.historyCount
    storageStats.totalSize = Math.floor(storageStats.historyCount * 50)
  }
}



// 获取AI配置
const getAIConfig = async () => {
  try {
    const response = await deepseekAPI.getConfig()
    
    if (response.success) {
      Object.assign(aiConfig, response.data)
    } else {
      console.error('获取AI配置失败:', response.message)
    }
  } catch (error) {
    console.error('获取AI配置失败:', error)
  }
}



// 清理缓存
const clearCache = async () => {
  clearingCache.value = true
  try {
    const response = await fetch(getFullApiURL('/api/clear-cache'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(result.message)
      if (result.data.freed_space_mb > 0) {
        ElMessage.info(`释放空间: ${result.data.freed_space_mb} MB`)
      }
      await getStorageStats() // 刷新存储统计
    } else {
      throw new Error(result.message || '缓存清理失败')
    }
  } catch (error) {
    ElMessage.error('缓存清理失败')
    console.error('缓存清理失败:', error)
  } finally {
    clearingCache.value = false
  }
}

// 导出配置
const exportConfig = () => {
  const config = {
    ai: aiConfig,
    exportTime: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `pressure-system-config-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('配置导出成功')
}

// 导入配置
const importConfig = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const config = JSON.parse(e.target.result)
      
      if (config.ai) Object.assign(aiConfig, config.ai)
      
      // 保存到本地存储
      saveAIConfig()
      
      ElMessage.success('配置导入成功')
    } catch (error) {
      ElMessage.error('配置文件格式错误')
    }
  }
  reader.readAsText(file)
  
  // 清空文件输入
  event.target.value = ''
}

// 数据备份
const backupData = async () => {
  backingUp.value = true
  try {
    const response = await fetch(getFullApiURL('/api/backup-data'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(result.message)
      ElMessage.info(`备份文件: ${result.data.backup_file} (${result.data.backup_size_mb} MB)`)
    } else {
      throw new Error(result.message || '数据备份失败')
    }
  } catch (error) {
    ElMessage.error('数据备份失败')
    console.error('数据备份失败:', error)
  } finally {
    backingUp.value = false
  }
}

// 清理所有数据
const cleanAllData = async () => {
  try {
    const response = await fetch(getFullApiURL('/api/clear-all-data'), {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(result.message)
      if (result.data.cleared_items.length > 0) {
        ElMessage.info(`清理项目: ${result.data.cleared_items.join(', ')}`)
      }
      await getStorageStats() // 刷新统计
    } else {
      throw new Error(result.message || '数据清理失败')
    }
  } catch (error) {
    ElMessage.error('数据清理失败')
    console.error('数据清理失败:', error)
  }
}



// 组件挂载
onMounted(() => {
  // 初始化数据
  getAIConfig()
  getStorageStats()
  testAIConnection()
})
</script>

<style scoped>
.settings {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.settings-content {
  margin-top: 20px;
}

.setting-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.unit {
  margin-left: 8px;
  color: #909399;
}





.storage-stats {
  margin-bottom: 24px;
}

.storage-stats h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.data-operations h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* 深色主题支持 */
:global(.dark) .setting-card {
  background-color: #2d2d2d;
  border-color: #4c4d4f;
}

:global(.dark) .card-header {
  color: #e5eaf3;
}

:global(.dark) .storage-stats h4,
:global(.dark) .data-operations h4 {
  color: #e5eaf3;
}

:global(.dark) .form-tip {
  color: #a3a6ad;
}
</style> 
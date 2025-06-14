<template>
  <div class="data-analysis-test">
    <h1>数据分析页面</h1>
    <p>这是数据分析功能的测试版本</p>
    
    <!-- 文件上传区域 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <h3>文件上传</h3>
          </template>
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            accept=".csv"
            :limit="1"
            @change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽CSV文件到此处<em>或点击选择文件</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                仅支持CSV格式，最大100MB
              </div>
            </template>
          </el-upload>
          <div v-if="selectedFile" style="margin-top: 16px;">
            <p><strong>已选择文件:</strong> {{ selectedFile.name }}</p>
            <p><strong>文件大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
            <el-button type="primary" @click="uploadFile" :loading="uploading">
              {{ uploading ? '上传中...' : '上传文件' }}
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <h3>分析参数</h3>
          </template>
          <el-form label-width="100px">
            <el-form-item label="目标力值">
              <el-input v-model="analysisParams.targetForces" placeholder="例如: 5, 25, 50" />
            </el-form-item>
            <el-form-item label="绝对容差">
              <el-input-number v-model="analysisParams.absoluteTolerance" :min="0" :step="0.1" />
            </el-form-item>
            <el-form-item label="百分比容差">
              <el-input-number v-model="analysisParams.percentageTolerance" :min="0" :max="100" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <h3>开始分析</h3>
          </template>
          <div style="text-align: center; padding: 20px;">
            <el-button 
              type="primary" 
              size="large" 
              @click="startAnalysis" 
              :disabled="!canStartAnalysis"
              :loading="analyzing"
            >
              {{ analyzing ? '分析中...' : '开始分析' }}
            </el-button>
          </div>
          <div v-if="currentTask" style="margin-top: 16px;">
            <el-divider>当前任务</el-divider>
            <p><strong>任务ID:</strong> {{ currentTask.task_id }}</p>
            <p><strong>状态:</strong> {{ currentTask.status }}</p>
            <p><strong>进度:</strong> {{ currentTask.progress || 0 }}%</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- API测试区域 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <h3>API连接测试</h3>
      </template>
      <el-button @click="testAPI" type="primary">测试后端连接</el-button>
      <el-button @click="testAI" type="warning" style="margin-left: 10px;">测试AI连接</el-button>
      <el-button @click="getTaskList" style="margin-left: 10px;">获取任务列表</el-button>
      
      <div v-if="apiResult" style="margin-top: 16px;">
        <h4>API响应:</h4>
        <pre>{{ apiResult }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getFullApiURL } from '@/config'

const router = useRouter()

// 状态管理
const selectedFile = ref(null)
const uploading = ref(false)
const analyzing = ref(false)
const apiResult = ref('')
const currentTask = ref(null)

// 分析参数
const analysisParams = ref({
  targetForces: '5, 25, 50',
  absoluteTolerance: 0.5,
  percentageTolerance: 5
})

// 计算属性
const canStartAnalysis = computed(() => {
  return selectedFile.value && !analyzing.value
})

// 文件处理
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  ElMessage.success(`已选择文件: ${file.name}`)
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
  uploadProgress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch(getFullApiURL('/api/upload'), {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`上传失败: ${response.status}`)
    }

    const data = await response.json()
    console.log('上传响应:', data)

    if (data.success) {
      uploadedFileName.value = data.filename
      ElMessage.success('文件上传成功')
    } else {
      throw new Error(data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.message || '上传失败')
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

const startAnalysis = async () => {
  if (!uploadedFileName.value) {
    ElMessage.error('请先上传文件')
    return
  }

  analyzing.value = true
  analysisProgress.value = 0

  try {
    const response = await fetch(getFullApiURL('/api/analyze'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filename: uploadedFileName.value
      })
    })

    if (!response.ok) {
      throw new Error(`分析失败: ${response.status}`)
    }

    const data = await response.json()
    console.log('分析响应:', data)

    if (data.success) {
      currentTaskId.value = data.task_id
      ElMessage.success('分析任务已启动')
      
      // 开始轮询任务状态
      pollTaskStatus()
    } else {
      throw new Error(data.message || '分析启动失败')
    }
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error(error.message || '分析失败')
    analyzing.value = false
  }
}

const checkHealth = async () => {
  try {
    const response = await fetch(getFullApiURL('/health'))
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success(`后端服务正常: ${data.message}`)
    } else {
      ElMessage.error('后端服务异常')
    }
  } catch (error) {
    ElMessage.error('无法连接到后端服务')
  }
}

const testDeepSeek = async () => {
  try {
    const response = await fetch(getFullApiURL('/api/deepseek/test-connection'))
    const data = await response.json()
    
    if (response.ok && data.success) {
      ElMessage.success('DeepSeek API 连接正常')
    } else {
      ElMessage.error(data.message || 'DeepSeek API 连接失败')
    }
  } catch (error) {
    ElMessage.error('DeepSeek API 测试失败')
  }
}

const getTasks = async () => {
  try {
    const response = await fetch(getFullApiURL('/api/tasks'))
    const data = await response.json()
    
    console.log('任务列表:', data)
    ElMessage.success('任务列表获取成功，请查看控制台')
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  }
}

// API测试函数（这些函数与上面的函数重复，已经修复过了）
</script>

<style scoped>
.data-analysis-test {
  padding: 20px;
}

.upload-demo {
  width: 100%;
}

pre {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

.el-form-item {
  margin-bottom: 16px;
}
</style> 
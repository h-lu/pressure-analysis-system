<template>
  <el-card shadow="hover" class="file-upload-card">
    <template #header>
      <div class="card-header">
        <el-icon><Upload /></el-icon>
        <span>文件上传</span>
      </div>
    </template>

    <el-upload
      class="upload-area"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :before-upload="beforeUpload"
      accept=".csv"
      :limit="1"
      :file-list="fileList"
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

    <!-- 上传进度条 -->
    <div v-if="uploading" class="upload-progress">
      <el-progress 
        :percentage="uploadProgress" 
        :status="uploadStatus"
        :stroke-width="6"
      />
      <div class="progress-text">{{ progressText }}</div>
    </div>

    <!-- 文件验证结果 -->
    <div v-if="validationResult" class="validation-result" :class="validationResult.valid ? 'valid' : 'invalid'">
      <div class="validation-header">
        <el-icon :class="validationResult.valid ? 'success' : 'error'">
          <component :is="validationResult.valid ? 'CircleCheck' : 'CircleClose'" />
        </el-icon>
        <span>{{ validationResult.valid ? '文件验证通过' : '文件验证失败' }}</span>
      </div>
      <div v-if="!validationResult.valid && validationResult.errors?.length" class="validation-errors">
        <ul>
          <li v-for="error in validationResult.errors" :key="error">{{ error }}</li>
        </ul>
      </div>
    </div>

    <div v-if="uploadedFile" class="file-info">
      <el-descriptions title="文件信息" :column="1" size="small">
        <el-descriptions-item label="文件名">
          {{ uploadedFile.name }}
        </el-descriptions-item>
        <el-descriptions-item label="文件大小">
          {{ formatFileSize(uploadedFile.size) }}
        </el-descriptions-item>
        <el-descriptions-item label="上传时间">
          {{ uploadedFile.upload_time ? formatDateTime(uploadedFile.upload_time) : '--' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态" v-if="uploadedFile.status">
          <el-tag :type="getStatusType(uploadedFile.status)">
            {{ uploadedFile.status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <template #footer v-if="selectedFile || uploadedFile">
      <div class="card-footer">
        <el-button @click="clearFile" size="small" :disabled="uploading">
          清空
        </el-button>
        <el-button 
          v-if="selectedFile && !uploadedFile" 
          type="primary" 
          @click="uploadFile" 
          :loading="uploading"
          :disabled="!canUpload"
          size="small"
        >
          {{ uploading ? '上传中...' : '上传文件' }}
        </el-button>
        <el-button 
          v-if="uploadedFile && validationResult?.valid" 
          type="success" 
          @click="previewFile" 
          :loading="previewing"
          size="small"
        >
          预览数据
        </el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { useAnalysisStore } from '@/stores/analysis'
import { analysisAPI } from '@/api'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['file-uploaded', 'file-previewed'])

const analysisStore = useAnalysisStore()
const selectedFile = ref(null)
const uploadedFile = ref(null)
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('')
const validationResult = ref(null)
const previewing = ref(false)

// 计算属性
const canUpload = computed(() => {
  return selectedFile.value && !uploading.value
})

const handleFileChange = (file) => {
  if (!beforeUpload(file.raw)) {
    return false
  }

  selectedFile.value = file.raw
  fileList.value = [file]
  uploadedFile.value = null
  validationResult.value = null
  
  // 重置进度
  uploadProgress.value = 0
  progressText.value = ''
}

const beforeUpload = (file) => {
  // 文件大小检查
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过100MB')
    return false
  }

  // 文件类型检查
  const allowedTypes = ['text/csv', 'application/vnd.ms-excel']
  const fileName = file.name.toLowerCase()
  if (!fileName.endsWith('.csv') && !allowedTypes.includes(file.type)) {
    ElMessage.error('只支持CSV格式文件')
    return false
  }

  return true
}

const handleFileRemove = () => {
  selectedFile.value = null
  uploadedFile.value = null
  fileList.value = []
  validationResult.value = null
  uploadProgress.value = 0
  progressText.value = ''
}

const clearFile = () => {
  selectedFile.value = null
  uploadedFile.value = null
  fileList.value = []
  validationResult.value = null
  uploadProgress.value = 0
  progressText.value = ''
  analysisStore.resetUploadedFile()
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  try {
    uploading.value = true
    uploadStatus.value = ''
    uploadProgress.value = 0
    progressText.value = '准备上传...'

    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 10
        progressText.value = `上传中... ${Math.round(uploadProgress.value)}%`
      }
    }, 200)

    const result = await analysisStore.uploadFile(selectedFile.value)
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    progressText.value = '上传完成！'

    uploadedFile.value = {
      name: result.filename || selectedFile.value.name,
      size: selectedFile.value.size,
      upload_time: new Date().toISOString(),
      status: '已上传'
    }

    ElMessage.success('文件上传成功')
    emit('file-uploaded', result)

    // 自动验证文件
    await validateFile(result.filename)

  } catch (error) {
    uploadStatus.value = 'exception'
    progressText.value = '上传失败'
    ElMessage.error(`文件上传失败: ${error.message || '未知错误'}`)
  } finally {
    uploading.value = false
    setTimeout(() => {
      if (uploadStatus.value === 'success') {
        uploadProgress.value = 0
        progressText.value = ''
      }
    }, 2000)
  }
}

const validateFile = async (filename) => {
  try {
    const result = await analysisAPI.validateFile(filename)
    validationResult.value = result
    
    if (result.valid) {
      ElMessage.success('文件验证通过')
    } else {
      ElMessage.warning('文件存在问题，请检查数据格式')
    }
  } catch (error) {
    console.error('文件验证失败:', error)
    validationResult.value = {
      valid: false,
      errors: ['文件验证服务暂时不可用']
    }
  }
}

const previewFile = async () => {
  if (!uploadedFile.value?.name) {
    ElMessage.warning('没有可预览的文件')
    return
  }

  try {
    previewing.value = true
    const result = await analysisAPI.previewFile(uploadedFile.value.name)
    emit('file-previewed', result)
    ElMessage.success('数据预览加载成功')
  } catch (error) {
    ElMessage.error(`数据预览失败: ${error.message || '未知错误'}`)
  } finally {
    previewing.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const typeMap = {
    '已上传': 'success',
    '上传中': 'warning',
    '失败': 'danger'
  }
  return typeMap[status] || 'info'
}
</script>

<style scoped>
.file-upload-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.upload-area {
  width: 100%;
}

.upload-area .el-upload {
  width: 100%;
}

.upload-area .el-upload-dragger {
  width: 100%;
  height: 180px;
}

.upload-progress {
  margin-top: 16px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
}

.progress-text {
  margin-top: 8px;
  text-align: center;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.validation-result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid;
}

.validation-result.valid {
  background-color: var(--el-color-success-light-9);
  border-color: var(--el-color-success-light-5);
  color: var(--el-color-success);
}

.validation-result.invalid {
  background-color: var(--el-color-error-light-9);
  border-color: var(--el-color-error-light-5);
  color: var(--el-color-error);
}

.validation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.validation-errors {
  margin-top: 8px;
}

.validation-errors ul {
  margin: 0;
  padding-left: 20px;
}

.validation-errors li {
  margin: 4px 0;
  font-size: 14px;
}

.file-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-light);
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.el-icon.success {
  color: var(--el-color-success);
}

.el-icon.error {
  color: var(--el-color-error);
}
</style> 
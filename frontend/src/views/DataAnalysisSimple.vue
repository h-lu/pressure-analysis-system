<template>
  <div class="data-analysis-simple">
    <h1>数据分析页面</h1>
    <p>这是简化版的数据分析页面</p>
    
    <el-card>
      <template #header>
        <h3>文件上传</h3>
      </template>
      <div>
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          accept=".csv"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处<em>或点击选择文件</em>
          </div>
        </el-upload>
      </div>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <h3>系统状态</h3>
      </template>
      <div>
        <el-button @click="testAPI" type="primary">测试API连接</el-button>
        <div v-if="apiResult" style="margin-top: 10px;">
          <pre>{{ apiResult }}</pre>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const apiResult = ref('')

const testAPI = async () => {
  try {
    const response = await fetch('http://localhost:8000/health')
    const data = await response.json()
    apiResult.value = JSON.stringify(data, null, 2)
    ElMessage.success('API连接成功')
  } catch (error) {
    apiResult.value = `错误: ${error.message}`
    ElMessage.error('API连接失败')
  }
}
</script>

<style scoped>
.data-analysis-simple {
  padding: 20px;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
}
</style> 
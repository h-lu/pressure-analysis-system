<template>
  <div class="test-page">
    <h1>测试页面</h1>
    <p>如果您能看到这个页面，说明Vue应用基本运行正常。</p>
    
    <el-button type="primary" @click="testBackend">测试后端连接</el-button>
    
    <div v-if="backendStatus" class="status">
      <h3>后端状态:</h3>
      <pre>{{ backendStatus }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getFullApiURL } from '@/config'

const backendStatus = ref(null)

const testBackend = async () => {
  try {
    const response = await fetch(getFullApiURL('/health'))
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success(`后端连接成功: ${data.message}`)
    } else {
      ElMessage.error('后端连接失败')
    }
  } catch (error) {
    ElMessage.error('无法连接到后端服务')
  }
}
</script>

<style scoped>
.test-page {
  padding: 20px;
}

.status {
  margin-top: 20px;
  padding: 15px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
}

pre {
  white-space: pre-wrap;
  font-family: monospace;
}
</style> 
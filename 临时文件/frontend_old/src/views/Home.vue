<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <h2>欢迎使用压力采集数据分析系统</h2>
          <p>这是一个基于Vue.js + FastAPI + R的全栈数据分析平台</p>
          <el-space>
            <el-button type="primary" @click="checkAPI">测试API连接</el-button>
            <el-button type="success" @click="$router.push('/upload')">开始上传数据</el-button>
          </el-space>
          <div v-if="apiStatus" class="api-status" :class="apiStatusClass">
            <p>{{ apiStatus }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据上传</span>
            </div>
          </template>
          <p>支持Excel、CSV等格式的压力数据上传</p>
          <el-button type="primary" @click="$router.push('/upload')">上传数据</el-button>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据分析</span>
            </div>
          </template>
          <p>使用R语言进行高级统计分析和可视化</p>
          <el-button type="success" @click="$router.push('/analysis')">开始分析</el-button>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>分析报告</span>
            </div>
          </template>
          <p>生成专业的数据分析报告和可视化图表</p>
          <el-button type="warning" @click="$router.push('/reports')">查看报告</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
  data() {
    return {
      apiStatus: '',
      apiStatusClass: ''
    }
  },
  methods: {
    async checkAPI() {
      try {
        const response = await axios.get('http://localhost:8001/health')
        this.apiStatus = `API连接成功 ✅ - ${response.data.service}`
        this.apiStatusClass = 'success'
      } catch (error) {
        this.apiStatus = 'API连接失败 ❌ - 请检查后端服务'
        this.apiStatusClass = 'error'
        console.error('API连接错误:', error)
      }
    }
  },
  mounted() {
    this.checkAPI()
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.api-status {
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
}

.api-status.success {
  background-color: #f0f9ff;
  border: 1px solid #67c23a;
  color: #67c23a;
}

.api-status.error {
  background-color: #fef0f0;
  border: 1px solid #f56c6c;
  color: #f56c6c;
}
</style> 
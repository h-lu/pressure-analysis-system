<template>
  <div class="home">
    <el-card>
      <h2>欢迎使用压力采集数据分析系统</h2>
      <p>这是一个基于Vue.js + FastAPI + R的全栈数据分析平台</p>
      <el-button type="primary" @click="checkAPI">测试API连接</el-button>
      <div v-if="apiStatus" class="api-status">
        <p>API状态: {{ apiStatus }}</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
  data() {
    return {
      apiStatus: ''
    }
  },
  methods: {
    async checkAPI() {
      try {
        const response = await axios.get('/api/health')
        this.apiStatus = '连接成功 ✅'
      } catch (error) {
        this.apiStatus = '连接失败 ❌'
      }
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
}

.api-status {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}
</style>
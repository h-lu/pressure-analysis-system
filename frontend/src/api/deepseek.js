import { apiClient } from '@/utils/http'

export const deepseekAPI = {
  // 生成AI分析报告
  generateReport(taskId) {
    return apiClient.post('/api/deepseek/generate-report', { task_id: taskId })
  },

  // 生成综合Word报告
  generateWordReport(taskId) {
    return apiClient.post('/api/deepseek/generate-comprehensive-word-report', { 
      task_id: taskId 
    })
  },

  // 获取AI分析结果
  getAnalysis(taskId) {
    return apiClient.get(`/api/deepseek/get/${taskId}`)
  },

  // 检查AI分析状态
  checkAnalysis(taskId) {
    return apiClient.get(`/api/deepseek/check/${taskId}`)
  },

  // 测试DeepSeek连接
  testConnection() {
    return apiClient.get('/api/deepseek/test-connection')
  },

  // 下载Word报告
  downloadReport(taskId) {
    return apiClient.get(`/api/download-comprehensive-report/${taskId}`, {
      responseType: 'blob'
    })
  },

  // 获取DeepSeek配置
  getConfig() {
    return apiClient.get('/api/deepseek/get-config')
  },

  // 保存DeepSeek配置
  saveConfig(config) {
    return apiClient.post('/api/deepseek/save-config', config)
  },


} 
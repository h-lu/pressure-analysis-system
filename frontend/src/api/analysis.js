import { apiClient } from '@/utils/http'

export const analysisAPI = {
  // 文件上传
  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 文件预览
  previewFile(filename) {
    return apiClient.get(`/api/preview/${filename}`)
  },

  // 数据验证
  validateFile(filename) {
    return apiClient.get(`/api/validate/${filename}`)
  },

  // 文件列表
  getFileList() {
    return apiClient.get('/api/list')
  },

  // 启动分析
  startAnalysis(params) {
    return apiClient.post('/api/analyze', params)
  },

  // 任务状态查询
  getTaskStatus(taskId) {
    return apiClient.get(`/api/task/${taskId}`)
  },

  // 获取分析结果
  getResults(taskId) {
    return apiClient.get(`/api/results/${taskId}`)
  },

  // 任务列表
  getTasks() {
    return apiClient.get('/api/tasks')
  },

  // 删除任务
  deleteTask(taskId) {
    return apiClient.delete(`/api/task/${taskId}`)
  },

  // 获取图表
  getChart(taskId, chartName) {
    return apiClient.get(`/api/chart/${taskId}/${chartName}`, {
      responseType: 'blob'
    })
  },

  // ==================== 历史记录相关 API ====================
  
  // 获取历史记录
  getHistory() {
    return apiClient.get('/api/history')
  },

  // 获取历史记录统计信息
  getHistoryStats() {
    return apiClient.get('/api/history/stats')
  },

  // 删除单个分析记录
  deleteAnalysisRecord(taskId) {
    return apiClient.delete(`/api/history/${taskId}`)
  },

  // 批量删除分析记录
  batchDeleteAnalysisRecords(taskIds) {
    return apiClient.delete('/api/history/batch', {
      data: { task_ids: taskIds }
    })
  },

  // 更新分析记录名称
  updateAnalysisRecordName(taskId, newName) {
    return apiClient.put(`/api/history/${taskId}/name`, {
      name: newName
    })
  }
} 
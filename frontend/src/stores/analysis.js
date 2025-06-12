import { defineStore } from 'pinia'
import { analysisAPI, deepseekAPI } from '@/api'

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    // 当前任务
    currentTask: null,
    
    // 任务列表
    tasks: [],
    
    // 分析结果缓存
    results: {},
    
    // 图表数据缓存
    charts: {},
    
    // DeepSeek AI分析结果缓存
    deepseekAnalysis: {},
    
    // 上传的文件信息
    uploadedFile: null,
    
    // 加载状态
    loading: {
      upload: false,
      analysis: false,
      ai: false,
      tasks: false,
      results: false
    }
  }),

  getters: {
    // 获取当前任务状态
    currentTaskStatus: (state) => {
      return state.currentTask?.status || 'idle'
    },
    
    // 获取当前任务进度
    currentTaskProgress: (state) => {
      return state.currentTask?.progress || 0
    },
    
    // 获取指定任务的图表
    getTaskCharts: (state) => (taskId) => {
      return state.charts[taskId] || {}
    },
    
    // 获取指定任务的AI分析
    getTaskAIAnalysis: (state) => (taskId) => {
      return state.deepseekAnalysis[taskId] || null
    }
  },

  actions: {
    // 文件上传
    async uploadFile(file) {
      this.loading.upload = true
      try {
        const response = await analysisAPI.uploadFile(file)
        this.uploadedFile = {
          filename: response.filename,
          original_name: file.name,
          size: file.size,
          upload_time: new Date().toISOString()
        }
        return response
      } finally {
        this.loading.upload = false
      }
    },

    // 启动分析
    async startAnalysis(params) {
      this.loading.analysis = true
      try {
        const response = await analysisAPI.startAnalysis(params)
        this.currentTask = response
        return response
      } finally {
        this.loading.analysis = false
      }
    },

    // 轮询任务状态
    async pollTaskStatus(taskId) {
      try {
        const response = await analysisAPI.getTaskStatus(taskId)
        this.currentTask = response
        
        // 更新任务列表中的对应任务
        const taskIndex = this.tasks.findIndex(task => task.task_id === taskId)
        if (taskIndex !== -1) {
          this.tasks[taskIndex] = response
        }
        
        // 如果任务完成，获取结果
        if (response.status === 'completed') {
          await this.getResults(taskId)
        }
        
        return response
      } catch (error) {
        console.error('轮询任务状态失败:', error)
        throw error
      }
    },

    // 获取分析结果
    async getResults(taskId) {
      this.loading.results = true
      try {
        const results = await analysisAPI.getResults(taskId)
        this.results[taskId] = results
        return results
      } catch (error) {
        console.error('获取分析结果失败:', error)
        throw error
      } finally {
        this.loading.results = false
      }
    },

    // 获取任务列表
    async getTasks() {
      this.loading.tasks = true
      try {
        const response = await analysisAPI.getTasks()
        this.tasks = response.tasks || []
        return response
      } catch (error) {
        console.error('获取任务列表失败:', error)
        throw error
      } finally {
        this.loading.tasks = false
      }
    },

    // 生成AI分析
    async generateAIAnalysis(taskId) {
      this.loading.ai = true
      try {
        const response = await deepseekAPI.generateWordReport(taskId)
        return response
      } finally {
        this.loading.ai = false
      }
    },

    // 获取AI分析结果
    async getAIAnalysis(taskId) {
      try {
        const analysis = await deepseekAPI.getAnalysis(taskId)
        this.deepseekAnalysis[taskId] = analysis
        return analysis
      } catch (error) {
        console.error('获取AI分析失败:', error)
        throw error
      }
    },

    // 加载图表
    async loadChart(taskId, chartName) {
      try {
        const chartBlob = await analysisAPI.getChart(taskId, chartName)
        const chartUrl = URL.createObjectURL(chartBlob)
        
        if (!this.charts[taskId]) {
          this.charts[taskId] = {}
        }
        this.charts[taskId][chartName] = chartUrl
        
        return chartUrl
      } catch (error) {
        console.error(`加载图表失败: ${chartName}`, error)
        throw error
      }
    },

    // 删除任务
    async deleteTask(taskId) {
      try {
        await analysisAPI.deleteTask(taskId)
        
        // 从任务列表中移除
        this.tasks = this.tasks.filter(task => task.task_id !== taskId)
        
        // 清理相关缓存
        delete this.results[taskId]
        delete this.charts[taskId] 
        delete this.deepseekAnalysis[taskId]
        
        // 如果删除的是当前任务，清空当前任务
        if (this.currentTask?.task_id === taskId) {
          this.currentTask = null
        }
        
        return true
      } catch (error) {
        console.error('删除任务失败:', error)
        throw error
      }
    },

    // ==================== 历史记录管理 ====================
    
    // 获取历史记录
    async getHistory() {
      try {
        const response = await analysisAPI.getHistory()
        return response.history || []
      } catch (error) {
        console.error('获取历史记录失败:', error)
        throw error
      }
    },

    // 获取历史记录统计
    async getHistoryStats() {
      try {
        const response = await analysisAPI.getHistoryStats()
        return response.stats || {}
      } catch (error) {
        console.error('获取历史记录统计失败:', error)
        throw error
      }
    },

    // 删除单个分析记录
    async deleteAnalysisRecord(taskId) {
      try {
        await analysisAPI.deleteAnalysisRecord(taskId)
        
        // 从任务列表中移除
        this.tasks = this.tasks.filter(task => task.task_id !== taskId)
        
        // 清理相关缓存
        delete this.results[taskId]
        delete this.charts[taskId] 
        delete this.deepseekAnalysis[taskId]
        
        return true
      } catch (error) {
        console.error('删除分析记录失败:', error)
        throw error
      }
    },

    // 批量删除分析记录
    async batchDeleteAnalysisRecords(taskIds) {
      try {
        const response = await analysisAPI.batchDeleteAnalysisRecords(taskIds)
        
        // 从任务列表中移除
        this.tasks = this.tasks.filter(task => !taskIds.includes(task.task_id))
        
        // 清理相关缓存
        taskIds.forEach(taskId => {
          delete this.results[taskId]
          delete this.charts[taskId] 
          delete this.deepseekAnalysis[taskId]
        })
        
        return response
      } catch (error) {
        console.error('批量删除分析记录失败:', error)
        throw error
      }
    },

    // 更新分析记录名称
    async updateAnalysisRecordName(taskId, newName) {
      try {
        const response = await analysisAPI.updateAnalysisRecordName(taskId, newName)
        
        // 更新任务列表中对应任务的名称
        const task = this.tasks.find(task => task.task_id === taskId)
        if (task && response.updated_record) {
          task.name = response.updated_record.name
        }
        
        return response
      } catch (error) {
        console.error('更新分析记录名称失败:', error)
        throw error
      }
    },

    // 清空当前任务
    clearCurrentTask() {
      this.currentTask = null
    },

    // 重置上传文件
    resetUploadedFile() {
      this.uploadedFile = null
    }
  }
}) 
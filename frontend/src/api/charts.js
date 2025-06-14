import { apiClient } from '@/utils/http'
import { getFullApiURL } from '@/config'

export const chartsAPI = {
  // 获取图表
  getChart(taskId, chartName) {
    return apiClient.get(`/api/chart/${taskId}/${chartName}`, {
      responseType: 'blob'
    })
  },

  // 检查图表是否存在
  async checkChart(taskId, chartName) {
    try {
      const url = getFullApiURL(`/api/chart/${taskId}/${chartName}`)
      const response = await fetch(url, {
        method: 'HEAD'
      })
      return response.ok
    } catch (error) {
      return false
    }
  },

  // 获取所有图表列表
  getChartsList(taskId) {
    // 35个图表的名称列表
    return [
      // 基础分析图表 (8个)
      'force_time_series', 'force_distribution', 'force_boxplot',
      'absolute_deviation_boxplot', 'percentage_deviation_boxplot',
      'interactive_3d_scatter', 'scatter_matrix', 'correlation_matrix',
      
      // 控制图 (7个)
      'shewhart_control', 'moving_average', 'xbar_r_control',
      'cusum_control', 'ewma_control', 'imr_control', 'run_chart',
      
      // 专业质量分析 (12个)
      'process_capability', 'pareto_chart', 'residual_analysis',
      'qq_normality', 'radar_chart', 'heatmap',
      'success_rate_trend', 'capability_index', 'quality_dashboard',
      'waterfall_chart', 'spatial_clustering', 'parallel_coordinates',
      
      // 多维分析 (8个)
      'xy_heatmap', 'projection_2d', 'position_anomaly_heatmap',
      'spatial_density', 'multivariate_relations', 'anomaly_patterns',
      'quality_distribution_map', 'comprehensive_assessment'
    ]
  },

  // 批量检查图表状态
  async batchCheckCharts(taskId, chartNames) {
    const promises = chartNames.map(async (chartName) => {
      const exists = await this.checkChart(taskId, chartName)
      return {
        name: chartName,
        exists,
        url: exists ? getFullApiURL(`/api/chart/${taskId}/${chartName}`) : null
      }
    })
    
    return Promise.all(promises)
  },

  // 下载图表
  async downloadChart(taskId, chartName, filename) {
    try {
      const blob = await this.getChart(taskId, chartName)
      const url = URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = filename || `${chartName}_${taskId}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)
      return true
    } catch (error) {
      console.error('下载图表失败:', error)
      throw error
    }
  },

  // 批量下载图表
  async batchDownloadCharts(taskId, chartNames, options = {}) {
    const { delay = 100, onProgress } = options
    const results = []
    
    for (let i = 0; i < chartNames.length; i++) {
      const chartName = chartNames[i]
      
      try {
        await this.downloadChart(taskId, chartName)
        results.push({ chartName, success: true })
        
        if (onProgress) {
          onProgress(i + 1, chartNames.length, chartName)
        }
        
        // 添加延迟避免过快下载
        if (delay > 0 && i < chartNames.length - 1) {
          await new Promise(resolve => setTimeout(resolve, delay))
        }
        
      } catch (error) {
        results.push({ chartName, success: false, error: error.message })
      }
    }
    
    return results
  },

  // 获取图表元数据
  async getChartMetadata(taskId, chartName) {
    try {
      const url = getFullApiURL(`/api/chart/${taskId}/${chartName}`)
      const response = await fetch(url, {
        method: 'HEAD'
      })
      
      if (!response.ok) {
        throw new Error('图表不存在')
      }
      
      return {
        name: chartName,
        size: response.headers.get('content-length'),
        type: response.headers.get('content-type'),
        lastModified: response.headers.get('last-modified'),
        url: url
      }
    } catch (error) {
      throw new Error(`获取图表元数据失败: ${error.message}`)
    }
  },

  // 验证图表URL
  async validateChartUrl(url) {
    try {
      const response = await fetch(url, { method: 'HEAD' })
      return response.ok
    } catch (error) {
      return false
    }
  },

  // 预加载图表
  async preloadChart(taskId, chartName) {
    try {
      const blob = await this.getChart(taskId, chartName)
      const url = URL.createObjectURL(blob)
      
      // 创建图片对象进行预加载
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          resolve({
            chartName,
            url,
            blob,
            width: img.naturalWidth,
            height: img.naturalHeight
          })
        }
        img.onerror = () => {
          URL.revokeObjectURL(url)
          reject(new Error('图片加载失败'))
        }
        img.src = url
      })
    } catch (error) {
      throw new Error(`预加载图表失败: ${error.message}`)
    }
  }
} 
<template>
  <div class="analysis-results-page">
    <!-- 页面标题和操作区 -->
    <div class="page-header">
      <h1 class="page-title">分析结果 / {{ fileName }}</h1>
      <div class="page-actions">
        <div class="status-indicator">
          <span class="status-dot completed"></span>
          <span class="status-text">分析完成</span>
        </div>
        <el-button type="primary" class="download-btn" @click="downloadWordReport" :loading="wordReportLoading">
          {{ wordReportLoading ? '生成中...' : 'Word报告' }}
        </el-button>
        <el-button type="success" class="download-btn" @click="exportData" :loading="exportLoading">
          {{ exportLoading ? '导出中...' : '导出数据' }}
        </el-button>
      </div>
    </div>

    <!-- 结果摘要卡片 -->
    <div class="results-summary-card">
      <div class="card-header">
        <h3 class="card-title">📊 分析摘要</h3>
      </div>
      <div class="card-content">
        <div class="summary-grid">
          <div class="summary-item success-rate">
            <div class="summary-value">{{ summaryData.successRate }}%</div>
            <div class="summary-label">成功率</div>
          </div>
          <div class="summary-item data-points">
            <div class="summary-value">{{ summaryData.dataPoints }}</div>
            <div class="summary-label">数据点数</div>
          </div>
          <div class="summary-item cp-value">
            <div class="summary-value">{{ summaryData.cpValue }}</div>
            <div class="summary-label">平均Cp值</div>
          </div>
          <div class="summary-item quality-grade">
            <div class="summary-value quality">{{ summaryData.qualityGrade }}</div>
            <div class="summary-label">质量等级</div>
          </div>
        </div>
      </div>
    </div>

    <!-- DeepSeek AI分析区域 -->
    <div class="ai-analysis-card">
      <div class="card-header">
        <h3 class="card-title">🤖 DeepSeek AI智能分析</h3>
        <el-button 
          type="primary" 
          class="ai-generate-btn" 
          @click="generateAIAnalysis"
          :loading="aiAnalysisLoading"
          :disabled="aiAnalysisLoading"
        >
          {{ aiAnalysisLoading ? '生成中...' : aiAnalysisGenerated ? '重新生成' : '生成AI分析' }}
        </el-button>
      </div>
      <div class="card-content">
        <div class="ai-analysis-content">
          <div v-if="!aiAnalysisGenerated && !aiAnalysisLoading" class="analysis-placeholder">
            <div class="placeholder-text">
              <p>🤖 点击"生成AI分析"按钮，获取DeepSeek AI对您数据的专业分析报告</p>
              <p>包含：质量评估、异常分析、改进建议等</p>
            </div>
          </div>
          <div v-else-if="aiAnalysisLoading" class="analysis-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <p>AI正在分析您的数据，请稍等...</p>
          </div>
          <div v-else class="analysis-text markdown-content" v-html="markdownToHtml(aiAnalysisContent)">
          </div>
        </div>
      </div>
    </div>

    <!-- 图表展示区域 -->
    <div class="charts-display-card">
      <div class="card-header">
        <h3 class="card-title">📈 专业图表展示 (35张)</h3>
        <!-- 不再需要切换按钮，所有图表都会显示 -->
      </div>
      <div class="card-content">
        <!-- 图表分类标签 -->
        <div class="chart-tabs">
          <div 
            v-for="category in chartCategories" 
            :key="category.key"
            class="tab-item" 
            :class="{ active: activeCategory === category.key }"
            @click="activeCategory = category.key"
          >
            {{ category.label }}
          </div>
        </div>

        <!-- 图表网格 - 直接显示图表 -->
        <div class="charts-grid-container">
          <div v-for="chart in currentCategoryCharts" :key="chart.name" class="chart-card">
            <div class="chart-header">
              <h4 class="chart-title">{{ chart.title }}</h4>
              <el-button 
                type="primary" 
                size="small" 
                @click="openChartModal(chart)"
                class="fullscreen-btn"
              >
                🔍 放大查看
              </el-button>
            </div>
            <div class="chart-image-container">
              <el-image
                :src="chart.imageUrl"
                :alt="chart.title"
                fit="contain"
                class="chart-image"
                :loading="'lazy'"
                @click="openChartModal(chart)"
              >
                <template #placeholder>
                  <div class="image-slot">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <div>加载中...</div>
                  </div>
                </template>
                <template #error>
                  <div class="image-slot">
                    <el-icon><Picture /></el-icon>
                    <div>图表生成中</div>
                  </div>
                </template>
              </el-image>
            </div>
          </div>
        </div>

        <!-- 不再需要显示更多按钮，因为所有图表都会显示 -->
      </div>
    </div>

    <!-- 图表放大模态窗口 -->
    <el-dialog
      v-model="chartModalVisible"
      :title="selectedChart?.title"
      width="95%"
      top="2vh"
      class="chart-modal"
      destroy-on-close
      lock-scroll
    >
      <div class="modal-chart-container">
        <el-image
          :src="selectedChart?.imageUrl"
          :alt="selectedChart?.title"
          fit="contain"
          class="modal-chart-image"
          style="width: 100%; height: 100%;"
          loading="lazy"
        >
          <template #placeholder>
            <div class="modal-image-slot">
              <el-icon class="is-loading"><Loading /></el-icon>
              <div>加载高清图表中...</div>
            </div>
          </template>
          <template #error>
            <div class="modal-image-slot">
              <el-icon><Picture /></el-icon>
              <div>图表暂时无法显示</div>
            </div>
          </template>
        </el-image>
      </div>
      <template #footer>
        <div class="modal-footer">
          <el-button @click="downloadChart(selectedChart)">
            <el-icon><Download /></el-icon>
            下载图表
          </el-button>
          <el-button type="primary" @click="chartModalVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading, Picture, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const fileName = ref('demo_data.csv')
const taskId = computed(() => route.params.taskId || 'demo-task-id')

// API基础地址
const API_BASE = 'http://localhost:8000'

// 改进的markdown渲染函数
const markdownToHtml = (markdown) => {
  if (!markdown) return ''
  
  let html = markdown
    // 标题
    .replace(/^# (.*$)/gim, '<h1 class="md-h1">$1</h1>')
    .replace(/^## (.*$)/gim, '<h2 class="md-h2">$1</h2>')
    .replace(/^### (.*$)/gim, '<h3 class="md-h3">$1</h3>')
    .replace(/^#### (.*$)/gim, '<h4 class="md-h4">$1</h4>')
    
    // 表格（简单处理）
    .replace(/\|(.+)\|/g, (match, content) => {
      const cells = content.split('|').map(cell => cell.trim())
      const cellTags = cells.map(cell => `<td>${cell}</td>`).join('')
      return `<tr>${cellTags}</tr>`
    })
    
    // 加粗和斜体
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    
    // 列表项
    .replace(/^[\-\*\+] (.*$)/gim, '<li>$1</li>')
    .replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>')
    
    // 代码块（内联）
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    
    // 换行
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
  
  // 包装列表
  html = html.replace(/(<li>.*?<\/li>)/gs, '<ul class="md-list">$1</ul>')
  
  // 包装表格
  html = html.replace(/(<tr>.*?<\/tr>)/gs, '<table class="md-table"><tbody>$1</tbody></table>')
  
  // 包装段落
  if (html && !html.startsWith('<h') && !html.startsWith('<ul') && !html.startsWith('<table')) {
    html = '<p>' + html + '</p>'
  }
  
  return html
}

// 摘要数据
const summaryData = ref({
  successRate: '90.0',
  dataPoints: '20',
  cpValue: '2.892',
  qualityGrade: '优秀',
  analysisTime: '2分27秒'
})

// 获取分析结果数据
const fetchAnalysisResults = async () => {
  try {
    console.log('获取分析结果...')
    const response = await fetch(`http://localhost:8000/api/results/${taskId.value}`)
    
    if (!response.ok) {
      throw new Error(`API返回错误: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('分析结果API返回:', data)
    
    // 解析真实的分析结果数据 - 基于实际返回的数据结构
    if (data.result) {
      const result = data.result
      console.log('完整的分析结果数据:', result)
      
      // 从analysis_results中获取数据，这是真正的分析结果数据结构
      const analysisResults = result.analysis_results || {}
      const summary = analysisResults.summary || {}
      const targetAnalysis = analysisResults.target_analysis || []
      const processCapability = analysisResults.process_capability || []
      const overallStats = analysisResults.overall_stats && analysisResults.overall_stats[0] || {}
      
      // 从summary获取总体成功率
      let totalSuccessRate = summary.success_rate || 0
      console.log('从summary获取的成功率:', totalSuccessRate)
      
      // 如果summary中没有，从target_analysis计算
      if (totalSuccessRate === 0 && targetAnalysis.length > 0) {
        console.log('目标分析数据:', targetAnalysis)
        const successRates = targetAnalysis.map(stat => stat['成功率_综合'] || 0)
        console.log('成功率数组:', successRates)
        totalSuccessRate = successRates.reduce((sum, rate) => sum + rate, 0) / successRates.length
      }
      
      // 计算平均Cp值
      let averageCp = 0
      if (processCapability.length > 0) {
        const cpValues = processCapability.map(cap => cap.Cp || 0)
        averageCp = cpValues.reduce((sum, cp) => sum + cp, 0) / cpValues.length
      }
      
      // 确定质量等级
      let qualityGrade = '不合格'
      if (averageCp >= 2.0) {
        qualityGrade = '优秀'
      } else if (averageCp >= 1.33) {
        qualityGrade = '良好'
      } else if (averageCp >= 1.0) {
        qualityGrade = '合格'
      }
      
      // 更新分析摘要数据
      summaryData.value = {
        successRate: Math.round(totalSuccessRate * 10) / 10, // 保留1位小数
        dataPoints: summary.total_records || overallStats['样本数'] || 0,
        cpValue: Math.round(averageCp * 1000) / 1000, // 保留3位小数
        qualityGrade: qualityGrade,
        // 移除分析时长字段
        targetForces: targetAnalysis.map(stat => `${stat.target_force}N`).join(', '),
        meanForce: Math.round((summary.mean_force || overallStats['均值'] || 0) * 10) / 10,
        stdForce: Math.round((summary.std_force || overallStats['标准差'] || 0) * 10) / 10,
        cvPercent: Math.round((summary.cv_percent || overallStats['变异系数'] || 0) * 10) / 10
      }
      
      console.log('解析后的分析结果:', summaryData.value)
    } else {
      console.warn('API返回数据格式不正确:', data)
      // 使用默认值
      summaryData.value = {
        successRate: 0,
        dataPoints: 0,
        cpValue: 0,
        qualityGrade: '未知',
        analysisTime: '未知',
        targetForces: [],
        meanForce: 0,
        stdForce: 0,
        cvPercent: 0
      }
    }
    
    // 更新文件名
    if (data.data_summary && data.data_summary.filename) {
      fileName.value = data.data_summary.filename
    }
    
  } catch (error) {
    console.error('获取分析结果失败:', error)
    // 设置错误状态的默认值
    summaryData.value = {
      successRate: 0,
      dataPoints: 0,
      cpValue: 0,
      qualityGrade: '获取失败',
      analysisTime: '未知',
      targetForces: [],
      meanForce: 0,
      stdForce: 0,
      cvPercent: 0
    }
  }
}

// 所有图表数据配置 - 更新为实际的文件名
const allCharts = computed(() => ({
  '基础分析': [
    { name: 'force_time_series', title: '时间序列图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/force_time_series.png` },
    { name: 'force_histogram', title: '分布直方图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/force_histogram.png` },
    { name: 'force_boxplot', title: '箱线图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/force_boxplot.png` },
    { name: 'deviation_analysis', title: '偏差分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/deviation_analysis.png` },
    { name: 'percentage_deviation', title: '百分比偏差', imageUrl: `${API_BASE}/api/chart/${taskId.value}/percentage_deviation.png` },
    { name: 'correlation_matrix', title: '相关性矩阵', imageUrl: `${API_BASE}/api/chart/${taskId.value}/correlation_matrix.png` },
    { name: 'coordinate_matrix', title: '坐标矩阵', imageUrl: `${API_BASE}/api/chart/${taskId.value}/coordinate_matrix.png` },
    { name: 'xy_heatmap', title: 'XY热力图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/xy_heatmap.png` }
  ],
  '控制图': [
    { name: 'shewhart_control', title: 'Shewhart控制图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/shewhart_control.png` },
    { name: 'moving_average', title: '移动平均控制图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/moving_average.png` },
    { name: 'xbar_r_chart', title: 'X-bar R控制图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/xbar_r_chart.png` },
    { name: 'cusum_chart', title: 'CUSUM控制图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/cusum_chart.png` },
    { name: 'ewma_chart', title: 'EWMA控制图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/ewma_chart.png` },
    { name: 'imr_chart', title: 'I-MR控制图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/imr_chart.png` },
    { name: 'run_chart', title: '运行图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/run_chart.png` }
  ],
  '专业质量分析': [
    { name: 'process_capability', title: '过程能力分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/process_capability.png` },
    { name: 'pareto_analysis', title: '帕雷托分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/pareto_analysis.png` },
    { name: 'residual_analysis', title: '残差分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/residual_analysis.png` },
    { name: 'qq_plot', title: 'Q-Q正态图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/qq_plot.png` },
    { name: 'radar_chart', title: '雷达图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/radar_chart.png` },
    { name: 'position_heatmap', title: '位置热力图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/position_heatmap.png` },
    { name: 'success_rate_trend', title: '成功率趋势', imageUrl: `${API_BASE}/api/chart/${taskId.value}/success_rate_trend.png` },
    { name: 'capability_histogram', title: '能力直方图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/capability_histogram.png` },
    { name: 'quality_dashboard', title: '质量仪表板', imageUrl: `${API_BASE}/api/chart/${taskId.value}/quality_dashboard.png` },
    { name: 'waterfall_chart', title: '瀑布图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/waterfall_chart.png` },
    { name: 'spatial_clustering', title: '空间聚类', imageUrl: `${API_BASE}/api/chart/${taskId.value}/spatial_clustering.png` },
    { name: 'parallel_coordinates', title: '平行坐标', imageUrl: `${API_BASE}/api/chart/${taskId.value}/parallel_coordinates.png` }
  ],
  '多维分析': [
    { name: 'projection_combined', title: '2D投影分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/projection_combined.png` },
    { name: 'error_spatial_distribution', title: '空间误差分布', imageUrl: `${API_BASE}/api/chart/${taskId.value}/error_spatial_distribution.png` },
    { name: 'spatial_correlation_matrix', title: '空间相关矩阵', imageUrl: `${API_BASE}/api/chart/${taskId.value}/spatial_correlation_matrix.png` },
    { name: 'error_distribution_analysis', title: '误差分布分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/error_distribution_analysis.png` },
    { name: 'error_qq_plot', title: '误差Q-Q图', imageUrl: `${API_BASE}/api/chart/${taskId.value}/error_qq_plot.png` },
    { name: 'success_rate', title: '成功率分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/success_rate.png` },
    { name: 'position_performance_comparison', title: '位置性能对比', imageUrl: `${API_BASE}/api/chart/${taskId.value}/position_performance_comparison.png` },
    { name: 'robot_consistency_analysis', title: '机器人一致性分析', imageUrl: `${API_BASE}/api/chart/${taskId.value}/robot_consistency_analysis.png` }
  ]
}))

// AI分析相关状态
const aiAnalysisLoading = ref(false)
const aiAnalysisContent = ref('')
const aiAnalysisGenerated = ref(false)

// 按钮加载状态
const wordReportLoading = ref(false)
const exportLoading = ref(false)

// 方法
const generateAIAnalysis = async () => {
  if (aiAnalysisLoading.value) return
  
  try {
    aiAnalysisLoading.value = true
    console.log('开始生成AI分析报告...')
    
    // 调用AI分析API
    const response = await fetch(`${API_BASE}/api/deepseek/generate-comprehensive-word-report?task_id=${taskId.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`API调用失败: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('AI分析API响应:', result)
    
    // 显示生成成功信息
    ElMessage.success('AI分析报告生成成功！')
    
    // 立即尝试获取分析结果
    try {
      const analysisResponse = await fetch(`${API_BASE}/api/deepseek/get/${taskId.value}`)
      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json()
        console.log('获取到的AI分析数据:', analysisData)
        if (analysisData.success && analysisData.data && analysisData.data.report) {
          aiAnalysisContent.value = analysisData.data.report
          aiAnalysisGenerated.value = true
          console.log('AI分析内容获取成功')
        } else {
          // 使用默认的分析内容
          console.log('AI分析数据格式不正确，使用默认内容')
          aiAnalysisContent.value = '# 智能分析报告\n\nAI分析功能正在优化中，请稍后重试。'
          aiAnalysisGenerated.value = true
        }
      } else {
        throw new Error('获取分析结果失败')
      }
    } catch (error) {
      console.error('获取AI分析结果失败:', error)
      aiAnalysisContent.value = '# 智能分析报告\n\n分析生成失败，请稍后重试。'
      aiAnalysisGenerated.value = true
    } finally {
      aiAnalysisLoading.value = false
    }
    
  } catch (error) {
    console.error('生成AI分析失败:', error)
    aiAnalysisLoading.value = false
    // 显示错误信息
    aiAnalysisContent.value = '# 智能分析报告\n\n分析生成失败，请检查网络连接后重试。'
    aiAnalysisGenerated.value = true
  }
}

// Word报告下载功能
const downloadWordReport = async () => {
  if (wordReportLoading.value) return
  
  try {
    wordReportLoading.value = true
    console.log('开始下载Word报告...')
    
    // 调用下载Word报告的API
    const response = await fetch(`${API_BASE}/api/download-comprehensive-report/${taskId.value}`, {
      method: 'GET'
    })
    
    if (!response.ok) {
      throw new Error(`下载失败: ${response.status}`)
    }
    
    // 获取文件流
    const blob = await response.blob()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `压力分析报告_${taskId.value}.docx`
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Word报告下载成功！')
    
  } catch (error) {
    console.error('下载Word报告失败:', error)
    ElMessage.error('Word报告下载失败，请稍后重试')
  } finally {
    wordReportLoading.value = false
  }
}

// 导出数据功能
const exportData = async () => {
  if (exportLoading.value) return
  
  try {
    exportLoading.value = true
    console.log('开始导出数据...')
    
    // 使用新的CSV下载API
    const downloadUrl = `${API_BASE}/api/download-csv/${taskId.value}`
    
    // 直接尝试下载文件
    const response = await fetch(downloadUrl)
    
    if (!response.ok) {
      throw new Error(`文件下载失败: ${response.status}`)
    }
    
    // 获取文件内容
    const blob = await response.blob()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `cleaned_data_${taskId.value}.csv`
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('数据导出成功！')
    
  } catch (error) {
    console.error('导出数据失败:', error)
    ElMessage.error('数据导出失败，请检查文件是否存在')
  } finally {
    exportLoading.value = false
  }
}

// 图表展示相关
const showAllCharts = ref(false)
const activeCategory = ref('基础分析')
const chartCategories = ref([
  { key: '基础分析', label: '基础分析' },
  { key: '控制图', label: '控制图分析' },
  { key: '专业质量分析', label: '质量分析' },
  { key: '多维分析', label: '多维分析' }
])
const selectedChart = ref(null)
const chartModalVisible = ref(false)

// 计算属性
const currentCategoryCharts = computed(() => {
  const categoryCharts = allCharts.value[activeCategory.value] || []
  // 始终显示所有图表，不再隐藏
  return categoryCharts
})

const totalChartsCount = computed(() => {
  return Object.values(allCharts.value).flat().length
})

const currentCategoryTotal = computed(() => {
  return allCharts.value[activeCategory.value]?.length || 0
})

const openChartModal = (chart) => {
  selectedChart.value = chart
  chartModalVisible.value = true
}

const downloadChart = (chart) => {
  if (chart?.imageUrl) {
    // 创建下载链接
    const link = document.createElement('a')
    link.href = chart.imageUrl
    link.download = `${chart.name}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// 检查DeepSeek分析是否存在
const checkAIAnalysisExists = async () => {
  try {
    console.log('检查AI分析是否存在...')
    const response = await fetch(`${API_BASE}/api/deepseek/get/${taskId.value}`)
    
    if (response.ok) {
      const analysisData = await response.json()
      console.log('AI分析检查结果:', analysisData)
      
      if (analysisData.success && analysisData.data && analysisData.data.report) {
        // 如果存在分析结果，直接显示
        aiAnalysisContent.value = analysisData.data.report
        aiAnalysisGenerated.value = true
        console.log('发现已存在的AI分析，直接显示')
        return true
      }
    }
    
    // 如果不存在分析结果
    console.log('未发现AI分析文件，显示生成按钮')
    aiAnalysisGenerated.value = false
    aiAnalysisContent.value = ''
    return false
    
  } catch (error) {
    console.error('检查AI分析失败:', error)
    aiAnalysisGenerated.value = false
    aiAnalysisContent.value = ''
    return false
  }
}

// 组件挂载
onMounted(async () => {
  console.log('分析结果页面已加载')
  await fetchAnalysisResults()
  
  // 检查是否已存在AI分析
  await checkAIAnalysisExists()
})
</script>

<style scoped>
.analysis-results-page {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  color: #303133;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 8px 15px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-dot.completed {
  background-color: #67C23A;
}

.status-text {
  color: #67C23A;
  font-size: 14px;
  font-weight: bold;
}

.download-btn {
  height: 25px;
  font-size: 11px;
  padding: 0 12px;
}

/* 结果摘要卡片 */
.results-summary-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 20px;
  height: 100px;
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.card-title {
  color: #303133;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.card-content {
  padding: 20px;
}

.summary-grid {
  display: flex;
  gap: 20px;
  justify-content: space-between;
}

.summary-item {
  background-color: #f0f9ff;
  border: 1px solid #409EFF;
  border-radius: 4px;
  padding: 15px;
  text-align: center;
  flex: 1;
  max-width: 120px;
  height: 55px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.summary-item.quality-grade {
  border-color: #67C23A;
  background-color: #f0f9ff;
}

.summary-item.analysis-time {
  border-color: #606266;
  background-color: #f0f9ff;
}

.summary-value {
  color: #409EFF;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.summary-value.quality {
  color: #67C23A;
}

.summary-item.analysis-time .summary-value {
  color: #606266;
}

.summary-label {
  color: #606266;
  font-size: 12px;
}

/* DeepSeek AI分析区域 */
.ai-analysis-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 20px;
  min-height: 160px;
}

.ai-generate-btn {
  background-color: #722ED1;
  border-color: #722ED1;
  height: 30px;
  font-size: 12px;
  padding: 0 20px;
}

.ai-analysis-content {
  background-color: #f9f9f9;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  min-height: 110px;
}

.analysis-title {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
}

.analysis-text {
  color: #606266;
  font-size: 12px;
  line-height: 1.6;
}

.analysis-text p {
  margin: 0 0 8px 0;
}

.recommendation {
  color: #67C23A;
  font-weight: bold;
  margin-top: 10px;
}

/* 图表展示区域 */
.charts-display-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  min-height: 240px;
}

.view-all-btn {
  background-color: #E6A23C;
  border-color: #E6A23C;
  height: 25px;
  font-size: 11px;
  padding: 0 20px;
}

.chart-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-item {
  background-color: #f0f0f0;
  color: #606266;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-item.active {
  background-color: #409EFF;
  color: white;
}

.tab-item:hover:not(.active) {
  background-color: #e0e0e0;
}

.charts-grid-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.chart-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  height: 320px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  cursor: pointer;
}

.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.chart-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
  margin: 0;
}

.chart-image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafbfc;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  min-height: 200px;
}

.chart-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s;
}

.chart-image:hover {
  transform: scale(1.02);
}

.fullscreen-btn {
  height: 32px;
  font-size: 12px;
  padding: 0 12px;
}

.image-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 12px;
  height: 100%;
  gap: 10px;
}

.modal-chart-container {
  width: 100%;
  height: 85vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  overflow: auto;
}

.modal-chart-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  cursor: zoom-in;
}

.modal-image-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 16px;
  height: 100%;
  gap: 15px;
}

.show-more {
  text-align: center;
  margin-top: 10px;
}

/* 图表放大模态窗口 */
.chart-modal {
  .modal-chart-container {
    padding: 10px;
  }

  .modal-image-slot {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    height: 100%;
  }

  .modal-footer {
    text-align: right;
  }
}

/* 确保模态框内的图片能完全显示 */
.chart-modal .el-dialog__body {
  padding: 10px !important;
  height: 85vh;
  overflow: hidden;
}

.chart-modal .el-dialog {
  margin: 0 !important;
}

/* Markdown内容样式 */
.markdown-content {
  line-height: 1.8;
  color: #303133;
  font-size: 14px;
}

.markdown-content .md-h1 {
  font-size: 24px;
  color: #2c3e50;
  border-bottom: 3px solid #409EFF;
  padding-bottom: 8px;
  margin: 30px 0 20px 0;
  font-weight: bold;
}

.markdown-content .md-h2 {
  font-size: 20px;
  color: #409EFF;
  margin: 25px 0 15px 0;
  font-weight: bold;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.markdown-content .md-h3 {
  font-size: 16px;
  color: #67C23A;
  margin: 20px 0 10px 0;
  font-weight: bold;
}

.markdown-content .md-h4 {
  font-size: 14px;
  color: #E6A23C;
  margin: 15px 0 8px 0;
  font-weight: bold;
}

.markdown-content .md-list {
  margin: 15px 0;
  padding-left: 25px;
}

.markdown-content .md-list li {
  margin: 8px 0;
  list-style-type: disc;
  line-height: 1.6;
}

.markdown-content .md-table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  font-size: 13px;
}

.markdown-content .md-table td {
  border: 1px solid #e4e7ed;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content .md-table tr:first-child td {
  background-color: #f5f7fa;
  font-weight: bold;
  color: #303133;
}

.markdown-content .md-table tr:nth-child(even) td {
  background-color: #fafafa;
}

.markdown-content strong {
  color: #E6A23C;
  font-weight: bold;
}

.markdown-content em {
  color: #909399;
  font-style: italic;
}

.markdown-content code {
  background-color: #f5f7fa;
  color: #e6a23c;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.markdown-content p {
  margin: 12px 0;
  text-align: justify;
  line-height: 1.7;
}

/* AI分析加载和占位符样式 */
.analysis-placeholder {
  text-align: center;
  color: #909399;
  padding: 40px 20px;
}

.analysis-placeholder .placeholder-text p {
  margin: 10px 0;
  font-size: 14px;
}

.analysis-loading {
  text-align: center;
  color: #409EFF;
  padding: 40px 20px;
}

.analysis-loading p {
  margin-top: 15px;
  font-size: 14px;
}
</style> 
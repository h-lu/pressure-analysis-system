// 图表配置文件 - 35个专业分析图表分类
export const CHART_CATEGORIES = {
  basic: {
    key: 'basic',
    label: '基础分析图表',
    description: '基础数据探索和描述性统计图表',
    icon: 'TrendCharts',
    color: '#409EFF',
    count: 8
  },
  control: {
    key: 'control',
    label: '统计过程控制',
    description: '质量控制和过程监控图表',
    icon: 'Monitor',
    color: '#67C23A',
    count: 7
  },
  quality: {
    key: 'quality',
    label: '质量分析图表',
    description: '深度质量分析和能力评估图表',
    icon: 'Medal',
    color: '#E6A23C',
    count: 12
  },
  multivariate: {
    key: 'multivariate',
    label: '多维分析图表',
    description: '多维数据分析和空间统计图表',
    icon: 'Connection',
    color: '#F56C6C',
    count: 8
  }
}

// 35个图表的详细配置
export const CHART_DEFINITIONS = {
  // ==================== 基础分析图表 (8个) ====================
  force_time_series: {
    name: 'force_time_series',
    title: '力值时间序列图',
    description: '显示力值随时间的变化趋势，用于识别时间相关的模式和异常',
    category: 'basic',
    complexity: 'low',
    analysisType: ['trend', 'temporal'],
    keywords: ['时间序列', '趋势分析', '时序模式'],
    insights: [
      '识别力值变化趋势',
      '检测时间相关异常',
      '评估测量稳定性'
    ]
  },
  force_distribution: {
    name: 'force_distribution',
    title: '力值分布图',
    description: '展示力值数据的概率分布，评估数据的正态性和分布特征',
    category: 'basic',
    complexity: 'low',
    analysisType: ['distribution', 'normality'],
    keywords: ['分布图', '概率密度', '正态性'],
    insights: [
      '评估数据分布形态',
      '检验正态性假设',
      '识别分布偏差'
    ]
  },
  force_boxplot: {
    name: 'force_boxplot',
    title: '力值箱线图',
    description: '通过四分位数展示力值的分布情况，快速识别异常值',
    category: 'basic',
    complexity: 'low',
    analysisType: ['outlier', 'distribution'],
    keywords: ['箱线图', '四分位数', '异常值检测'],
    insights: [
      '快速识别异常值',
      '比较不同组别差异',
      '评估数据离散程度'
    ]
  },
  absolute_deviation_boxplot: {
    name: 'absolute_deviation_boxplot',
    title: '绝对偏差箱线图',
    description: '显示各测量点相对于目标值的绝对偏差分布',
    category: 'basic',
    complexity: 'medium',
    analysisType: ['deviation', 'accuracy'],
    keywords: ['绝对偏差', '精度分析', '目标偏差'],
    insights: [
      '评估测量精度',
      '识别系统性偏差',
      '分析误差分布'
    ]
  },
  percentage_deviation_boxplot: {
    name: 'percentage_deviation_boxplot',
    title: '百分比偏差箱线图',
    description: '以百分比形式显示偏差分布，便于不同量级数据的比较',
    category: 'basic',
    complexity: 'medium',
    analysisType: ['deviation', 'percentage'],
    keywords: ['百分比偏差', '相对误差', '标准化偏差'],
    insights: [
      '标准化偏差比较',
      '评估相对精度',
      '跨量级数据对比'
    ]
  },
  interactive_3d_scatter: {
    name: 'interactive_3d_scatter',
    title: '交互式3D散点图',
    description: '三维空间中展示X、Y、Z坐标与力值的关系',
    category: 'basic',
    complexity: 'high',
    analysisType: ['spatial', 'correlation'],
    keywords: ['3D可视化', '空间分布', '多维关系'],
    insights: [
      '空间位置与力值关系',
      '3D数据模式识别',
      '立体分布特征'
    ]
  },
  scatter_matrix: {
    name: 'scatter_matrix',
    title: '散点矩阵图',
    description: '变量间两两关系的矩阵图，全面展示多变量相关性',
    category: 'basic',
    complexity: 'medium',
    analysisType: ['correlation', 'multivariate'],
    keywords: ['散点矩阵', '变量关系', '相关性分析'],
    insights: [
      '多变量关系全览',
      '识别线性/非线性关系',
      '变量间相关强度'
    ]
  },
  correlation_matrix: {
    name: 'correlation_matrix',
    title: '相关性矩阵图',
    description: '以热力图形式展示变量间的相关系数矩阵',
    category: 'basic',
    complexity: 'medium',
    analysisType: ['correlation', 'heatmap'],
    keywords: ['相关矩阵', '皮尔逊相关', '相关强度'],
    insights: [
      '量化变量关系强度',
      '识别强相关变量对',
      '多重共线性检测'
    ]
  },

  // ==================== 统计过程控制 (7个) ====================
  shewhart_control: {
    name: 'shewhart_control',
    title: 'Shewhart控制图',
    description: '经典的统计过程控制图，监控过程稳定性',
    category: 'control',
    complexity: 'medium',
    analysisType: ['spc', 'stability'],
    keywords: ['Shewhart', '控制限', '过程稳定性'],
    insights: [
      '过程是否受控',
      '识别特殊原因变异',
      '监控过程稳定性'
    ]
  },
  moving_average: {
    name: 'moving_average',
    title: '移动平均控制图',
    description: '使用移动平均平滑数据，提高异常检测敏感性',
    category: 'control',
    complexity: 'medium',
    analysisType: ['spc', 'smoothing'],
    keywords: ['移动平均', 'MA控制图', '数据平滑'],
    insights: [
      '平滑短期波动',
      '提高趋势检测能力',
      '减少假警报'
    ]
  },
  xbar_r_control: {
    name: 'xbar_r_control',
    title: 'X-R控制图',
    description: '同时监控过程均值和变异性的双控制图',
    category: 'control',
    complexity: 'high',
    analysisType: ['spc', 'variability'],
    keywords: ['X-R图', '均值控制', '变异控制'],
    insights: [
      '过程中心位置监控',
      '过程变异性监控',
      '双重质量控制'
    ]
  },
  cusum_control: {
    name: 'cusum_control',
    title: 'CUSUM控制图',
    description: '累积和控制图，对小偏移敏感的过程监控',
    category: 'control',
    complexity: 'high',
    analysisType: ['spc', 'drift'],
    keywords: ['CUSUM', '累积和', '漂移检测'],
    insights: [
      '检测过程微小漂移',
      '早期异常预警',
      '过程趋势监控'
    ]
  },
  ewma_control: {
    name: 'ewma_control',
    title: 'EWMA控制图',
    description: '指数加权移动平均控制图，平衡历史和当前数据',
    category: 'control',
    complexity: 'high',
    analysisType: ['spc', 'weighted'],
    keywords: ['EWMA', '指数平滑', '加权平均'],
    insights: [
      '历史数据权重递减',
      '平衡敏感性和稳定性',
      '优化异常检测'
    ]
  },
  imr_control: {
    name: 'imr_control',
    title: 'I-MR控制图',
    description: '个别值-移动极差控制图，适用于单个观测值',
    category: 'control',
    complexity: 'medium',
    analysisType: ['spc', 'individual'],
    keywords: ['I-MR图', '个别值', '移动极差'],
    insights: [
      '单值过程监控',
      '个别异常识别',
      '连续过程控制'
    ]
  },
  run_chart: {
    name: 'run_chart',
    title: '运行图',
    description: '简单的时序图，显示数据随时间的变化模式',
    category: 'control',
    complexity: 'low',
    analysisType: ['trend', 'pattern'],
    keywords: ['运行图', '时序模式', '趋势识别'],
    insights: [
      '识别运行模式',
      '检测趋势变化',
      '过程行为分析'
    ]
  },

  // ==================== 质量分析图表 (12个) ====================
  process_capability: {
    name: 'process_capability',
    title: '过程能力分析',
    description: '评估过程满足规格要求的能力',
    category: 'quality',
    complexity: 'high',
    analysisType: ['capability', 'specification'],
    keywords: ['过程能力', 'Cp/Cpk', '规格限'],
    insights: [
      '过程能力指数',
      '规格符合率',
      '过程改进方向'
    ]
  },
  pareto_chart: {
    name: 'pareto_chart',
    title: '帕雷托图',
    description: '识别影响质量的主要因素，遵循80/20法则',
    category: 'quality',
    complexity: 'medium',
    analysisType: ['ranking', 'priority'],
    keywords: ['帕雷托', '80/20法则', '主要因素'],
    insights: [
      '识别关键质量因素',
      '优先改进方向',
      '资源配置指导'
    ]
  },
  residual_analysis: {
    name: 'residual_analysis',
    title: '残差分析图',
    description: '分析模型拟合残差，验证模型假设',
    category: 'quality',
    complexity: 'high',
    analysisType: ['residual', 'validation'],
    keywords: ['残差分析', '模型验证', '拟合优度'],
    insights: [
      '模型拟合质量',
      '假设条件验证',
      '模型改进建议'
    ]
  },
  qq_normality: {
    name: 'qq_normality',
    title: 'Q-Q正态性检验图',
    description: '通过Q-Q图检验数据的正态性',
    category: 'quality',
    complexity: 'medium',
    analysisType: ['normality', 'distribution'],
    keywords: ['Q-Q图', '正态性检验', '分位数图'],
    insights: [
      '数据正态性评估',
      '分布偏离程度',
      '数据转换建议'
    ]
  },
  radar_chart: {
    name: 'radar_chart',
    title: '雷达图',
    description: '多维质量指标的综合评估图',
    category: 'quality',
    complexity: 'medium',
    analysisType: ['multivariate', 'assessment'],
    keywords: ['雷达图', '多维评估', '综合指标'],
    insights: [
      '多维度质量评估',
      '性能平衡分析',
      '改进优先级'
    ]
  },
  heatmap: {
    name: 'heatmap',
    title: '热力图',
    description: '以颜色强度展示数据密度和关系强度',
    category: 'quality',
    complexity: 'medium',
    analysisType: ['density', 'visualization'],
    keywords: ['热力图', '数据密度', '可视化'],
    insights: [
      '数据密度分布',
      '热点区域识别',
      '模式可视化'
    ]
  },
  success_rate_trend: {
    name: 'success_rate_trend',
    title: '成功率趋势图',
    description: '跟踪质量成功率随时间的变化趋势',
    category: 'quality',
    complexity: 'medium',
    analysisType: ['trend', 'success_rate'],
    keywords: ['成功率', '质量趋势', '达标率'],
    insights: [
      '质量改进趋势',
      '成功率变化',
      '目标达成情况'
    ]
  },
  capability_index: {
    name: 'capability_index',
    title: '能力指数图',
    description: '可视化展示各种过程能力指数',
    category: 'quality',
    complexity: 'high',
    analysisType: ['capability', 'index'],
    keywords: ['能力指数', 'Cp', 'Cpk', 'Pp', 'Ppk'],
    insights: [
      '多种能力指数对比',
      '过程稳定性评估',
      '规格符合能力'
    ]
  },
  quality_dashboard: {
    name: 'quality_dashboard',
    title: '质量仪表板',
    description: '集成多个质量指标的综合仪表板',
    category: 'quality',
    complexity: 'high',
    analysisType: ['dashboard', 'comprehensive'],
    keywords: ['仪表板', '综合指标', '质量监控'],
    insights: [
      '质量状态一览',
      '关键指标监控',
      '决策支持信息'
    ]
  },
  waterfall_chart: {
    name: 'waterfall_chart',
    title: '瀑布图',
    description: '展示各因素对总体质量的贡献分解',
    category: 'quality',
    complexity: 'medium',
    analysisType: ['decomposition', 'contribution'],
    keywords: ['瀑布图', '因素分解', '贡献分析'],
    insights: [
      '质量因素贡献度',
      '改进效果量化',
      '成本效益分析'
    ]
  },
  spatial_clustering: {
    name: 'spatial_clustering',
    title: '空间聚类图',
    description: '基于空间位置的数据聚类分析',
    category: 'quality',
    complexity: 'high',
    analysisType: ['clustering', 'spatial'],
    keywords: ['空间聚类', '地理分析', '区域特征'],
    insights: [
      '空间数据聚类',
      '区域质量模式',
      '地理影响因素'
    ]
  },
  parallel_coordinates: {
    name: 'parallel_coordinates',
    title: '平行坐标图',
    description: '多维数据的平行坐标可视化',
    category: 'quality',
    complexity: 'high',
    analysisType: ['multivariate', 'parallel'],
    keywords: ['平行坐标', '多维可视化', '模式识别'],
    insights: [
      '多维数据模式',
      '变量关系网络',
      '异常模式识别'
    ]
  },

  // ==================== 多维分析图表 (8个) ====================
  xy_heatmap: {
    name: 'xy_heatmap',
    title: 'XY热力图',
    description: '基于XY坐标的二维热力分布图',
    category: 'multivariate',
    complexity: 'medium',
    analysisType: ['spatial', 'density'],
    keywords: ['XY热力图', '空间密度', '二维分布'],
    insights: [
      'XY平面数据密度',
      '空间热点识别',
      '位置相关模式'
    ]
  },
  projection_2d: {
    name: 'projection_2d',
    title: '2D投影图',
    description: '高维数据的二维投影可视化',
    category: 'multivariate',
    complexity: 'high',
    analysisType: ['projection', 'dimensionality'],
    keywords: ['降维投影', 'PCA', '数据可视化'],
    insights: [
      '高维数据降维',
      '主要变异方向',
      '数据结构简化'
    ]
  },
  position_anomaly_heatmap: {
    name: 'position_anomaly_heatmap',
    title: '位置异常热力图',
    description: '显示空间位置上的异常值分布热力图',
    category: 'multivariate',
    complexity: 'high',
    analysisType: ['anomaly', 'spatial'],
    keywords: ['位置异常', '空间异常', '异常热力图'],
    insights: [
      '空间异常分布',
      '异常聚集区域',
      '位置相关异常'
    ]
  },
  spatial_density: {
    name: 'spatial_density',
    title: '空间密度图',
    description: '三维空间中的数据点密度分布',
    category: 'multivariate',
    complexity: 'high',
    analysisType: ['density', 'spatial'],
    keywords: ['空间密度', '3D密度', '体积分布'],
    insights: [
      '3D空间密度',
      '体积数据分布',
      '空间聚集模式'
    ]
  },
  multivariate_relations: {
    name: 'multivariate_relations',
    title: '多元关系图',
    description: '复杂多变量关系的网络图展示',
    category: 'multivariate',
    complexity: 'high',
    analysisType: ['network', 'relationships'],
    keywords: ['多元关系', '网络图', '关系网络'],
    insights: [
      '变量关系网络',
      '复杂关系模式',
      '影响路径分析'
    ]
  },
  anomaly_patterns: {
    name: 'anomaly_patterns',
    title: '异常模式图',
    description: '异常数据的模式和分布特征分析',
    category: 'multivariate',
    complexity: 'high',
    analysisType: ['anomaly', 'pattern'],
    keywords: ['异常模式', '异常分析', '模式识别'],
    insights: [
      '异常数据模式',
      '异常类型分类',
      '异常成因分析'
    ]
  },
  quality_distribution_map: {
    name: 'quality_distribution_map',
    title: '质量分布图',
    description: '质量等级在空间上的分布地图',
    category: 'multivariate',
    complexity: 'medium',
    analysisType: ['quality', 'distribution'],
    keywords: ['质量分布', '等级地图', '空间质量'],
    insights: [
      '质量空间分布',
      '质量等级区域',
      '地理质量模式'
    ]
  },
  comprehensive_assessment: {
    name: 'comprehensive_assessment',
    title: '综合评估图',
    description: '多维度质量指标的综合评估可视化',
    category: 'multivariate',
    complexity: 'high',
    analysisType: ['assessment', 'comprehensive'],
    keywords: ['综合评估', '多维评价', '整体质量'],
    insights: [
      '综合质量评估',
      '多维度集成',
      '整体性能评价'
    ]
  }
}

// 获取指定类别的图表
export const getChartsByCategory = (categoryKey) => {
  return Object.values(CHART_DEFINITIONS).filter(chart => chart.category === categoryKey)
}

// 获取所有图表名称列表
export const getAllChartNames = () => {
  return Object.keys(CHART_DEFINITIONS)
}

// 根据复杂度筛选图表
export const getChartsByComplexity = (complexity) => {
  return Object.values(CHART_DEFINITIONS).filter(chart => chart.complexity === complexity)
}

// 根据分析类型筛选图表
export const getChartsByAnalysisType = (analysisType) => {
  return Object.values(CHART_DEFINITIONS).filter(chart => 
    chart.analysisType.includes(analysisType)
  )
}

// 搜索图表
export const searchCharts = (keyword) => {
  const lowerKeyword = keyword.toLowerCase()
  return Object.values(CHART_DEFINITIONS).filter(chart => 
    chart.title.toLowerCase().includes(lowerKeyword) ||
    chart.description.toLowerCase().includes(lowerKeyword) ||
    chart.keywords.some(kw => kw.toLowerCase().includes(lowerKeyword))
  )
}

// 获取图表统计信息
export const getChartStatistics = () => {
  const stats = {
    total: Object.keys(CHART_DEFINITIONS).length,
    byCategory: {},
    byComplexity: {
      low: 0,
      medium: 0,
      high: 0
    }
  }
  
  Object.values(CHART_CATEGORIES).forEach(category => {
    stats.byCategory[category.key] = {
      label: category.label,
      count: getChartsByCategory(category.key).length,
      color: category.color
    }
  })
  
  Object.values(CHART_DEFINITIONS).forEach(chart => {
    stats.byComplexity[chart.complexity]++
  })
  
  return stats
} 
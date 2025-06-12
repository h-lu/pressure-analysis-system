// 35个图表完整配置
export const chartConfigs = {
  // ================================
  // 基础分析图表 (8个)
  // ================================
  force_time_series: {
    title: '力值时间序列图',
    category: 'basic',
    complexity: 'basic',
    description: '显示力值随时间变化的趋势，帮助识别数据的时间模式和趋势',
    keywords: ['时间序列', '趋势分析', '数据模式'],
    analysisTypes: ['趋势分析', '时间模式'],
    insights: [
      '观察力值随时间的整体变化趋势',
      '识别数据中的周期性模式',
      '检测异常时间点和突变'
    ],
    useCases: ['数据预览', '趋势分析', '异常检测'],
    complexity_score: 1
  },

  force_distribution: {
    title: '力值分布图',
    category: 'basic',
    complexity: 'basic',
    description: '展示力值的统计分布情况，包括频率分布和概率密度',
    keywords: ['分布分析', '频率统计', '概率密度'],
    analysisTypes: ['分布分析', '统计描述'],
    insights: [
      '了解力值的分布形状和特征',
      '识别数据的集中趋势和离散程度',
      '检测分布的偏斜度和峰态'
    ],
    useCases: ['数据分布', '统计分析', '质量评估'],
    complexity_score: 1
  },

  force_boxplot: {
    title: '力值箱线图',
    category: 'basic',
    complexity: 'basic',
    description: '通过四分位数显示力值的分布特征，有效识别异常值',
    keywords: ['箱线图', '四分位数', '异常值检测'],
    analysisTypes: ['分布分析', '异常检测'],
    insights: [
      '快速了解数据的五数概括',
      '直观识别异常值和离群点',
      '比较不同组别的分布差异'
    ],
    useCases: ['异常检测', '数据比较', '质量控制'],
    complexity_score: 1
  },

  absolute_deviation_boxplot: {
    title: '绝对偏差箱线图',
    category: 'basic',
    complexity: 'intermediate',
    description: '显示实际力值与目标力值的绝对偏差分布，评估测量精度',
    keywords: ['绝对偏差', '精度分析', '目标偏差'],
    analysisTypes: ['精度分析', '偏差评估'],
    insights: [
      '评估测量系统的绝对精度',
      '识别系统性偏差和随机误差',
      '确定测量的可接受范围'
    ],
    useCases: ['精度评估', '系统校准', '质量控制'],
    complexity_score: 2
  },

  percentage_deviation_boxplot: {
    title: '百分比偏差箱线图',
    category: 'basic',
    complexity: 'intermediate',
    description: '显示相对偏差的分布，便于不同量级的力值比较',
    keywords: ['百分比偏差', '相对误差', '量级比较'],
    analysisTypes: ['相对精度', '比较分析'],
    insights: [
      '评估不同力值水平的相对精度',
      '比较各目标力值的测量稳定性',
      '识别与力值相关的系统误差'
    ],
    useCases: ['相对精度', '多级比较', '性能评估'],
    complexity_score: 2
  },

  interactive_3d_scatter: {
    title: '交互式3D散点图',
    category: 'basic',
    complexity: 'intermediate',
    description: '三维空间中展示力值、X坐标、Y坐标的关系，支持交互式探索',
    keywords: ['3D可视化', '空间分布', '交互探索'],
    analysisTypes: ['空间分析', '多维关系'],
    insights: [
      '发现力值与位置的三维空间关系',
      '识别空间中的聚类和模式',
      '检测位置相关的测量偏差'
    ],
    useCases: ['空间分析', '位置效应', '多维探索'],
    complexity_score: 3
  },

  scatter_matrix: {
    title: '散点矩阵图',
    category: 'basic',
    complexity: 'intermediate',
    description: '展示所有变量之间的两两关系，快速识别变量间的关联性',
    keywords: ['散点矩阵', '变量关系', '关联分析'],
    analysisTypes: ['关系分析', '多变量探索'],
    insights: [
      '全面了解变量间的线性关系',
      '识别强相关和弱相关的变量对',
      '发现意外的关联模式'
    ],
    useCases: ['关系探索', '变量筛选', '模式发现'],
    complexity_score: 3
  },

  correlation_matrix: {
    title: '相关性矩阵图',
    category: 'basic',
    complexity: 'intermediate',
    description: '量化显示变量间的相关系数，用热力图形式直观展示',
    keywords: ['相关系数', '热力图', '关联强度'],
    analysisTypes: ['相关分析', '关联度量'],
    insights: [
      '量化变量间的线性关联强度',
      '识别高度相关的变量组合',
      '发现反向关联和独立变量'
    ],
    useCases: ['相关分析', '特征选择', '数据理解'],
    complexity_score: 2
  },

  // ================================
  // 统计过程控制图表 (7个)
  // ================================
  shewhart_control: {
    title: 'Shewhart控制图',
    category: 'control',
    complexity: 'intermediate',
    description: '经典的统计过程控制图，监控过程稳定性和异常点',
    keywords: ['控制图', '过程控制', 'UCL/LCL'],
    analysisTypes: ['过程控制', '稳定性监控'],
    insights: [
      '监控过程是否处于统计控制状态',
      '识别特殊原因导致的变异',
      '评估过程能力和稳定性'
    ],
    useCases: ['质量控制', '过程监控', '异常预警'],
    complexity_score: 3
  },

  moving_average: {
    title: '移动平均控制图',
    category: 'control',
    complexity: 'intermediate',
    description: '使用移动平均平滑数据波动，更好地识别趋势变化',
    keywords: ['移动平均', '趋势识别', '平滑处理'],
    analysisTypes: ['趋势分析', '过程控制'],
    insights: [
      '平滑短期波动，突出长期趋势',
      '提高小幅度变化的检测能力',
      '减少误报警，提高控制效果'
    ],
    useCases: ['趋势监控', '过程优化', '预防控制'],
    complexity_score: 3
  },

  xbar_r_control: {
    title: 'X-R控制图',
    category: 'control',
    complexity: 'advanced',
    description: '同时监控过程均值和变异性，是制造业质量控制的标准工具',
    keywords: ['均值控制', '极差控制', '双重监控'],
    analysisTypes: ['均值监控', '变异控制'],
    insights: [
      '同时监控过程中心和散布',
      '区分均值偏移和变异增大',
      '全面评估过程稳定性'
    ],
    useCases: ['制造控制', '质量管理', '过程改进'],
    complexity_score: 4
  },

  cusum_control: {
    title: 'CUSUM控制图',
    category: 'control',
    complexity: 'advanced',
    description: '累积和控制图，对小幅度的过程偏移非常敏感',
    keywords: ['累积和', '微小偏移', '敏感检测'],
    analysisTypes: ['偏移检测', '累积监控'],
    insights: [
      '快速检测过程均值的小幅偏移',
      '提供偏移开始时间的准确估计',
      '对渐进性变化特别敏感'
    ],
    useCases: ['精密控制', '早期预警', '质量改进'],
    complexity_score: 4
  },

  ewma_control: {
    title: 'EWMA控制图',
    category: 'control',
    complexity: 'advanced',
    description: '指数加权移动平均控制图，平衡历史数据和当前数据的影响',
    keywords: ['指数加权', '历史记忆', '平衡控制'],
    analysisTypes: ['加权监控', '记忆控制'],
    insights: [
      '考虑历史数据的累积影响',
      '对中等程度的偏移最为敏感',
      '提供平滑的控制响应'
    ],
    useCases: ['连续监控', '预测控制', '过程优化'],
    complexity_score: 4
  },

  imr_control: {
    title: 'IMR控制图',
    category: 'control',
    complexity: 'intermediate',
    description: '个体-移动极差控制图，适用于单个测量值的过程控制',
    keywords: ['个体值', '移动极差', '单点控制'],
    analysisTypes: ['个体监控', '变异控制'],
    insights: [
      '监控单个测量值的稳定性',
      '评估连续测量间的变异',
      '适用于慢速或昂贵的测量过程'
    ],
    useCases: ['个体控制', '高价测试', '关键监控'],
    complexity_score: 3
  },

  run_chart: {
    title: '趋势图',
    category: 'control',
    complexity: 'basic',
    description: '简单的时间序列图，显示数据的运行趋势和模式',
    keywords: ['运行图', '时间趋势', '模式识别'],
    analysisTypes: ['趋势分析', '模式识别'],
    insights: [
      '观察数据的时间序列模式',
      '识别上升、下降或周期性趋势',
      '检测非随机的运行模式'
    ],
    useCases: ['初步分析', '趋势监控', '简单控制'],
    complexity_score: 1
  },

  // ================================
  // 专业质量分析图表 (12个) 
  // ================================
  process_capability: {
    title: '过程能力分析',
    category: 'quality',
    complexity: 'advanced',
    description: '评估过程满足规格要求的能力，计算Cp、Cpk等能力指数',
    keywords: ['过程能力', 'Cp指数', 'Cpk指数'],
    analysisTypes: ['能力评估', '规格分析'],
    insights: [
      '量化过程满足规格的能力',
      '评估过程中心化程度',
      '预测不合格品率'
    ],
    useCases: ['能力评估', '过程改进', '质量预测'],
    complexity_score: 4
  },

  pareto_chart: {
    title: '帕雷托图',
    category: 'quality',
    complexity: 'intermediate',
    description: '基于80/20法则，识别影响质量的主要因素',
    keywords: ['帕雷托', '80/20法则', '主要因素'],
    analysisTypes: ['因素分析', '优先级排序'],
    insights: [
      '识别影响质量的关键因素',
      '确定改进工作的优先级',
      '量化不同因素的相对重要性'
    ],
    useCases: ['问题分析', '改进优先级', '资源分配'],
    complexity_score: 2
  },

  residual_analysis: {
    title: '残差分析图',
    category: 'quality',
    complexity: 'advanced',
    description: '分析模型拟合的残差，检验模型假设和识别异常',
    keywords: ['残差分析', '模型诊断', '假设检验'],
    analysisTypes: ['模型诊断', '假设验证'],
    insights: [
      '验证模型的适用性和准确性',
      '识别模型未能解释的模式',
      '检测异常数据点和影响点'
    ],
    useCases: ['模型验证', '异常检测', '模型改进'],
    complexity_score: 4
  },

  qq_normality: {
    title: 'Q-Q正态性检验图',
    category: 'quality',
    complexity: 'intermediate',
    description: '检验数据是否符合正态分布，为后续统计分析提供依据',
    keywords: ['正态性检验', 'QQ图', '分布验证'],
    analysisTypes: ['分布检验', '正态性评估'],
    insights: [
      '评估数据的正态性程度',
      '识别分布的偏离类型',
      '为选择统计方法提供依据'
    ],
    useCases: ['分布检验', '方法选择', '数据转换'],
    complexity_score: 3
  },

  radar_chart: {
    title: '雷达图',
    category: 'quality',
    complexity: 'intermediate',
    description: '多维度性能评估，直观比较不同指标的表现',
    keywords: ['雷达图', '多维评估', '性能比较'],
    analysisTypes: ['多维分析', '性能评估'],
    insights: [
      '全面评估多个质量维度',
      '识别优势和薄弱环节',
      '支持综合性能比较'
    ],
    useCases: ['综合评估', '性能监控', '标杆比较'],
    complexity_score: 2
  },

  heatmap: {
    title: '热力图',
    category: 'quality',
    complexity: 'intermediate',
    description: '二维热力图显示数据的空间分布和密度特征',
    keywords: ['热力图', '空间分布', '密度可视化'],
    analysisTypes: ['空间分析', '密度分析'],
    insights: [
      '显示数据在二维空间的分布',
      '识别高密度和低密度区域',
      '发现空间聚集和分散模式'
    ],
    useCases: ['空间分析', '密度研究', '模式发现'],
    complexity_score: 2
  },

  success_rate_trend: {
    title: '成功率趋势图',
    category: 'quality',
    complexity: 'intermediate',
    description: '追踪质量成功率随时间的变化趋势，监控质量改进效果',
    keywords: ['成功率', '质量趋势', '改进监控'],
    analysisTypes: ['成功率分析', '趋势监控'],
    insights: [
      '监控质量水平的时间变化',
      '评估改进措施的效果',
      '预测未来的质量表现'
    ],
    useCases: ['质量监控', '改进评估', '目标管理'],
    complexity_score: 2
  },

  capability_index: {
    title: '能力指数图',
    category: 'quality',
    complexity: 'advanced',
    description: '可视化展示各种过程能力指数，包括Cp、Cpk、Pp、Ppk',
    keywords: ['能力指数', 'Cp/Cpk', 'Pp/Ppk'],
    analysisTypes: ['能力指数', '性能评估'],
    insights: [
      '比较不同能力指数的表现',
      '评估短期和长期过程能力',
      '识别过程改进的潜力'
    ],
    useCases: ['能力评估', '性能比较', '改进指导'],
    complexity_score: 4
  },

  quality_dashboard: {
    title: '质量仪表盘',
    category: 'quality',
    complexity: 'advanced',
    description: '综合质量指标的仪表盘视图，提供全面的质量状态概览',
    keywords: ['质量仪表盘', '综合指标', '状态概览'],
    analysisTypes: ['综合监控', '状态评估'],
    insights: [
      '提供质量状态的全景视图',
      '快速识别关键质量问题',
      '支持高层决策和管理'
    ],
    useCases: ['管理报告', '状态监控', '决策支持'],
    complexity_score: 4
  },

  waterfall_chart: {
    title: '瀑布图',
    category: 'quality',
    complexity: 'intermediate',
    description: '展示各因素对总体质量指标的累积贡献',
    keywords: ['瀑布图', '因素贡献', '累积影响'],
    analysisTypes: ['因素分析', '贡献分解'],
    insights: [
      '量化各因素的具体贡献',
      '理解因素间的累积效应',
      '指导改进工作的重点'
    ],
    useCases: ['因素分析', '改进指导', '贡献评估'],
    complexity_score: 3
  },

  spatial_clustering: {
    title: '空间聚类图',
    category: 'quality',
    complexity: 'advanced',
    description: '识别测量点的空间聚类模式，发现位置相关的质量问题',
    keywords: ['空间聚类', '位置分析', '聚类识别'],
    analysisTypes: ['聚类分析', '空间模式'],
    insights: [
      '识别测量点的聚类模式',
      '发现位置相关的质量规律',
      '指导传感器布置和改进'
    ],
    useCases: ['空间分析', '传感器优化', '质量改进'],
    complexity_score: 4
  },

  parallel_coordinates: {
    title: '平行坐标图',
    category: 'quality',
    complexity: 'advanced',
    description: '多维数据的平行坐标可视化，识别数据模式和异常',
    keywords: ['平行坐标', '多维可视化', '模式识别'],
    analysisTypes: ['多维分析', '模式识别'],
    insights: [
      '可视化高维数据的模式',
      '识别变量间的复杂关系',
      '发现多维空间中的异常'
    ],
    useCases: ['多维分析', '模式发现', '异常检测'],
    complexity_score: 4
  },

  // ================================
  // 多维分析图表 (8个)
  // ================================
  xy_heatmap: {
    title: 'XY位置热力图',
    category: 'multivariate',
    complexity: 'intermediate',
    description: '显示力值在XY位置平面上的分布热力图，识别空间模式',
    keywords: ['位置热力图', 'XY分布', '空间模式'],
    analysisTypes: ['空间分析', '位置效应'],
    insights: [
      '识别力值的空间分布模式',
      '发现位置相关的测量偏差',
      '优化测量点的空间布局'
    ],
    useCases: ['空间优化', '位置分析', '布局改进'],
    complexity_score: 3
  },

  projection_2d: {
    title: '2D投影图',
    category: 'multivariate',
    complexity: 'advanced',
    description: '将高维数据投影到2D平面，保持数据的主要结构特征',
    keywords: ['降维投影', '主成分', '结构保持'],
    analysisTypes: ['降维分析', '结构探索'],
    insights: [
      '在低维空间中保持数据结构',
      '识别数据的主要变异方向',
      '发现隐藏的数据模式'
    ],
    useCases: ['降维分析', '数据探索', '模式发现'],
    complexity_score: 4
  },

  position_anomaly_heatmap: {
    title: '位置异常热力图',
    category: 'multivariate',
    complexity: 'advanced',
    description: '标识出各个位置的异常程度，帮助定位问题区域',
    keywords: ['位置异常', '异常定位', '问题区域'],
    analysisTypes: ['异常检测', '位置诊断'],
    insights: [
      '精确定位异常发生的位置',
      '量化不同区域的异常程度',
      '指导针对性的问题解决'
    ],
    useCases: ['异常定位', '故障诊断', '针对改进'],
    complexity_score: 4
  },

  spatial_density: {
    title: '空间密度图',
    category: 'multivariate',
    complexity: 'intermediate',
    description: '显示测量点在空间中的密度分布，优化测量策略',
    keywords: ['空间密度', '测量分布', '策略优化'],
    analysisTypes: ['密度分析', '分布优化'],
    insights: [
      '评估测量点的空间覆盖度',
      '识别测量密度不足的区域',
      '优化未来的测量策略'
    ],
    useCases: ['测量优化', '覆盖评估', '策略改进'],
    complexity_score: 3
  },

  multivariate_relations: {
    title: '多元关系图',
    category: 'multivariate',
    complexity: 'advanced',
    description: '展示多个变量之间的复杂关系网络，识别关键关联',
    keywords: ['多元关系', '关系网络', '关联分析'],
    analysisTypes: ['关系分析', '网络分析'],
    insights: [
      '理解变量间的复杂关联',
      '识别关键的中介变量',
      '发现意外的关系模式'
    ],
    useCases: ['关系探索', '机制理解', '模型构建'],
    complexity_score: 4
  },

  anomaly_patterns: {
    title: '异常模式图',
    category: 'multivariate',
    complexity: 'advanced',
    description: '识别和可视化各种类型的异常模式，支持异常分类',
    keywords: ['异常模式', '模式分类', '异常类型'],
    analysisTypes: ['异常分析', '模式识别'],
    insights: [
      '识别不同类型的异常模式',
      '理解异常的发生机制',
      '建立异常预警体系'
    ],
    useCases: ['异常分类', '预警系统', '质量改进'],
    complexity_score: 4
  },

  quality_distribution_map: {
    title: '质量分布图',
    category: 'multivariate',
    complexity: 'advanced',
    description: '在空间中映射质量等级的分布，支持质量管理决策',
    keywords: ['质量分布', '等级映射', '管理决策'],
    analysisTypes: ['质量映射', '等级分析'],
    insights: [
      '可视化质量在空间中的分布',
      '识别质量等级的区域特征',
      '支持基于位置的质量管理'
    ],
    useCases: ['质量管理', '区域分析', '决策支持'],
    complexity_score: 4
  },

  comprehensive_assessment: {
    title: '综合评估图',
    category: 'multivariate',
    complexity: 'advanced',
    description: '整合所有分析维度的综合评估结果，提供最终的质量判断',
    keywords: ['综合评估', '整合分析', '最终判断'],
    analysisTypes: ['综合分析', '最终评估'],
    insights: [
      '提供基于多维度的综合评估',
      '整合所有分析结果',
      '支持最终的质量决策'
    ],
    useCases: ['最终评估', '综合决策', '报告总结'],
    complexity_score: 5
  }
}

// 图表分类配置
export const chartCategories = {
  basic: {
    key: 'basic',
    label: '基础分析图表',
    description: '基础的数据探索和描述性分析图表',
    icon: 'Chart',
    color: '#409EFF',
    charts: [
      'force_time_series',
      'force_distribution', 
      'force_boxplot',
      'absolute_deviation_boxplot',
      'percentage_deviation_boxplot',
      'interactive_3d_scatter',
      'scatter_matrix',
      'correlation_matrix'
    ]
  },
  
  control: {
    key: 'control',
    label: '统计过程控制',
    description: '统计过程控制图表，监控过程稳定性',
    icon: 'Monitor',
    color: '#67C23A',
    charts: [
      'shewhart_control',
      'moving_average', 
      'xbar_r_control',
      'cusum_control',
      'ewma_control',
      'imr_control',
      'run_chart'
    ]
  },
  
  quality: {
    key: 'quality',
    label: '专业质量分析',
    description: '专业的质量分析和评估图表',
    icon: 'Medal',
    color: '#E6A23C',
    charts: [
      'process_capability',
      'pareto_chart',
      'residual_analysis',
      'qq_normality',
      'radar_chart',
      'heatmap',
      'success_rate_trend',
      'capability_index',
      'quality_dashboard',
      'waterfall_chart',
      'spatial_clustering',
      'parallel_coordinates'
    ]
  },
  
  multivariate: {
    key: 'multivariate',
    label: '多维分析图表',
    description: '多变量和高维数据分析图表',
    icon: 'Connection',
    color: '#F56C6C',
    charts: [
      'xy_heatmap',
      'projection_2d',
      'position_anomaly_heatmap',
      'spatial_density',
      'multivariate_relations',
      'anomaly_patterns',
      'quality_distribution_map',
      'comprehensive_assessment'
    ]
  }
}

// 复杂度等级配置
export const complexityLevels = {
  basic: {
    label: '基础',
    color: '#67C23A',
    description: '简单易懂，适合初学者',
    level: 1
  },
  intermediate: {
    label: '中级', 
    color: '#E6A23C',
    description: '需要一定统计知识',
    level: 2
  },
  advanced: {
    label: '高级',
    color: '#F56C6C', 
    description: '需要专业统计背景',
    level: 3
  }
}

// 工具函数
export const chartUtils = {
  // 获取图表配置
  getChartConfig(chartName) {
    return chartConfigs[chartName] || null
  },

  // 获取分类下的所有图表
  getChartsByCategory(categoryKey) {
    const category = chartCategories[categoryKey]
    if (!category) return []
    
    return category.charts.map(chartName => ({
      name: chartName,
      config: chartConfigs[chartName]
    }))
  },

  // 搜索图表
  searchCharts(query) {
    const results = []
    const searchTerm = query.toLowerCase()
    
    Object.entries(chartConfigs).forEach(([name, config]) => {
      const searchable = [
        config.title,
        config.description,
        ...config.keywords,
        ...config.analysisTypes
      ].join(' ').toLowerCase()
      
      if (searchable.includes(searchTerm)) {
        results.push({
          name,
          config,
          relevance: this.calculateRelevance(searchable, searchTerm)
        })
      }
    })
    
    return results.sort((a, b) => b.relevance - a.relevance)
  },

  // 按复杂度筛选
  filterByComplexity(complexityLevel) {
    const results = []
    
    Object.entries(chartConfigs).forEach(([name, config]) => {
      if (config.complexity === complexityLevel) {
        results.push({ name, config })
      }
    })
    
    return results
  },

  // 按关键词筛选
  filterByKeywords(keywords) {
    const results = []
    const keywordSet = new Set(keywords.map(k => k.toLowerCase()))
    
    Object.entries(chartConfigs).forEach(([name, config]) => {
      const chartKeywords = config.keywords.map(k => k.toLowerCase())
      const intersection = chartKeywords.filter(k => keywordSet.has(k))
      
      if (intersection.length > 0) {
        results.push({
          name,
          config,
          matchCount: intersection.length
        })
      }
    })
    
    return results.sort((a, b) => b.matchCount - a.matchCount)
  },

  // 计算搜索相关性
  calculateRelevance(text, searchTerm) {
    const words = searchTerm.split(' ')
    let score = 0
    
    words.forEach(word => {
      const regex = new RegExp(word, 'gi')
      const matches = text.match(regex)
      if (matches) {
        score += matches.length
      }
    })
    
    return score
  },

  // 获取推荐图表
  getRecommendedCharts(currentChart, count = 3) {
    const current = chartConfigs[currentChart]
    if (!current) return []
    
    const recommendations = []
    
    Object.entries(chartConfigs).forEach(([name, config]) => {
      if (name === currentChart) return
      
      let score = 0
      
      // 相同分类加分
      if (config.category === current.category) score += 3
      
      // 相似复杂度加分
      if (config.complexity === current.complexity) score += 2
      
      // 共同关键词加分
      const commonKeywords = config.keywords.filter(k => 
        current.keywords.includes(k)
      )
      score += commonKeywords.length
      
      // 共同分析类型加分
      const commonTypes = config.analysisTypes.filter(t =>
        current.analysisTypes.includes(t)
      )
      score += commonTypes.length * 2
      
      if (score > 0) {
        recommendations.push({ name, config, score })
      }
    })
    
    return recommendations
      .sort((a, b) => b.score - a.score)
      .slice(0, count)
  },

  // 获取所有图表名称列表
  getAllChartNames() {
    return Object.keys(chartConfigs)
  },

  // 获取分类统计
  getCategoryStats() {
    const stats = {}
    
    Object.entries(chartCategories).forEach(([key, category]) => {
      stats[key] = {
        ...category,
        count: category.charts.length,
        complexityBreakdown: this.getComplexityBreakdown(category.charts)
      }
    })
    
    return stats
  },

  // 获取复杂度分布
  getComplexityBreakdown(chartNames) {
    const breakdown = { basic: 0, intermediate: 0, advanced: 0 }
    
    chartNames.forEach(name => {
      const config = chartConfigs[name]
      if (config && breakdown.hasOwnProperty(config.complexity)) {
        breakdown[config.complexity]++
      }
    })
    
    return breakdown
  }
}

export default chartConfigs 
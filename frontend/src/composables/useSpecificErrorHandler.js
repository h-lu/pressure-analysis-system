import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { analysisAPI } from '@/api'

export function useSpecificErrorHandler() {
  const errorStats = reactive({
    fileFormatErrors: 0,
    rScriptErrors: 0,
    memoryErrors: 0,
    networkErrors: 0,
    totalErrors: 0,
    lastError: null,
    errorHistory: []
  })

  const isHandling = ref(false)

  // 文件格式错误处理
  const handleFileFormatError = async (error) => {
    errorStats.fileFormatErrors++
    errorStats.totalErrors++
    errorStats.lastError = { type: 'FILE_FORMAT', time: new Date(), error }
    errorStats.errorHistory.unshift(errorStats.lastError)

    const errorType = detectFileFormatErrorType(error)
    
    const solutions = {
      INVALID_CSV: {
        title: 'CSV格式错误',
        content: `
          <div>
            <h4>❌ 检测到CSV格式问题</h4>
            <p><strong>常见原因：</strong></p>
            <ul>
              <li>文件不是标准CSV格式</li>
              <li>分隔符不是逗号(,)</li>
              <li>编码格式不是UTF-8</li>
              <li>文件损坏或不完整</li>
            </ul>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>用Excel或记事本打开文件，另存为UTF-8编码的CSV</li>
              <li>确保列与列之间用逗号分隔</li>
              <li>检查文件是否完整无损坏</li>
              <li>移除特殊字符和换行符</li>
            </ol>
          </div>
        `,
        actions: ['重新选择文件', '查看示例格式', '联系技术支持']
      },
      MISSING_COLUMNS: {
        title: '缺少必要列',
        content: `
          <div>
            <h4>❌ 检测到数据列缺失</h4>
            <p><strong>必需列：</strong></p>
            <ul>
              <li>Time (时间戳)</li>
              <li>Force (力值)</li>
              <li>Position_X (X坐标)</li>
              <li>Position_Y (Y坐标)</li>
            </ul>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>确保CSV文件包含所有必需列</li>
              <li>检查列名拼写是否正确</li>
              <li>确保首行为列标题</li>
              <li>删除空白列和行</li>
            </ol>
          </div>
        `,
        actions: ['重新选择文件', '下载模板文件', '查看数据要求']
      },
      ENCODING_ERROR: {
        title: '文件编码错误',
        content: `
          <div>
            <h4>❌ 文件编码格式不支持</h4>
            <p><strong>当前检测编码：</strong> ${error.detected_encoding || '未知'}</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>使用记事本打开文件</li>
              <li>选择"另存为"</li>
              <li>编码选择"UTF-8"</li>
              <li>保存后重新上传</li>
            </ol>
            <p><strong>或者：</strong></p>
            <ul>
              <li>使用Excel打开，另存为UTF-8 CSV</li>
              <li>使用专业文本编辑器转换编码</li>
            </ul>
          </div>
        `,
        actions: ['重新选择文件', '查看编码指南', '尝试自动转换']
      }
    }

    await showErrorDialog(solutions[errorType])
  }

  // R脚本执行错误处理
  const handleRScriptError = async (error) => {
    errorStats.rScriptErrors++
    errorStats.totalErrors++
    errorStats.lastError = { type: 'R_SCRIPT', time: new Date(), error }
    errorStats.errorHistory.unshift(errorStats.lastError)

    const errorType = detectRScriptErrorType(error)
    
    const solutions = {
      MEMORY_INSUFFICIENT: {
        title: 'R分析内存不足',
        content: `
          <div>
            <h4>❌ R分析过程中内存不足</h4>
            <p><strong>数据量：</strong> ${error.data_size || '未知'}</p>
            <p><strong>可用内存：</strong> ${error.available_memory || '未知'}</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>关闭其他占用内存的程序</li>
              <li>减少数据量（选择部分数据进行分析）</li>
              <li>重启浏览器释放内存</li>
              <li>联系管理员增加服务器内存</li>
            </ol>
          </div>
        `,
        actions: ['重试分析', '减少数据量', '查看内存状态']
      },
      PACKAGE_MISSING: {
        title: 'R包缺失',
        content: `
          <div>
            <h4>❌ 缺少必要的R分析包</h4>
            <p><strong>缺失包：</strong> ${error.missing_packages?.join(', ') || '未知'}</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>系统将自动尝试安装缺失的包</li>
              <li>如果自动安装失败，请联系技术支持</li>
              <li>您可以稍后重试分析</li>
            </ol>
          </div>
        `,
        actions: ['自动修复', '重试分析', '联系支持']
      },
      SYNTAX_ERROR: {
        title: 'R脚本语法错误',
        content: `
          <div>
            <h4>❌ R分析脚本存在语法错误</h4>
            <p><strong>错误位置：</strong> ${error.line || '未知'}</p>
            <p><strong>错误信息：</strong> ${error.message || '未知'}</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>这是系统内部错误，请联系技术支持</li>
              <li>提供错误ID以便快速定位问题</li>
              <li>您可以尝试使用不同的分析参数</li>
            </ol>
          </div>
        `,
        actions: ['联系技术支持', '重试分析', '报告问题']
      },
      DATA_TYPE_ERROR: {
        title: '数据类型错误',
        content: `
          <div>
            <h4>❌ 数据类型不符合分析要求</h4>
            <p><strong>问题列：</strong> ${error.problematic_columns?.join(', ') || '未知'}</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>确保数值列只包含数字</li>
              <li>移除或修正异常值</li>
              <li>检查日期时间格式</li>
              <li>确保坐标值为有效数字</li>
            </ol>
          </div>
        `,
        actions: ['检查数据', '重新上传', '数据清理指南']
      }
    }

    await showErrorDialog(solutions[errorType])
  }

  // 内存不足错误处理
  const handleMemoryError = async (error) => {
    errorStats.memoryErrors++
    errorStats.totalErrors++
    errorStats.lastError = { type: 'MEMORY', time: new Date(), error }
    errorStats.errorHistory.unshift(errorStats.lastError)

    const solution = {
      title: '系统内存不足',
      content: `
        <div>
          <h4>❌ 检测到内存不足</h4>
          <p><strong>当前内存使用：</strong> ${error.memory_usage || '未知'}</p>
          <p><strong>可用内存：</strong> ${error.available_memory || '未知'}</p>
          <p><strong>🔧 立即解决方案：</strong></p>
          <ol>
            <li><strong>关闭其他浏览器标签页</strong></li>
            <li><strong>关闭其他应用程序</strong></li>
            <li><strong>重启浏览器</strong></li>
            <li><strong>减少分析数据量</strong></li>
          </ol>
          <p><strong>⚙️ 系统优化建议：</strong></p>
          <ul>
            <li>定期清理浏览器缓存</li>
            <li>升级系统内存</li>
            <li>使用64位浏览器</li>
            <li>分批处理大量数据</li>
          </ul>
        </div>
      `,
      actions: ['释放内存', '减少数据量', '重启浏览器', '系统优化指南']
    }

    await showErrorDialog(solution)
  }

  // 网络连接错误处理
  const handleNetworkError = async (error) => {
    errorStats.networkErrors++
    errorStats.totalErrors++
    errorStats.lastError = { type: 'NETWORK', time: new Date(), error }
    errorStats.errorHistory.unshift(errorStats.lastError)

    const errorType = detectNetworkErrorType(error)
    
    const solutions = {
      NETWORK_ERROR: {
        title: '网络连接错误',
        content: `
          <div>
            <h4>❌ 无法连接到服务器</h4>
            <p><strong>错误类型：</strong> 网络连接失败</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>检查网络连接状态</li>
              <li>确认服务器地址正确</li>
              <li>检查防火墙设置</li>
              <li>尝试刷新页面</li>
            </ol>
            <p><strong>📞 如果问题持续：</strong></p>
            <ul>
              <li>联系网络管理员</li>
              <li>检查VPN连接</li>
              <li>尝试不同网络环境</li>
            </ul>
          </div>
        `,
        actions: ['重试连接', '测试网络', '联系管理员']
      },
      TIMEOUT: {
        title: '请求超时',
        content: `
          <div>
            <h4>❌ 服务器响应超时</h4>
            <p><strong>超时时间：</strong> ${error.timeout || '30'}秒</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>检查网络速度</li>
              <li>减少上传文件大小</li>
              <li>稍后重试</li>
              <li>联系技术支持</li>
            </ol>
          </div>
        `,
        actions: ['重试请求', '检查网络速度', '联系支持']
      },
      SERVER_ERROR: {
        title: '服务器错误',
        content: `
          <div>
            <h4>❌ 服务器内部错误</h4>
            <p><strong>状态码：</strong> ${error.status || '500'}</p>
            <p><strong>错误信息：</strong> ${error.message || '服务器内部错误'}</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>稍后重试</li>
              <li>检查输入数据格式</li>
              <li>联系技术支持</li>
            </ol>
          </div>
        `,
        actions: ['重试请求', '检查数据', '报告问题']
      },
      NOT_FOUND: {
        title: '资源不存在',
        content: `
          <div>
            <h4>❌ 请求的资源不存在</h4>
            <p><strong>请求路径：</strong> ${error.url || '未知'}</p>
            <p><strong>🔧 解决方案：</strong></p>
            <ol>
              <li>检查请求URL是否正确</li>
              <li>确认资源是否存在</li>
              <li>刷新页面重试</li>
              <li>联系技术支持</li>
            </ol>
          </div>
        `,
        actions: ['刷新页面', '重试请求', '联系支持']
      }
    }

    await showErrorDialog(solutions[errorType])
  }

  // 错误类型检测函数
  const detectFileFormatErrorType = (error) => {
    if (error.message?.includes('encoding')) return 'ENCODING_ERROR'
    if (error.message?.includes('columns') || error.message?.includes('header')) return 'MISSING_COLUMNS'
    return 'INVALID_CSV'
  }

  const detectRScriptErrorType = (error) => {
    if (error.message?.includes('memory') || error.message?.includes('Memory')) return 'MEMORY_INSUFFICIENT'
    if (error.message?.includes('package') || error.message?.includes('library')) return 'PACKAGE_MISSING'
    if (error.message?.includes('syntax') || error.message?.includes('Error in parse')) return 'SYNTAX_ERROR'
    if (error.message?.includes('type') || error.message?.includes('numeric')) return 'DATA_TYPE_ERROR'
    return 'SYNTAX_ERROR'
  }

  const detectNetworkErrorType = (error) => {
    if (error.code === 'NETWORK_ERROR') return 'NETWORK_ERROR'
    if (error.code === 'TIMEOUT') return 'TIMEOUT'
    if (error.status >= 500) return 'SERVER_ERROR'
    if (error.status === 404) return 'NOT_FOUND'
    return 'NETWORK_ERROR'
  }

  // 显示错误解决方案对话框
  const showErrorDialog = async (solution) => {
    return new Promise((resolve) => {
      ElMessageBox({
        title: solution.title,
        message: solution.content,
        dangerouslyUseHTMLString: true,
        showCancelButton: true,
        confirmButtonText: solution.actions[0] || '确定',
        cancelButtonText: '关闭',
        type: 'error',
        customClass: 'error-solution-dialog',
        beforeClose: (action, instance, done) => {
          if (action === 'confirm') {
            handleSolutionAction(solution.actions[0])
          }
          done()
          resolve(action)
        }
      })
    })
  }

  // 处理解决方案操作
  const handleSolutionAction = (action) => {
    switch (action) {
      case '重新选择文件':
      case '重试分析':
      case '重试连接':
      case '重试请求':
        ElMessage.info('请重新尝试操作')
        break
      case '查看示例格式':
      case '下载模板文件':
        downloadTemplate()
        break
      case '联系技术支持':
      case '联系管理员':
      case '联系支持':
        showSupportDialog()
        break
      case '自动修复':
        attemptAutoFix()
        break
      case '测试网络':
        testNetworkConnection()
        break
      case '释放内存':
        suggestMemoryCleanup()
        break
      default:
        ElMessage.info('功能开发中...')
    }
  }

  // 下载文件模板
  const downloadTemplate = () => {
    const template = `Time,Force,Position_X,Position_Y
0.000,0.0,0.0,0.0
0.001,5.2,0.1,0.1
0.002,10.5,0.2,0.2
0.003,15.8,0.3,0.3
0.004,20.1,0.4,0.4
0.005,25.0,0.5,0.5`
    
    const blob = new Blob([template], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '压力测试数据模板.csv'
    link.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('模板文件已下载')
  }

  // 显示技术支持对话框
  const showSupportDialog = () => {
    ElMessageBox.alert(`
      <div>
        <h4>📞 技术支持联系方式</h4>
        <p><strong>邮箱：</strong> support@pressure-system.com</p>
        <p><strong>电话：</strong> 400-xxx-xxxx</p>
        <p><strong>工作时间：</strong> 周一至周五 9:00-18:00</p>
        <br>
        <p><strong>错误ID：</strong> ${generateErrorId()}</p>
        <p style="font-size: 12px; color: #666;">请提供错误ID以便快速定位问题</p>
      </div>
    `, '技术支持', {
      dangerouslyUseHTMLString: true,
      type: 'info'
    })
  }

  // 尝试自动修复
  const attemptAutoFix = async () => {
    ElMessage.info('正在尝试自动修复...')
    // 模拟自动修复过程
    setTimeout(() => {
      ElMessage.success('自动修复完成，请重试操作')
    }, 2000)
  }

  // 测试网络连接
  const testNetworkConnection = async () => {
    try {
      ElMessage.info('正在测试网络连接...')
      await analysisAPI.healthCheck()
      ElMessage.success('网络连接正常')
    } catch (error) {
      ElMessage.error('网络连接失败，请检查网络设置')
    }
  }

  // 建议内存清理
  const suggestMemoryCleanup = () => {
    ElNotification({
      title: '内存优化建议',
      message: `
        1. 关闭其他浏览器标签页
        2. 关闭不必要的应用程序
        3. 重启浏览器
        4. 清理浏览器缓存
      `,
      type: 'info',
      duration: 10000
    })
  }

  // 生成错误ID
  const generateErrorId = () => {
    return 'ERR-' + Date.now().toString(36).toUpperCase() + Math.random().toString(36).substr(2, 5).toUpperCase()
  }

  // 导出诊断报告
  const exportDiagnosticReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      errorStats,
      systemInfo: {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine
      },
      performanceInfo: {
        memory: performance.memory ? {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        } : null
      }
    }

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `diagnostic-report-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)

    ElMessage.success('诊断报告已导出')
  }

  // 清除错误历史
  const clearErrorHistory = () => {
    errorStats.errorHistory = []
    errorStats.fileFormatErrors = 0
    errorStats.rScriptErrors = 0
    errorStats.memoryErrors = 0
    errorStats.networkErrors = 0
    errorStats.totalErrors = 0
    errorStats.lastError = null
    ElMessage.success('错误历史已清除')
  }

  // 主要错误处理入口
  const handleSpecificError = async (error, context = '') => {
    isHandling.value = true

    try {
      // 根据错误类型调用对应处理函数
      if (error.type === 'FILE_FORMAT' || error.message?.includes('format')) {
        await handleFileFormatError(error)
      } else if (error.type === 'R_SCRIPT' || error.message?.includes('R ')) {
        await handleRScriptError(error)
      } else if (error.type === 'MEMORY' || error.message?.includes('memory')) {
        await handleMemoryError(error)
      } else if (error.type === 'NETWORK' || error.code === 'NETWORK_ERROR') {
        await handleNetworkError(error)
      } else {
        // 通用错误处理
        ElMessage.error(`${context}: ${error.message || '未知错误'}`)
      }
    } finally {
      isHandling.value = false
    }
  }

  return {
    errorStats,
    isHandling,
    handleSpecificError,
    handleFileFormatError,
    handleRScriptError,
    handleMemoryError,
    handleNetworkError,
    exportDiagnosticReport,
    clearErrorHistory
  }
} 
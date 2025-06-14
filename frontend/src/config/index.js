/**
 * 应用配置管理
 */

// 获取API基础URL
export const getApiBaseURL = () => {
  // 优先使用环境变量
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // 生产环境使用相对路径（通过nginx代理）
  if (import.meta.env.PROD) {
    return ''  // 使用相对路径，通过nginx代理到后端
  }
  
  // 开发环境使用localhost
  return 'http://localhost:8000'
}

// 获取完整的API URL
export const getFullApiURL = (path = '') => {
  const baseURL = getApiBaseURL()
  if (!baseURL) {
    return path // 相对路径
  }
  return `${baseURL}${path}`
}

// 应用配置
export const appConfig = {
  // 应用信息
  title: import.meta.env.VITE_APP_TITLE || '压力采集数据分析系统',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // API配置
  api: {
    baseURL: getApiBaseURL(),
    timeout: 30000,
  },
  
  // 开发配置
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  
  // 调试模式
  debug: import.meta.env.DEV || import.meta.env.VITE_DEBUG === 'true',
}

// 导出默认配置
export default appConfig 
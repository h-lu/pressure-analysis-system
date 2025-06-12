import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

// 路由懒加载函数
const lazyLoad = (view) => {
  return () => import(`@/views/${view}.vue`)
}

// 组件懒加载函数
const lazyLoadComponent = (component) => {
  return () => import(`@/components/${component}.vue`)
}

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/analysis',
    meta: {
      title: '压力系统首页',
      requiresAuth: false
    }
  },
  
  // 测试页面
  {
    path: '/test',
    name: 'Test',
    component: lazyLoad('TestPage'),
    meta: {
      title: '测试页面',
      requiresAuth: false
    }
  },
  
  // 数据分析模块
  {
    path: '/analysis',
    name: 'Analysis',
    component: lazyLoad('DataAnalysis'),
    meta: {
      title: '数据分析',
      icon: 'DataAnalysis',
      requiresAuth: false,
      keepAlive: true
    }
  },
  
  // 测试分析页面
  {
    path: '/analysis-test',
    name: 'AnalysisTest',
    component: lazyLoad('DataAnalysisTest'),
    meta: {
      title: '分析测试',
      requiresAuth: false,
      keepAlive: false
    }
  },
  
  // 任务管理模块
  {
    path: '/tasks',
    name: 'Tasks',
    component: lazyLoad('TaskManagement'),
    meta: {
      title: '任务管理',
      icon: 'List',
      requiresAuth: false,
      keepAlive: true
    }
  },
  
  // 任务详情和状态
  {
    path: '/task/:taskId',
    name: 'TaskStatus',
    component: lazyLoad('TaskStatus'),
    props: true,
    meta: {
      title: '任务状态',
      requiresAuth: false,
      keepAlive: false
    }
  },
  
  // 分析结果展示
  {
    path: '/results/:taskId',
    name: 'Results',
    component: lazyLoad('AnalysisResults'),
    props: true,
    meta: {
      title: '分析结果',
      requiresAuth: false,
      keepAlive: true
    }
  },
  
  // 文件管理
  {
    path: '/files',
    name: 'Files',
    component: lazyLoad('FileManagement'),
    meta: {
      title: '文件管理',
      icon: 'Document',
      requiresAuth: false,
      keepAlive: true
    }
  },
  
  // 历史记录
  {
    path: '/history',
    name: 'History',
    component: lazyLoad('History'),
    meta: {
      title: '历史记录',
      icon: 'Clock',
      requiresAuth: false,
      keepAlive: true
    }
  },
  
  // 系统设置
  {
    path: '/settings',
    name: 'Settings',
    component: lazyLoad('Settings'),
    meta: {
      title: '系统设置',
      icon: 'Setting',
      requiresAuth: false,
      keepAlive: false
    },
    children: [
      {
        path: 'theme',
        name: 'ThemeSettings',
        component: lazyLoadComponent('ThemeSettings'),
        meta: {
          title: '主题设置',
          requiresAuth: false
        }
      },
      {
        path: 'performance',
        name: 'PerformanceMonitor',
        component: lazyLoadComponent('PerformanceMonitor'),
        meta: {
          title: '性能监控',
          requiresAuth: false
        }
      },
      {
        path: 'ai',
        name: 'AISettings',
        component: lazyLoadComponent('AISettings'),
        meta: {
          title: 'AI设置',
          requiresAuth: false
        }
      }
    ]
  },
  
  // 图表展示 (独立路由用于全屏查看)
  {
    path: '/charts/:taskId',
    name: 'ChartsView',
    component: lazyLoad('ChartsView'),
    props: true,
    meta: {
      title: '图表查看',
      requiresAuth: false,
      keepAlive: false,
      fullscreen: true
    }
  },
  
  // 关于页面
  {
    path: '/about',
    name: 'About',
    component: lazyLoad('AboutView'),
    meta: {
      title: '关于系统',
      requiresAuth: false,
      keepAlive: false
    }
  },
  

  
  // 错误页面
  {
    path: '/error',
    name: 'Error',
    component: lazyLoad('NotFound'),
    meta: {
      title: '系统错误',
      requiresAuth: false,
      keepAlive: false
    }
  },
  
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: lazyLoad('NotFound'),
    meta: {
      title: '页面未找到',
      requiresAuth: false,
      keepAlive: false
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 路由切换时的滚动行为
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 显示加载指示器
  if (typeof window !== 'undefined' && window.showPageLoading) {
    window.showPageLoading()
  }
  
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 压力采集数据分析系统`
  }
  
  // 权限验证
  if (to.meta?.requiresAuth) {
    // 这里可以添加认证逻辑
    // const isAuthenticated = await checkAuth()
    // if (!isAuthenticated) {
    //   next('/login')
    //   return
    // }
  }
  
  // 记录路由访问
  console.log(`[Router] Navigating to: ${to.path}`)
  
  next()
})

// 全局后置钩子
router.afterEach((to, from, failure) => {
  // 隐藏加载指示器
  if (typeof window !== 'undefined' && window.hidePageLoading) {
    window.hidePageLoading()
  }
  
  // 处理路由错误
  if (failure) {
    console.error('[Router] Navigation failed:', failure)
    ElMessage.error('页面导航失败，请重试')
  }
  
  // 发送页面访问统计
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('config', 'GA_TRACKING_ID', {
      page_path: to.path,
      page_title: to.meta?.title
    })
  }
})

// 路由错误处理
router.onError((error) => {
  console.error('[Router] Error:', error)
  
  if (error.message.includes('Loading chunk')) {
    ElMessage.error('加载页面资源失败，请刷新页面重试')
    
    // 自动刷新页面
    setTimeout(() => {
      window.location.reload()
    }, 2000)
  } else {
    ElMessage.error('路由错误，请联系管理员')
  }
})

// 导出路由实例和相关函数
export default router

// 获取菜单路由 (用于侧边栏导航)
export const getMenuRoutes = () => {
  return routes.filter(route => 
    route.meta?.icon && 
    !route.meta?.hidden &&
    route.path !== '/' &&
    !route.path.includes(':')
  )
}

// 获取面包屑导航
export const getBreadcrumb = (route) => {
  const breadcrumb = []
  const matched = route.matched
  
  matched.forEach(match => {
    if (match.meta?.title) {
      breadcrumb.push({
        title: match.meta.title,
        path: match.path
      })
    }
  })
  
  return breadcrumb
}

// 预加载路由组件
export const preloadRoutes = (routeNames = []) => {
  const preloadPromises = []
  
  routes.forEach(route => {
    if (routeNames.length === 0 || routeNames.includes(route.name)) {
      if (typeof route.component === 'function') {
        preloadPromises.push(route.component())
      }
    }
  })
  
  return Promise.allSettled(preloadPromises)
}

// 路由工具函数
export const routeUtils = {
  // 检查当前路由是否匹配
  isCurrentRoute(routeName, currentRoute) {
    return currentRoute.name === routeName
  },
  
  // 检查是否为子路由
  isChildRoute(parentRoute, currentRoute) {
    return currentRoute.path.startsWith(parentRoute)
  },
  
  // 生成带参数的路由路径
  generatePath(routeName, params = {}) {
    const route = routes.find(r => r.name === routeName)
    if (!route) return '/'
    
    let path = route.path
    Object.entries(params).forEach(([key, value]) => {
      path = path.replace(`:${key}`, value)
    })
    
    return path
  },
  
  // 获取路由meta信息
  getRouteMeta(routeName) {
    const route = routes.find(r => r.name === routeName)
    return route?.meta || {}
  }
}

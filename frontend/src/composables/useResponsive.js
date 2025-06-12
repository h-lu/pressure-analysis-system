import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式断点定义
export const BREAKPOINTS = {
  xs: 480,
  sm: 768,
  md: 1024,
  lg: 1200,
  xl: 1920
}

// 屏幕尺寸管理
export function useScreenSize() {
  const width = ref(0)
  const height = ref(0)

  const updateSize = () => {
    width.value = window.innerWidth
    height.value = window.innerHeight
  }

  const currentBreakpoint = computed(() => {
    const w = width.value
    if (w < BREAKPOINTS.xs) return 'xs'
    if (w < BREAKPOINTS.sm) return 'sm'
    if (w < BREAKPOINTS.md) return 'md'
    if (w < BREAKPOINTS.lg) return 'lg'
    return 'xl'
  })

  const isMobile = computed(() => {
    return currentBreakpoint.value === 'xs'
  })

  const isTablet = computed(() => {
    return currentBreakpoint.value === 'sm'
  })

  const isDesktop = computed(() => {
    return ['md', 'lg', 'xl'].includes(currentBreakpoint.value)
  })

  const isSmallScreen = computed(() => {
    return ['xs', 'sm'].includes(currentBreakpoint.value)
  })

  onMounted(() => {
    updateSize()
    window.addEventListener('resize', updateSize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateSize)
  })

  return {
    width,
    height,
    currentBreakpoint,
    isMobile,
    isTablet,
    isDesktop,
    isSmallScreen
  }
}

// 触摸设备检测
export function useTouchDevice() {
  const isTouchDevice = ref(false)
  const hasHover = ref(true)
  const isStandalone = ref(false)

  const detectTouch = () => {
    // 检测触摸支持
    isTouchDevice.value = (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      navigator.msMaxTouchPoints > 0
    )

    // 检测悬停支持
    hasHover.value = window.matchMedia('(hover: hover)').matches

    // 检测PWA模式
    isStandalone.value = (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    )
  }

  onMounted(() => {
    detectTouch()
  })

  return {
    isTouchDevice,
    hasHover,
    isStandalone
  }
}

// 响应式网格配置
export function useResponsiveGrid() {
  const { currentBreakpoint } = useScreenSize()

  const gridConfig = computed(() => {
    switch (currentBreakpoint.value) {
      case 'xs':
        return {
          columns: 1,
          gap: 8,
          cardSize: 'small',
          showSidebar: false,
          compactMode: true
        }
      case 'sm':
        return {
          columns: 2,
          gap: 12,
          cardSize: 'small',
          showSidebar: false,
          compactMode: true
        }
      case 'md':
        return {
          columns: 3,
          gap: 16,
          cardSize: 'default',
          showSidebar: true,
          compactMode: false
        }
      case 'lg':
        return {
          columns: 4,
          gap: 20,
          cardSize: 'default',
          showSidebar: true,
          compactMode: false
        }
      default: // xl
        return {
          columns: 5,
          gap: 24,
          cardSize: 'large',
          showSidebar: true,
          compactMode: false
        }
    }
  })

  const getTableConfig = () => {
    const { isSmallScreen } = useScreenSize()
    
    return {
      size: isSmallScreen.value ? 'small' : 'default',
      showPagination: !isSmallScreen.value,
      maxHeight: isSmallScreen.value ? 300 : 500,
      stripe: true,
      border: !isSmallScreen.value
    }
  }

  const getDialogConfig = () => {
    const { isSmallScreen, width } = useScreenSize()
    
    return {
      width: isSmallScreen.value ? '95%' : '80%',
      fullscreen: isSmallScreen.value && width.value < 600,
      center: true,
      modal: true,
      lockScroll: true
    }
  }

  return {
    gridConfig,
    getTableConfig,
    getDialogConfig
  }
}

// 响应式布局管理
export function useResponsiveLayout() {
  const { isSmallScreen, isMobile } = useScreenSize()
  const sidebarCollapsed = ref(false)
  const drawerVisible = ref(false)

  // 自动响应式侧边栏
  const autoCollapseSidebar = computed(() => {
    return isSmallScreen.value || sidebarCollapsed.value
  })

  // 移动端抽屉模式
  const useMobileDrawer = computed(() => {
    return isMobile.value
  })

  const toggleSidebar = () => {
    if (isMobile.value) {
      drawerVisible.value = !drawerVisible.value
    } else {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }
  }

  const closeSidebar = () => {
    if (isMobile.value) {
      drawerVisible.value = false
    } else {
      sidebarCollapsed.value = true
    }
  }

  const openSidebar = () => {
    if (isMobile.value) {
      drawerVisible.value = true
    } else {
      sidebarCollapsed.value = false
    }
  }

  // 监听路由变化，在移动端自动关闭侧边栏
  const handleRouteChange = () => {
    if (isMobile.value) {
      drawerVisible.value = false
    }
  }

  return {
    sidebarCollapsed,
    drawerVisible,
    autoCollapseSidebar,
    useMobileDrawer,
    toggleSidebar,
    closeSidebar,
    openSidebar,
    handleRouteChange
  }
}

// 响应式字体和间距
export function useResponsiveSpacing() {
  const { currentBreakpoint } = useScreenSize()

  const spacing = computed(() => {
    switch (currentBreakpoint.value) {
      case 'xs':
        return {
          page: '8px',
          section: '12px',
          card: '8px',
          item: '4px'
        }
      case 'sm':
        return {
          page: '12px',
          section: '16px',
          card: '12px',
          item: '6px'
        }
      case 'md':
        return {
          page: '16px',
          section: '20px',
          card: '16px',
          item: '8px'
        }
      case 'lg':
        return {
          page: '20px',
          section: '24px',
          card: '20px',
          item: '10px'
        }
      default: // xl
        return {
          page: '24px',
          section: '32px',
          card: '24px',
          item: '12px'
        }
    }
  })

  const fontSize = computed(() => {
    switch (currentBreakpoint.value) {
      case 'xs':
        return {
          title: '18px',
          subtitle: '14px',
          body: '12px',
          caption: '10px'
        }
      case 'sm':
        return {
          title: '20px',
          subtitle: '16px',
          body: '14px',
          caption: '12px'
        }
      default:
        return {
          title: '24px',
          subtitle: '18px',
          body: '16px',
          caption: '14px'
        }
    }
  })

  return {
    spacing,
    fontSize
  }
}

// 响应式手势支持
export function useGestureSupport() {
  const { isTouchDevice } = useTouchDevice()

  const enableSwipeGestures = (element, callbacks = {}) => {
    if (!isTouchDevice.value || !element) return

    let startX = 0
    let startY = 0
    let startTime = 0

    const handleTouchStart = (e) => {
      const touch = e.touches[0]
      startX = touch.clientX
      startY = touch.clientY
      startTime = Date.now()
    }

    const handleTouchEnd = (e) => {
      const touch = e.changedTouches[0]
      const endX = touch.clientX
      const endY = touch.clientY
      const endTime = Date.now()

      const deltaX = endX - startX
      const deltaY = endY - startY
      const deltaTime = endTime - startTime

      // 滑动距离和时间阈值
      const minDistance = 50
      const maxTime = 500

      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minDistance && deltaTime < maxTime) {
        if (deltaX > 0 && callbacks.onSwipeRight) {
          callbacks.onSwipeRight()
        } else if (deltaX < 0 && callbacks.onSwipeLeft) {
          callbacks.onSwipeLeft()
        }
      } else if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > minDistance && deltaTime < maxTime) {
        if (deltaY > 0 && callbacks.onSwipeDown) {
          callbacks.onSwipeDown()
        } else if (deltaY < 0 && callbacks.onSwipeUp) {
          callbacks.onSwipeUp()
        }
      }
    }

    element.addEventListener('touchstart', handleTouchStart, { passive: true })
    element.addEventListener('touchend', handleTouchEnd, { passive: true })

    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchend', handleTouchEnd)
    }
  }

  const enablePinchZoom = (element, callback) => {
    if (!isTouchDevice.value || !element) return

    let initialDistance = 0
    let initialScale = 1

    const getDistance = (touches) => {
      const dx = touches[0].clientX - touches[1].clientX
      const dy = touches[0].clientY - touches[1].clientY
      return Math.sqrt(dx * dx + dy * dy)
    }

    const handleTouchStart = (e) => {
      if (e.touches.length === 2) {
        initialDistance = getDistance(e.touches)
        initialScale = 1
      }
    }

    const handleTouchMove = (e) => {
      if (e.touches.length === 2) {
        e.preventDefault()
        const currentDistance = getDistance(e.touches)
        const scale = currentDistance / initialDistance
        
        if (callback) {
          callback(scale * initialScale)
        }
      }
    }

    element.addEventListener('touchstart', handleTouchStart, { passive: true })
    element.addEventListener('touchmove', handleTouchMove, { passive: false })

    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchmove', handleTouchMove)
    }
  }

  return {
    enableSwipeGestures,
    enablePinchZoom
  }
}

// 响应式工具函数
export function useResponsiveUtils() {
  const { isMobile, isTablet, isSmallScreen } = useScreenSize()

  const optimizeForTouch = (config = {}) => {
    if (isMobile.value) {
      return {
        ...config,
        size: 'large',
        touchFriendly: true,
        minHeight: '44px',
        padding: '12px',
        margin: '8px'
      }
    }
    return config
  }

  const getOptimalColumns = (totalItems, maxColumns = 5) => {
    if (isMobile.value) return 1
    if (isTablet.value) return Math.min(2, Math.ceil(totalItems / 3))
    return Math.min(maxColumns, Math.ceil(Math.sqrt(totalItems)))
  }

  const shouldShowCompactUI = () => {
    return isSmallScreen.value
  }

  const getAdaptivePageSize = (defaultSize = 20) => {
    if (isMobile.value) return Math.ceil(defaultSize / 2)
    if (isTablet.value) return Math.ceil(defaultSize * 0.75)
    return defaultSize
  }

  return {
    optimizeForTouch,
    getOptimalColumns,
    shouldShowCompactUI,
    getAdaptivePageSize
  }
} 
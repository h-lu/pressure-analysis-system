import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

// 预定义主题
export const THEMES = {
  light: {
    name: 'light',
    label: '浅色主题',
    colors: {
      primary: '#409EFF',
      success: '#67C23A',
      warning: '#E6A23C',
      danger: '#F56C6C',
      info: '#909399',
      background: '#FFFFFF',
      backgroundPage: '#F5F7FA',
      text: '#303133',
      textRegular: '#606266',
      textSecondary: '#909399',
      border: '#DCDFE6',
      borderLight: '#E4E7ED'
    }
  },
  dark: {
    name: 'dark',
    label: '深色主题',
    colors: {
      primary: '#409EFF',
      success: '#67C23A',
      warning: '#E6A23C',
      danger: '#F56C6C',
      info: '#909399',
      background: '#1D1E1F',
      backgroundPage: '#141414',
      text: '#E5EAF3',
      textRegular: '#CFD3DC',
      textSecondary: '#A3A6AD',
      border: '#4C4D4F',
      borderLight: '#414243'
    }
  },
  blue: {
    name: 'blue',
    label: '蓝色主题',
    colors: {
      primary: '#1890FF',
      success: '#52C41A',
      warning: '#FAAD14',
      danger: '#FF4D4F',
      info: '#8C8C8C',
      background: '#F0F2F5',
      backgroundPage: '#FAFAFA',
      text: '#000000',
      textRegular: '#262626',
      textSecondary: '#8C8C8C',
      border: '#D9D9D9',
      borderLight: '#F0F0F0'
    }
  },
  green: {
    name: 'green',
    label: '绿色主题',
    colors: {
      primary: '#52C41A',
      success: '#389E0D',
      warning: '#FAAD14',
      danger: '#FF4D4F',
      info: '#8C8C8C',
      background: '#F6FFED',
      backgroundPage: '#FCFFE6',
      text: '#000000',
      textRegular: '#262626',
      textSecondary: '#8C8C8C',
      border: '#B7EB8F',
      borderLight: '#D9F7BE'
    }
  }
}

// 字体大小配置
export const FONT_SIZES = {
  small: {
    name: 'small',
    label: '小字体',
    scale: 0.875,
    sizes: {
      base: '12px',
      small: '10px',
      large: '14px',
      extraLarge: '16px'
    }
  },
  medium: {
    name: 'medium',
    label: '标准字体',
    scale: 1,
    sizes: {
      base: '14px',
      small: '12px',
      large: '16px',
      extraLarge: '18px'
    }
  },
  large: {
    name: 'large',
    label: '大字体',
    scale: 1.125,
    sizes: {
      base: '16px',
      small: '14px',
      large: '18px',
      extraLarge: '20px'
    }
  },
  extraLarge: {
    name: 'extraLarge',
    label: '超大字体',
    scale: 1.25,
    sizes: {
      base: '18px',
      small: '16px',
      large: '20px',
      extraLarge: '24px'
    }
  }
}

// 布局配置
export const LAYOUT_CONFIGS = {
  compact: {
    name: 'compact',
    label: '紧凑布局',
    spacing: {
      small: '4px',
      medium: '8px',
      large: '12px',
      extraLarge: '16px'
    },
    componentSize: 'small',
    cardPadding: '12px',
    sidebarWidth: '200px'
  },
  comfortable: {
    name: 'comfortable',
    label: '舒适布局',
    spacing: {
      small: '8px',
      medium: '16px',
      large: '24px',
      extraLarge: '32px'
    },
    componentSize: 'default',
    cardPadding: '20px',
    sidebarWidth: '240px'
  },
  spacious: {
    name: 'spacious',
    label: '宽松布局',
    spacing: {
      small: '12px',
      medium: '24px',
      large: '36px',
      extraLarge: '48px'
    },
    componentSize: 'large',
    cardPadding: '32px',
    sidebarWidth: '280px'
  }
}

// 主题管理
export function useTheme() {
  const currentTheme = ref('light')
  const currentFontSize = ref('medium')
  const currentLayout = ref('comfortable')
  const customColors = ref({})

  // 计算当前主题配置
  const themeConfig = computed(() => {
    const baseTheme = THEMES[currentTheme.value]
    return {
      ...baseTheme,
      colors: {
        ...baseTheme.colors,
        ...customColors.value
      }
    }
  })

  // 计算字体配置
  const fontConfig = computed(() => {
    return FONT_SIZES[currentFontSize.value]
  })

  // 计算布局配置
  const layoutConfig = computed(() => {
    return LAYOUT_CONFIGS[currentLayout.value]
  })

  // 获取CSS变量
  const cssVariables = computed(() => {
    const theme = themeConfig.value
    const font = fontConfig.value
    const layout = layoutConfig.value

    return {
      // 颜色变量
      '--el-color-primary': theme.colors.primary,
      '--el-color-success': theme.colors.success,
      '--el-color-warning': theme.colors.warning,
      '--el-color-danger': theme.colors.danger,
      '--el-color-info': theme.colors.info,
      '--el-bg-color': theme.colors.background,
      '--el-bg-color-page': theme.colors.backgroundPage,
      '--el-text-color-primary': theme.colors.text,
      '--el-text-color-regular': theme.colors.textRegular,
      '--el-text-color-secondary': theme.colors.textSecondary,
      '--el-border-color': theme.colors.border,
      '--el-border-color-light': theme.colors.borderLight,

      // 字体变量
      '--el-font-size-base': font.sizes.base,
      '--el-font-size-small': font.sizes.small,
      '--el-font-size-large': font.sizes.large,
      '--el-font-size-extra-large': font.sizes.extraLarge,
      '--font-scale': font.scale,

      // 布局变量
      '--spacing-small': layout.spacing.small,
      '--spacing-medium': layout.spacing.medium,
      '--spacing-large': layout.spacing.large,
      '--spacing-extra-large': layout.spacing.extraLarge,
      '--card-padding': layout.cardPadding,
      '--sidebar-width': layout.sidebarWidth
    }
  })

  // 应用CSS变量到根元素
  const applyCSSVariables = () => {
    const root = document.documentElement
    const variables = cssVariables.value

    Object.entries(variables).forEach(([key, value]) => {
      root.style.setProperty(key, value)
    })
  }

  // 切换主题
  const setTheme = (themeName) => {
    if (THEMES[themeName]) {
      currentTheme.value = themeName
      localStorage.setItem('app-theme', themeName)
      ElMessage.success(`已切换到${THEMES[themeName].label}`)
    }
  }

  // 切换字体大小
  const setFontSize = (size) => {
    if (FONT_SIZES[size]) {
      currentFontSize.value = size
      localStorage.setItem('app-font-size', size)
      ElMessage.success(`已切换到${FONT_SIZES[size].label}`)
    }
  }

  // 切换布局
  const setLayout = (layout) => {
    if (LAYOUT_CONFIGS[layout]) {
      currentLayout.value = layout
      localStorage.setItem('app-layout', layout)
      ElMessage.success(`已切换到${LAYOUT_CONFIGS[layout].label}`)
    }
  }

  // 自定义颜色
  const setCustomColor = (colorKey, colorValue) => {
    customColors.value[colorKey] = colorValue
    localStorage.setItem('app-custom-colors', JSON.stringify(customColors.value))
  }

  // 重置自定义颜色
  const resetCustomColors = () => {
    customColors.value = {}
    localStorage.removeItem('app-custom-colors')
    ElMessage.success('已重置自定义颜色')
  }

  // 获取对比色（用于自动调整文字颜色）
  const getContrastColor = (backgroundColor) => {
    // 简单的对比度计算
    const hex = backgroundColor.replace('#', '')
    const r = parseInt(hex.substr(0, 2), 16)
    const g = parseInt(hex.substr(2, 2), 16)
    const b = parseInt(hex.substr(4, 2), 16)
    const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000
    return brightness > 155 ? '#000000' : '#FFFFFF'
  }

  // 导出主题配置
  const exportTheme = () => {
    const config = {
      theme: currentTheme.value,
      fontSize: currentFontSize.value,
      layout: currentLayout.value,
      customColors: customColors.value
    }
    
    const blob = new Blob([JSON.stringify(config, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'theme-config.json'
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('主题配置已导出')
  }

  // 导入主题配置
  const importTheme = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        try {
          const config = JSON.parse(e.target.result)
          
          if (config.theme && THEMES[config.theme]) {
            setTheme(config.theme)
          }
          
          if (config.fontSize && FONT_SIZES[config.fontSize]) {
            setFontSize(config.fontSize)
          }
          
          if (config.layout && LAYOUT_CONFIGS[config.layout]) {
            setLayout(config.layout)
          }
          
          if (config.customColors) {
            customColors.value = config.customColors
            localStorage.setItem('app-custom-colors', JSON.stringify(config.customColors))
          }
          
          ElMessage.success('主题配置已导入')
          resolve(config)
        } catch (error) {
          ElMessage.error('主题配置文件格式错误')
          reject(error)
        }
      }
      
      reader.onerror = () => {
        ElMessage.error('读取主题配置文件失败')
        reject(new Error('File read error'))
      }
      
      reader.readAsText(file)
    })
  }

  // 创建主题预览
  const generateThemePreview = (themeName) => {
    const theme = THEMES[themeName]
    if (!theme) return null

    return {
      name: theme.name,
      label: theme.label,
      preview: {
        primary: theme.colors.primary,
        background: theme.colors.background,
        text: theme.colors.text,
        border: theme.colors.border
      }
    }
  }

  // 系统主题检测
  const detectSystemTheme = () => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
    return 'light'
  }

  // 自动跟随系统主题
  const followSystemTheme = ref(false)

  const setupSystemThemeListener = () => {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      
      const handleChange = (e) => {
        if (followSystemTheme.value) {
          setTheme(e.matches ? 'dark' : 'light')
        }
      }
      
      mediaQuery.addEventListener('change', handleChange)
      
      return () => {
        mediaQuery.removeEventListener('change', handleChange)
      }
    }
  }

  // 初始化主题
  const initTheme = () => {
    // 从本地存储加载设置
    const savedTheme = localStorage.getItem('app-theme')
    const savedFontSize = localStorage.getItem('app-font-size')
    const savedLayout = localStorage.getItem('app-layout')
    const savedCustomColors = localStorage.getItem('app-custom-colors')
    const savedFollowSystem = localStorage.getItem('app-follow-system-theme')

    if (savedTheme && THEMES[savedTheme]) {
      currentTheme.value = savedTheme
    } else {
      // 检测系统主题偏好
      currentTheme.value = detectSystemTheme()
    }

    if (savedFontSize && FONT_SIZES[savedFontSize]) {
      currentFontSize.value = savedFontSize
    }

    if (savedLayout && LAYOUT_CONFIGS[savedLayout]) {
      currentLayout.value = savedLayout
    }

    if (savedCustomColors) {
      try {
        customColors.value = JSON.parse(savedCustomColors)
      } catch (error) {
        console.warn('解析自定义颜色配置失败:', error)
      }
    }

    if (savedFollowSystem === 'true') {
      followSystemTheme.value = true
      setupSystemThemeListener()
    }
  }

  // 监听配置变化，自动应用CSS变量
  watch(cssVariables, () => {
    nextTick(() => {
      applyCSSVariables()
    })
  }, { immediate: true })

  // 组件挂载时初始化
  onMounted(() => {
    initTheme()
  })

  return {
    // 状态
    currentTheme,
    currentFontSize,
    currentLayout,
    customColors,
    followSystemTheme,
    
    // 计算属性
    themeConfig,
    fontConfig,
    layoutConfig,
    cssVariables,
    
    // 方法
    setTheme,
    setFontSize,
    setLayout,
    setCustomColor,
    resetCustomColors,
    getContrastColor,
    exportTheme,
    importTheme,
    generateThemePreview,
    detectSystemTheme,
    setupSystemThemeListener,
    initTheme,
    
    // 常量
    THEMES,
    FONT_SIZES,
    LAYOUT_CONFIGS
  }
}

// 主题工具函数
export function useThemeUtils() {
  // 颜色工具
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }

  const rgbToHex = (r, g, b) => {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
  }

  const lightenColor = (color, amount) => {
    const rgb = hexToRgb(color)
    if (!rgb) return color

    const r = Math.min(255, Math.floor(rgb.r + (255 - rgb.r) * amount))
    const g = Math.min(255, Math.floor(rgb.g + (255 - rgb.g) * amount))
    const b = Math.min(255, Math.floor(rgb.b + (255 - rgb.b) * amount))

    return rgbToHex(r, g, b)
  }

  const darkenColor = (color, amount) => {
    const rgb = hexToRgb(color)
    if (!rgb) return color

    const r = Math.max(0, Math.floor(rgb.r * (1 - amount)))
    const g = Math.max(0, Math.floor(rgb.g * (1 - amount)))
    const b = Math.max(0, Math.floor(rgb.b * (1 - amount)))

    return rgbToHex(r, g, b)
  }

  // 生成颜色调色板
  const generateColorPalette = (baseColor) => {
    return {
      'light-9': lightenColor(baseColor, 0.9),
      'light-8': lightenColor(baseColor, 0.8),
      'light-7': lightenColor(baseColor, 0.7),
      'light-6': lightenColor(baseColor, 0.6),
      'light-5': lightenColor(baseColor, 0.5),
      'light-4': lightenColor(baseColor, 0.4),
      'light-3': lightenColor(baseColor, 0.3),
      'light-2': lightenColor(baseColor, 0.2),
      'light-1': lightenColor(baseColor, 0.1),
      'default': baseColor,
      'dark-1': darkenColor(baseColor, 0.1),
      'dark-2': darkenColor(baseColor, 0.2)
    }
  }

  return {
    hexToRgb,
    rgbToHex,
    lightenColor,
    darkenColor,
    generateColorPalette
  }
} 
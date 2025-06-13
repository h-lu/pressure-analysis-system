<template>
  <div class="theme-settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon><Palette /></el-icon>
          <span>主题设置</span>
        </div>
      </template>

      <!-- 主题选择 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Monitor /></el-icon>
          <span>主题色彩</span>
        </div>
        
        <div class="theme-grid">
          <div
            v-for="(theme, key) in THEMES"
            :key="key"
            class="theme-option"
            :class="{ 'active': currentTheme === key }"
            @click="setTheme(key)"
          >
            <div class="theme-preview">
              <div 
                class="preview-color primary"
                :style="{ backgroundColor: theme.colors.primary }"
              ></div>
              <div 
                class="preview-color background"
                :style="{ backgroundColor: theme.colors.background }"
              ></div>
              <div 
                class="preview-color text"
                :style="{ 
                  backgroundColor: theme.colors.text,
                  opacity: 0.8
                }"
              ></div>
            </div>
            <span class="theme-label">{{ theme.label }}</span>
            <el-icon v-if="currentTheme === key" class="check-icon">
              <Check />
            </el-icon>
          </div>
        </div>

        <!-- 系统主题跟随 -->
        <div class="system-theme">
          <el-switch
            v-model="followSystemTheme"
            @change="handleSystemThemeChange"
          />
          <span class="switch-label">跟随系统主题</span>
        </div>
      </div>

      <!-- 字体大小 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><EditPen /></el-icon>
          <span>字体大小</span>
        </div>
        
        <div class="font-options">
          <el-radio-group 
            v-model="currentFontSize" 
            @change="setFontSize"
            class="font-radio-group"
          >
            <el-radio
              v-for="(font, key) in FONT_SIZES"
              :key="key"
              :value="key"
              class="font-radio"
            >
              <div class="font-option">
                <span class="font-label">{{ font.label }}</span>
                <span 
                  class="font-preview"
                  :style="{ fontSize: font.sizes.base }"
                >
                  示例文字 Aa
                </span>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
      </div>

      <!-- 布局配置 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Grid /></el-icon>
          <span>界面布局</span>
        </div>
        
        <div class="layout-options">
          <el-radio-group 
            v-model="currentLayout" 
            @change="setLayout"
            class="layout-radio-group"
          >
            <el-radio
              v-for="(layout, key) in LAYOUT_CONFIGS"
              :key="key"
              :value="key"
              class="layout-radio"
            >
              <div class="layout-option">
                <span class="layout-label">{{ layout.label }}</span>
                <div class="layout-preview">
                  <div 
                    class="preview-spacing"
                    :style="{ 
                      gap: layout.spacing.small,
                      padding: layout.spacing.medium 
                    }"
                  >
                    <div class="preview-block"></div>
                    <div class="preview-block"></div>
                    <div class="preview-block"></div>
                  </div>
                </div>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
      </div>

      <!-- 自定义颜色 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Brush /></el-icon>
          <span>自定义颜色</span>
        </div>
        
        <div class="custom-colors">
          <div class="color-row">
            <label class="color-label">主色调</label>
            <el-color-picker
              v-model="customPrimary"
              @change="handleCustomColorChange('primary', $event)"
              show-alpha
              :predefine="predefineColors"
            />
          </div>
          
          <div class="color-row">
            <label class="color-label">成功色</label>
            <el-color-picker
              v-model="customSuccess"
              @change="handleCustomColorChange('success', $event)"
              show-alpha
              :predefine="predefineColors"
            />
          </div>
          
          <div class="color-row">
            <label class="color-label">警告色</label>
            <el-color-picker
              v-model="customWarning"
              @change="handleCustomColorChange('warning', $event)"
              show-alpha
              :predefine="predefineColors"
            />
          </div>
          
          <div class="color-row">
            <label class="color-label">危险色</label>
            <el-color-picker
              v-model="customDanger"
              @change="handleCustomColorChange('danger', $event)"
              show-alpha
              :predefine="predefineColors"
            />
          </div>
        </div>

        <div class="custom-actions">
          <el-button @click="resetCustomColors" size="small">
            重置颜色
          </el-button>
          <el-button @click="generateColorPalette" size="small" type="primary">
            生成调色板
          </el-button>
        </div>
      </div>

      <!-- 主题操作 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><Operation /></el-icon>
          <span>主题管理</span>
        </div>
        
        <div class="theme-actions">
          <el-button @click="exportTheme" size="small">
            <el-icon><Download /></el-icon>
            导出主题
          </el-button>
          
          <el-upload
            :auto-upload="false"
            :on-change="handleImportTheme"
            :show-file-list="false"
            accept=".json"
          >
            <el-button size="small">
              <el-icon><Upload /></el-icon>
              导入主题
            </el-button>
          </el-upload>
          
          <el-button @click="resetToDefault" size="small" type="warning">
            <el-icon><RefreshLeft /></el-icon>
            恢复默认
          </el-button>
        </div>
      </div>

      <!-- 预览区域 -->
      <div class="setting-section">
        <div class="section-title">
          <el-icon><View /></el-icon>
          <span>效果预览</span>
        </div>
        
        <div class="theme-preview-area">
          <div class="preview-content">
            <div class="preview-header">
              <h3>预览标题</h3>
              <el-button type="primary" size="small">主按钮</el-button>
            </div>
            
            <div class="preview-body">
              <p>这是一段普通文本，用来预览当前主题的文字效果。</p>
              
              <div class="preview-components">
                <el-button type="success" size="small">成功</el-button>
                <el-button type="warning" size="small">警告</el-button>
                <el-button type="danger" size="small">危险</el-button>
                <el-button type="info" size="small">信息</el-button>
              </div>
              
              <div class="preview-card">
                <el-card>
                  <p>这是一个卡片组件的预览效果</p>
                </el-card>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  useTheme, 
  useThemeUtils, 
  THEMES, 
  FONT_SIZES, 
  LAYOUT_CONFIGS 
} from '@/composables/useTheme'

const {
  currentTheme,
  currentFontSize,
  currentLayout,
  customColors,
  followSystemTheme,
  setTheme,
  setFontSize,
  setLayout,
  setCustomColor,
  resetCustomColors,
  exportTheme,
  importTheme,
  setupSystemThemeListener
} = useTheme()

const { generateColorPalette } = useThemeUtils()

// 自定义颜色
const customPrimary = ref('')
const customSuccess = ref('')
const customWarning = ref('')
const customDanger = ref('')

// 预定义颜色
const predefineColors = ref([
  '#ff4500',
  '#ff8c00',
  '#ffd700',
  '#90ee90',
  '#00ced1',
  '#1e90ff',
  '#c71585'
])

// 监听自定义颜色变化
watch(customColors, (newColors) => {
  customPrimary.value = newColors.primary || ''
  customSuccess.value = newColors.success || ''
  customWarning.value = newColors.warning || ''
  customDanger.value = newColors.danger || ''
}, { immediate: true })

// 处理自定义颜色变化
const handleCustomColorChange = (colorKey, colorValue) => {
  if (colorValue) {
    setCustomColor(colorKey, colorValue)
  }
}

// 处理系统主题跟随
const handleSystemThemeChange = (value) => {
  localStorage.setItem('app-follow-system-theme', value.toString())
  if (value) {
    setupSystemThemeListener()
    ElMessage.success('已开启系统主题跟随')
  } else {
    ElMessage.info('已关闭系统主题跟随')
  }
}

// 生成调色板功能已通过 useThemeUtils() 提供

// 导入主题
const handleImportTheme = async (file) => {
  try {
    await importTheme(file.raw)
  } catch (error) {
    console.error('导入主题失败:', error)
  }
}

// 恢复默认设置
const resetToDefault = () => {
  setTheme('light')
  setFontSize('medium')
  setLayout('comfortable')
  resetCustomColors()
  followSystemTheme.value = false
  localStorage.setItem('app-follow-system-theme', 'false')
  ElMessage.success('已恢复默认设置')
}
</script>

<style scoped>
.theme-settings {
  max-width: 800px;
  margin: 0 auto;
}

.settings-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.setting-section {
  margin-bottom: 32px;
}

.setting-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
}

/* 主题选择 */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.theme-option {
  position: relative;
  cursor: pointer;
  border: 2px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s;
  text-align: center;
}

.theme-option:hover {
  border-color: var(--el-color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.theme-option.active {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.theme-preview {
  display: flex;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.preview-color {
  flex: 1;
}

.theme-label {
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  color: var(--el-color-primary);
  font-size: 16px;
}

.system-theme {
  display: flex;
  align-items: center;
  gap: 8px;
}

.switch-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

/* 字体选择 */
.font-radio-group {
  width: 100%;
}

.font-radio {
  width: 100%;
  margin-bottom: 12px;
}

.font-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  transition: all 0.3s;
}

.font-option:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.font-label {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.font-preview {
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

/* 布局选择 */
.layout-radio-group {
  width: 100%;
}

.layout-radio {
  width: 100%;
  margin-bottom: 12px;
}

.layout-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  transition: all 0.3s;
}

.layout-option:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.layout-label {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.layout-preview {
  width: 60px;
}

.preview-spacing {
  display: flex;
  align-items: center;
}

.preview-block {
  width: 12px;
  height: 12px;
  background-color: var(--el-color-primary);
  border-radius: 2px;
}

/* 自定义颜色 */
.custom-colors {
  margin-bottom: 16px;
}

.color-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.color-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.custom-actions {
  display: flex;
  gap: 12px;
}

/* 主题操作 */
.theme-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 预览区域 */
.theme-preview-area {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
}

.preview-content {
  background-color: var(--el-bg-color);
  border-radius: 6px;
  padding: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.preview-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.preview-body p {
  margin-bottom: 16px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.preview-components {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.preview-card {
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .theme-actions {
    flex-direction: column;
  }
  
  .theme-actions .el-button {
    width: 100%;
  }
  
  .color-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .custom-actions {
    flex-direction: column;
  }
  
  .custom-actions .el-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .theme-grid {
    grid-template-columns: 1fr;
  }
  
  .preview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .preview-components {
    flex-direction: column;
  }
  
  .preview-components .el-button {
    width: 100%;
  }
}
</style> 
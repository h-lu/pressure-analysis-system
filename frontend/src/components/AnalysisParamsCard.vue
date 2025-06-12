<template>
  <el-card shadow="hover" class="params-card">
    <template #header>
      <div class="card-header">
        <el-icon><Setting /></el-icon>
        <span>分析参数</span>
        <div class="header-actions">
          <el-tooltip content="参数说明" placement="top">
            <el-button size="small" @click="showHelp = !showHelp" :type="showHelp ? 'primary' : 'text'">
              <el-icon><QuestionFilled /></el-icon>
            </el-button>
          </el-tooltip>
          <el-dropdown @command="handleTemplateSelect">
            <el-button size="small" type="text">
              <el-icon><Collection /></el-icon>
              模板
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="default">默认参数</el-dropdown-item>
                <el-dropdown-item command="precision">高精度模式</el-dropdown-item>
                <el-dropdown-item command="tolerance">高容差模式</el-dropdown-item>
                <el-dropdown-item divided command="light">轻载测试</el-dropdown-item>
                <el-dropdown-item command="medium">中载测试</el-dropdown-item>
                <el-dropdown-item command="heavy">重载测试</el-dropdown-item>
                <el-dropdown-item divided command="save">保存当前</el-dropdown-item>
                <el-dropdown-item command="history">历史参数</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </template>

    <!-- 参数说明 -->
    <el-alert
      v-if="showHelp"
      title="参数说明"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 16px;"
    >
      <div class="help-content">
        <h4>参数详细说明:</h4>
        <ul>
          <li><strong>目标力值 (N)</strong>: 需要检测的压力值，支持多个值，用逗号分隔。例如: 5, 25, 50</li>
          <li><strong>绝对容差 (N)</strong>: 允许的绝对偏差值，单位为牛顿。推荐范围: 0.1 ~ 2.0</li>
          <li><strong>百分比容差 (%)</strong>: 允许的相对偏差百分比。推荐范围: 1% ~ 10%</li>
          <li><strong>分析精度</strong>: 影响分析算法的精确度和计算时间</li>
          <li><strong>异常值检测</strong>: 是否启用统计异常值自动识别</li>
          <li><strong>置信度水平</strong>: 统计分析的置信区间，影响控制图限制线</li>
        </ul>
        <h4>质量标准:</h4>
        <ul>
          <li><strong>优秀</strong>: 百分比容差 ≤ 3%, 绝对容差 ≤ 0.5N</li>
          <li><strong>良好</strong>: 百分比容差 ≤ 5%, 绝对容差 ≤ 1.0N</li>
          <li><strong>合格</strong>: 百分比容差 ≤ 10%, 绝对容差 ≤ 2.0N</li>
        </ul>
      </div>
    </el-alert>

    <el-form 
      ref="formRef"
      :model="localParams" 
      :rules="formRules"
      label-width="120px" 
      size="small"
      @validate="handleValidate"
    >
      <!-- 目标力值 -->
      <el-form-item label="目标力值(N)" prop="targetForces">
        <el-input
          v-model="localParams.targetForces"
          placeholder="例如: 5, 25, 50"
          :disabled="disabled"
          @input="handleTargetForcesChange"
          @blur="validateTargetForces"
          :class="{ 'validation-error': validation.targetForces.status === 'error' }"
        >
          <template #suffix>
            <el-tooltip content="添加常用力值" placement="top">
              <el-button size="small" @click="showForcePresets = true" type="text">
                <el-icon><Plus /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-input>
        <div class="param-feedback">
          <div class="param-tip">
            {{ parsedForces.length > 0 ? `已解析 ${parsedForces.length} 个力值: ${parsedForces.join(', ')}N` : '请输入有效的数值，用逗号分隔' }}
          </div>
          <el-tag 
            v-if="validation.targetForces.status !== 'success'" 
            :type="validation.targetForces.status === 'error' ? 'danger' : 'warning'" 
            size="small"
          >
            {{ validation.targetForces.message }}
          </el-tag>
          <el-tag v-else type="success" size="small">
            ✓ 有效
          </el-tag>
        </div>
      </el-form-item>

      <!-- 绝对容差 -->
      <el-form-item label="绝对容差" prop="absoluteTolerance">
        <el-input-number
          v-model="localParams.absoluteTolerance"
          :min="0.01"
          :max="10"
          :step="0.1"
          :precision="2"
          :disabled="disabled"
          @change="handleAbsoluteToleranceChange"
          style="width: 100%"
          :class="{ 'validation-warning': validation.absoluteTolerance.status === 'warning' }"
        />
        <div class="param-feedback">
          <div class="param-tip">
            单位: N (推荐范围: 0.1 ~ 2.0)
          </div>
          <el-tag 
            :type="getValidationTagType(validation.absoluteTolerance.status)"
            size="small"
          >
            {{ validation.absoluteTolerance.message }}
          </el-tag>
        </div>
      </el-form-item>

      <!-- 百分比容差 -->
      <el-form-item label="百分比容差" prop="percentageTolerance">
        <el-input-number
          v-model="localParams.percentageTolerance"
          :min="0.1"
          :max="50"
          :step="0.5"
          :precision="1"
          :disabled="disabled"
          @change="handlePercentageToleranceChange"
          style="width: 100%"
          :class="{ 'validation-warning': validation.percentageTolerance.status === 'warning' }"
        />
        <div class="param-feedback">
          <div class="param-tip">
            单位: % (推荐范围: 1% ~ 10%)
          </div>
          <el-tag 
            :type="getValidationTagType(validation.percentageTolerance.status)"
            size="small"
          >
            {{ validation.percentageTolerance.message }}
          </el-tag>
        </div>
      </el-form-item>

      <!-- 高级参数 -->
      <el-form-item>
        <el-button size="small" @click="showAdvanced = !showAdvanced" type="text">
          {{ showAdvanced ? '收起' : '展开' }}高级参数
          <el-icon><component :is="showAdvanced ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
        </el-button>
      </el-form-item>

      <el-collapse v-model="showAdvanced" v-if="showAdvanced">
        <el-collapse-item name="advanced">
          <el-form-item label="分析精度">
            <el-select v-model="localParams.precision" style="width: 100%" @change="updateParams">
              <el-option label="标准 (推荐)" value="standard" />
              <el-option label="高精度 (更准确)" value="high" />
              <el-option label="超高精度 (最慢)" value="ultra" />
            </el-select>
            <div class="param-tip">
              精度越高，分析越准确，但时间更长
            </div>
          </el-form-item>
          
          <el-form-item label="异常值检测">
            <el-switch 
              v-model="localParams.outlierDetection" 
              @change="updateParams"
              active-text="启用"
              inactive-text="禁用"
            />
            <div class="param-tip">
              自动识别和标记统计异常值
            </div>
          </el-form-item>
          
          <el-form-item label="置信度水平">
            <el-slider
              v-model="localParams.confidenceLevel"
              :min="90"
              :max="99.9"
              :step="0.1"
              :show-tooltip="true"
              :format-tooltip="val => `${val}%`"
              @change="updateParams"
            />
            <div class="param-tip">
              影响控制图的控制限计算，推荐95%
            </div>
          </el-form-item>
        </el-collapse-item>
      </el-collapse>
    </el-form>

    <!-- 参数预览和验证 -->
    <div class="params-preview">
      <el-divider content-position="left">参数预览</el-divider>
      
      <div class="preview-section">
        <div class="preview-item">
          <span class="preview-label">目标力值:</span>
          <div class="force-tags">
            <el-tag 
              v-for="force in parsedForces" 
              :key="force" 
              size="small"
              class="force-tag"
              :type="getForceTagType(force)"
            >
              {{ force }}N
            </el-tag>
            <el-tag v-if="parsedForces.length === 0" type="warning" size="small">
              无有效力值
            </el-tag>
          </div>
        </div>
        
        <div class="preview-item">
          <span class="preview-label">容差范围:</span>
          <span class="preview-value">
            绝对: ±{{ localParams.absoluteTolerance }}N, 相对: ±{{ localParams.percentageTolerance }}%
          </span>
        </div>
        
        <!-- 容差预览表格 -->
        <div v-if="parsedForces.length > 0" class="tolerance-table">
          <el-table :data="tolerancePreview" size="mini" style="width: 100%">
            <el-table-column prop="force" label="目标力值(N)" width="100" />
            <el-table-column prop="absoluteRange" label="绝对范围(N)" width="120" />
            <el-table-column prop="percentageRange" label="百分比范围(%)" width="140" />
            <el-table-column prop="quality" label="质量等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getQualityTagType(row.quality)" size="mini">
                  {{ row.quality }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="preview-item">
          <span class="preview-label">分析配置:</span>
          <div class="config-tags">
            <el-tag size="small" :type="getPrecisionTagType()">
              {{ getPrecisionText() }}
            </el-tag>
            <el-tag size="small" :type="localParams.outlierDetection ? 'success' : 'info'">
              异常值检测: {{ localParams.outlierDetection ? '启用' : '禁用' }}
            </el-tag>
            <el-tag size="small" type="info">
              置信度: {{ localParams.confidenceLevel }}%
            </el-tag>
          </div>
        </div>
        
        <div class="preview-item">
          <span class="preview-label">参数有效性:</span>
          <el-tag :type="overallValidation.type" size="small">
            {{ overallValidation.message }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 历史参数 -->
    <div v-if="showHistory" class="history-section">
      <el-divider content-position="left">历史参数</el-divider>
      <div class="history-list">
        <div 
          v-for="(item, index) in paramHistory" 
          :key="index"
          class="history-item"
          @click="applyHistoryParams(item)"
        >
          <div class="history-info">
            <span class="history-time">{{ formatTime(item.timestamp) }}</span>
            <span class="history-params">力值: {{ item.params.targetForces }}, 容差: ±{{ item.params.absoluteTolerance }}N/{{ item.params.percentageTolerance }}%</span>
          </div>
          <el-button size="mini" @click.stop="removeHistoryItem(index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <el-empty v-if="paramHistory.length === 0" description="暂无历史参数" :image-size="60" />
      </div>
    </div>

    <!-- 力值预设弹窗 -->
    <el-dialog v-model="showForcePresets" title="力值预设" width="600px">
      <div class="preset-section">
        <h4>常用力值预设:</h4>
        <div class="preset-buttons">
          <el-button 
            v-for="preset in forcePresets" 
            :key="preset.name"
            size="small"
            @click="applyForcePreset(preset)"
          >
            {{ preset.name }}: {{ preset.values.join(', ') }}N
          </el-button>
        </div>
        
        <el-divider />
        
        <h4>自定义力值:</h4>
        <el-form :model="customForce" inline>
          <el-form-item label="力值(N)">
            <el-input-number v-model="customForce.value" :min="0.1" :step="0.1" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addCustomForce">添加</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, QuestionFilled, Collection, Plus, ArrowUp, ArrowDown, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      targetForces: '5, 25, 50',
      absoluteTolerance: 0.5,
      percentageTolerance: 5,
      precision: 'standard',
      outlierDetection: true,
      confidenceLevel: 95
    })
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'validate', 'change'])

// 响应式状态
const formRef = ref(null)
const localParams = ref({ ...props.modelValue })
const showHelp = ref(false)
const showAdvanced = ref('')
const showHistory = ref(false)
const showForcePresets = ref(false)
const customForce = ref({ value: 10 })

// 参数模板
const paramTemplates = {
  default: {
    targetForces: '5, 25, 50',
    absoluteTolerance: 0.5,
    percentageTolerance: 5,
    precision: 'standard',
    outlierDetection: true,
    confidenceLevel: 95
  },
  precision: {
    targetForces: '5, 25, 50',
    absoluteTolerance: 0.2,
    percentageTolerance: 2,
    precision: 'high',
    outlierDetection: true,
    confidenceLevel: 99
  },
  tolerance: {
    targetForces: '5, 25, 50',
    absoluteTolerance: 1.0,
    percentageTolerance: 8,
    precision: 'standard',
    outlierDetection: false,
    confidenceLevel: 90
  },
  light: {
    targetForces: '1, 5, 10',
    absoluteTolerance: 0.1,
    percentageTolerance: 3,
    precision: 'high',
    outlierDetection: true,
    confidenceLevel: 95
  },
  medium: {
    targetForces: '10, 25, 50',
    absoluteTolerance: 0.5,
    percentageTolerance: 5,
    precision: 'standard',
    outlierDetection: true,
    confidenceLevel: 95
  },
  heavy: {
    targetForces: '50, 100, 200',
    absoluteTolerance: 2.0,
    percentageTolerance: 8,
    precision: 'standard',
    outlierDetection: true,
    confidenceLevel: 95
  }
}

// 力值预设
const forcePresets = [
  { name: '轻载', values: [1, 5, 10] },
  { name: '标准', values: [5, 25, 50] },
  { name: '中载', values: [10, 25, 50, 100] },
  { name: '重载', values: [50, 100, 200] },
  { name: '精密', values: [1, 2, 5, 10] },
  { name: '大范围', values: [5, 25, 50, 100, 200] }
]

// 参数历史
const paramHistory = ref([])

// 验证状态
const validation = ref({
  targetForces: { status: 'success', message: '有效' },
  absoluteTolerance: { status: 'success', message: '推荐范围内' },
  percentageTolerance: { status: 'success', message: '推荐范围内' }
})

// 表单验证规则
const formRules = {
  targetForces: [
    { required: true, message: '请输入目标力值', trigger: 'blur' },
    { validator: validateTargetForcesRule, trigger: 'blur' }
  ],
  absoluteTolerance: [
    { required: true, message: '请输入绝对容差', trigger: 'blur' },
    { type: 'number', min: 0.01, max: 10, message: '绝对容差范围: 0.01 ~ 10', trigger: 'blur' }
  ],
  percentageTolerance: [
    { required: true, message: '请输入百分比容差', trigger: 'blur' },
    { type: 'number', min: 0.1, max: 50, message: '百分比容差范围: 0.1 ~ 50', trigger: 'blur' }
  ]
}

// 计算属性
const parsedForces = computed(() => {
  if (!localParams.value.targetForces) return []
  return localParams.value.targetForces
    .split(',')
    .map(f => parseFloat(f.trim()))
    .filter(f => !isNaN(f) && f > 0)
    .sort((a, b) => a - b)
})

const tolerancePreview = computed(() => {
  return parsedForces.value.map(force => {
    const absRange = `${(force - localParams.value.absoluteTolerance).toFixed(2)} ~ ${(force + localParams.value.absoluteTolerance).toFixed(2)}`
    const percRange = `${(force * (1 - localParams.value.percentageTolerance / 100)).toFixed(2)} ~ ${(force * (1 + localParams.value.percentageTolerance / 100)).toFixed(2)}`
    
    let quality = '优秀'
    if (localParams.value.percentageTolerance > 5 || localParams.value.absoluteTolerance > 1.0) {
      quality = '良好'
    }
    if (localParams.value.percentageTolerance > 10 || localParams.value.absoluteTolerance > 2.0) {
      quality = '合格'
    }
    
    return {
      force,
      absoluteRange: absRange,
      percentageRange: percRange,
      quality
    }
  })
})

const overallValidation = computed(() => {
  const hasErrors = Object.values(validation.value).some(v => v.status === 'error')
  const hasWarnings = Object.values(validation.value).some(v => v.status === 'warning')
  
  if (hasErrors) {
    return { type: 'danger', message: '参数存在错误' }
  }
  if (hasWarnings) {
    return { type: 'warning', message: '参数可以优化' }
  }
  return { type: 'success', message: '参数配置良好' }
})

// 监听本地参数变化
watch(
  () => localParams.value,
  (newParams) => {
    emit('update:modelValue', { ...newParams })
    emit('change', { ...newParams })
    validateAllParams()
  },
  { deep: true }
)

// 监听外部参数变化
watch(
  () => props.modelValue,
  (newValue) => {
    localParams.value = { ...newValue }
  },
  { deep: true }
)

// 方法
function validateTargetForcesRule(rule, value, callback) {
  if (!value) {
    callback(new Error('请输入目标力值'))
    return
  }
  
  const forces = value.split(',').map(f => parseFloat(f.trim())).filter(f => !isNaN(f) && f > 0)
  if (forces.length === 0) {
    callback(new Error('请输入有效的数值'))
    return
  }
  
  callback()
}

function validateTargetForces() {
  const forces = parsedForces.value
  
  if (forces.length === 0) {
    validation.value.targetForces = { status: 'error', message: '无有效力值' }
    return
  }
  
  if (forces.length > 10) {
    validation.value.targetForces = { status: 'warning', message: '力值过多，建议不超过10个' }
    return
  }
  
  if (forces.some(f => f < 0.1)) {
    validation.value.targetForces = { status: 'warning', message: '存在过小的力值 (< 0.1N)' }
    return
  }
  
  if (forces.some(f => f > 1000)) {
    validation.value.targetForces = { status: 'warning', message: '存在过大的力值 (> 1000N)' }
    return
  }
  
  validation.value.targetForces = { status: 'success', message: '有效' }
}

function validateAbsoluteTolerance() {
  const tolerance = localParams.value.absoluteTolerance
  
  if (tolerance < 0.1) {
    validation.value.absoluteTolerance = { status: 'warning', message: '容差较小，可能过于严格' }
  } else if (tolerance > 2.0) {
    validation.value.absoluteTolerance = { status: 'warning', message: '容差较大，质量要求偏低' }
  } else {
    validation.value.absoluteTolerance = { status: 'success', message: '推荐范围内' }
  }
}

function validatePercentageTolerance() {
  const tolerance = localParams.value.percentageTolerance
  
  if (tolerance < 1) {
    validation.value.percentageTolerance = { status: 'warning', message: '容差较小，可能过于严格' }
  } else if (tolerance > 10) {
    validation.value.percentageTolerance = { status: 'warning', message: '容差较大，质量要求偏低' }
  } else {
    validation.value.percentageTolerance = { status: 'success', message: '推荐范围内' }
  }
}

function validateAllParams() {
  validateTargetForces()
  validateAbsoluteTolerance()
  validatePercentageTolerance()
  
  const isValid = !Object.values(validation.value).some(v => v.status === 'error')
  emit('validate', isValid)
}

function handleTargetForcesChange() {
  validateTargetForces()
  updateParams()
}

function handleAbsoluteToleranceChange() {
  validateAbsoluteTolerance()
  updateParams()
}

function handlePercentageToleranceChange() {
  validatePercentageTolerance()
  updateParams()
}

function handleValidate(prop, isValid, message) {
  // Element Plus 表单验证回调
}

function updateParams() {
  emit('update:modelValue', { ...localParams.value })
  emit('change', { ...localParams.value })
}

function handleTemplateSelect(command) {
  if (command === 'save') {
    saveCurrentParams()
  } else if (command === 'history') {
    showHistory.value = !showHistory.value
  } else if (paramTemplates[command]) {
    localParams.value = { ...paramTemplates[command] }
    ElMessage.success('模板应用成功')
  }
}

function saveCurrentParams() {
  const params = {
    params: { ...localParams.value },
    timestamp: Date.now(),
    name: `参数_${formatTime(Date.now())}`
  }
  
  paramHistory.value.unshift(params)
  
  // 只保留最近10次
  if (paramHistory.value.length > 10) {
    paramHistory.value = paramHistory.value.slice(0, 10)
  }
  
  saveToLocalStorage()
  ElMessage.success('参数已保存到历史记录')
}

function applyHistoryParams(item) {
  localParams.value = { ...item.params }
  ElMessage.success('历史参数应用成功')
}

function removeHistoryItem(index) {
  paramHistory.value.splice(index, 1)
  saveToLocalStorage()
}

function applyForcePreset(preset) {
  localParams.value.targetForces = preset.values.join(', ')
  showForcePresets.value = false
  ElMessage.success(`${preset.name}力值预设应用成功`)
}

function addCustomForce() {
  if (customForce.value.value && customForce.value.value > 0) {
    const currentForces = localParams.value.targetForces ? localParams.value.targetForces + ', ' : ''
    localParams.value.targetForces = currentForces + customForce.value.value
    customForce.value.value = 10
  }
}

function getForceTagType(force) {
  if (force <= 10) return 'success'
  if (force <= 50) return 'primary'
  if (force <= 100) return 'warning'
  return 'danger'
}

function getQualityTagType(quality) {
  switch (quality) {
    case '优秀': return 'success'
    case '良好': return 'primary'
    case '合格': return 'warning'
    default: return 'danger'
  }
}

function getPrecisionTagType() {
  switch (localParams.value.precision) {
    case 'ultra': return 'success'
    case 'high': return 'primary'
    default: return 'info'
  }
}

function getPrecisionText() {
  switch (localParams.value.precision) {
    case 'ultra': return '超高精度'
    case 'high': return '高精度'
    default: return '标准精度'
  }
}

function getValidationTagType(status) {
  switch (status) {
    case 'success': return 'success'
    case 'warning': return 'warning'
    case 'error': return 'danger'
    default: return 'info'
  }
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function loadFromLocalStorage() {
  try {
    const stored = localStorage.getItem('analysisParamHistory')
    if (stored) {
      paramHistory.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('加载历史参数失败:', error)
  }
}

function saveToLocalStorage() {
  try {
    localStorage.setItem('analysisParamHistory', JSON.stringify(paramHistory.value))
  } catch (error) {
    console.error('保存历史参数失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadFromLocalStorage()
  validateAllParams()
})
</script>

<style scoped>
.params-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.help-content h4 {
  margin: 16px 0 8px 0;
  color: var(--el-text-color-primary);
}

.help-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.help-content li {
  margin: 6px 0;
  line-height: 1.5;
}

.param-feedback {
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.validation-error {
  border-color: var(--el-color-error) !important;
}

.validation-warning {
  border-color: var(--el-color-warning) !important;
}

.params-preview {
  margin-top: 16px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
}

.preview-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.preview-label {
  min-width: 80px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.preview-value {
  color: var(--el-text-color-regular);
}

.force-tags, .config-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.force-tag {
  margin: 0;
}

.tolerance-table {
  margin-top: 12px;
}

.history-section {
  margin-top: 16px;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background-color: var(--el-bg-color-page);
  border-color: var(--el-color-primary);
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.history-params {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.preset-section h4 {
  margin: 16px 0 8px 0;
  color: var(--el-text-color-primary);
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style> 
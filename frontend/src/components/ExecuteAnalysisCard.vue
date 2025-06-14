<template>
  <el-card shadow="hover" class="execute-card">
    <template #header>
      <div class="card-header">
        <el-icon><VideoPlay /></el-icon>
        <span>执行分析</span>
        <div class="header-status" v-if="validationStatus">
          <el-tag :type="validationStatus.type" size="small">
            {{ validationStatus.message }}
          </el-tag>
        </div>
      </div>
    </template>

    <div class="execute-content">
      <!-- 执行条件检查 -->
      <div class="preconditions-check">
        <el-divider content-position="left">执行条件检查</el-divider>
        <div class="check-items">
          <div class="check-item" :class="getCheckItemClass(checks.file)">
            <el-icon><component :is="getCheckIcon(checks.file)" /></el-icon>
            <span class="check-label">文件上传</span>
            <span class="check-desc">{{ checks.file.message }}</span>
          </div>
          <div class="check-item" :class="getCheckItemClass(checks.params)">
            <el-icon><component :is="getCheckIcon(checks.params)" /></el-icon>
            <span class="check-label">参数配置</span>
            <span class="check-desc">{{ checks.params.message }}</span>
          </div>
          <div class="check-item" :class="getCheckItemClass(checks.data)">
            <el-icon><component :is="getCheckIcon(checks.data)" /></el-icon>
            <span class="check-label">数据质量</span>
            <span class="check-desc">{{ checks.data.message }}</span>
          </div>
          <div class="check-item" :class="getCheckItemClass(checks.service)">
            <el-icon><component :is="getCheckIcon(checks.service)" /></el-icon>
            <span class="check-label">服务状态</span>
            <span class="check-desc">{{ checks.service.message }}</span>
            <el-button v-if="checks.service.status === 'error'" size="mini" @click="checkServiceHealth">
              重试
            </el-button>
          </div>
        </div>
      </div>

      <!-- 状态信息 -->
      <div class="status-section">
        <div class="status-info">
          <el-icon class="status-icon" :class="statusIconClass">
            <component :is="statusIcon" />
          </el-icon>
          <div class="status-text">
            <div class="status-title">{{ statusTitle }}</div>
            <div class="status-desc">{{ statusDescription }}</div>
          </div>
        </div>
        
        <!-- 实时状态监控 -->
        <div v-if="systemHealth" class="system-health">
          <el-tag size="small" :type="getHealthTagType(systemHealth.status)">
            后端: {{ systemHealth.status }}
          </el-tag>
          <el-tag size="small" type="info">
            延迟: {{ systemHealth.latency }}ms
          </el-tag>
          <el-tag size="small" type="info">
            版本: {{ systemHealth.version }}
          </el-tag>
        </div>
      </div>

      <!-- 分析参数摘要 -->
      <div v-if="canExecute && analysisParams" class="analysis-summary">
        <el-divider content-position="left">分析摘要</el-divider>
        <el-descriptions :column="2" size="small">
          <el-descriptions-item label="数据文件">
            <el-tag size="small" type="success">{{ filename || '未上传' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数据行数">
            {{ dataStats?.total_rows || 0 }} 行
          </el-descriptions-item>
          <el-descriptions-item label="目标力值">
            {{ parsedTargetForces.join(', ') }}N
          </el-descriptions-item>
          <el-descriptions-item label="容差设置">
            绝对: ±{{ analysisParams.absoluteTolerance }}N, 相对: ±{{ analysisParams.percentageTolerance }}%
          </el-descriptions-item>
          <el-descriptions-item label="预计时长">
            {{ estimatedDuration }}
          </el-descriptions-item>
          <el-descriptions-item label="分析精度">
            <el-tag size="small" :type="getPrecisionTagType()">
              {{ getPrecisionText() }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="quality-preview">
          <h4>质量预览:</h4>
          <p>基于当前参数，预计将生成 <strong>{{ predictedCharts }}</strong> 个图表，质量等级为 <el-tag size="small" :type="getQualityTagType()">{{ predictedQuality }}</el-tag></p>
        </div>
      </div>

      <!-- 执行按钮 -->
      <div class="action-section">
        <el-button
          type="primary"
          size="large"
          :disabled="!canExecute"
          :loading="executing"
          @click="showExecuteDialog"
          class="execute-btn"
        >
          <el-icon v-if="!executing"><VideoPlay /></el-icon>
          {{ getButtonText() }}
        </el-button>
        
        <div v-if="!canExecute" class="blocking-reason">
          <el-alert
            :title="blockingReason"
            type="warning"
            show-icon
            :closable="false"
          />
        </div>
      </div>

      <!-- 分析步骤预览 -->
      <div class="steps-preview">
        <el-divider content-position="left">分析步骤</el-divider>
        <el-steps direction="vertical" :active="currentStep" finish-status="success">
          <el-step title="数据预处理" description="验证数据格式、检查缺失值和异常值" />
          <el-step title="R统计分析" description="执行专业统计分析，生成35种图表" />
          <el-step title="质量评估" description="计算过程能力指数、成功率等关键指标" />
          <el-step title="结果整理" description="组织分析结果，准备图表展示" />
        </el-steps>
      </div>

      <!-- 高级选项 -->
      <div class="advanced-section">
        <el-divider content-position="left">
          <el-button size="small" @click="showAdvanced = !showAdvanced" type="text">
            {{ showAdvanced ? '收起' : '展开' }}高级选项
            <el-icon><component :is="showAdvanced ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
          </el-button>
        </el-divider>
        
        <el-collapse v-model="showAdvanced" v-if="showAdvanced">
          <el-collapse-item name="advanced">
            <div class="advanced-options">
              <el-form size="small" label-width="120px">
                <el-form-item label="自动跳转">
                  <el-switch 
                    v-model="options.autoNavigate" 
                    active-text="分析完成后自动跳转到结果页面"
                  />
                </el-form-item>
                
                <el-form-item label="邮件通知">
                  <el-switch 
                    v-model="options.emailNotify" 
                    active-text="分析完成后发送邮件通知"
                    :disabled="true"
                  />
                  <div class="option-tip">功能开发中</div>
                </el-form-item>
                
                <el-form-item label="任务优先级">
                  <el-radio-group v-model="options.priority">
                    <el-radio label="low">普通</el-radio>
                    <el-radio label="normal">标准</el-radio>
                    <el-radio label="high">优先</el-radio>
                  </el-radio-group>
                  <div class="option-tip">高优先级任务将优先处理</div>
                </el-form-item>
                
                <el-form-item label="实验性功能">
                  <el-checkbox v-model="options.enableExperimental">
                    启用实验性分析算法
                  </el-checkbox>
                  <div class="option-tip">可能提供更准确的结果，但稳定性待验证</div>
                </el-form-item>
              </el-form>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 最近任务快速访问 -->
      <div v-if="recentTasks.length > 0" class="recent-tasks">
        <el-divider content-position="left">最近任务</el-divider>
        <div class="recent-list">
          <div 
            v-for="task in recentTasks" 
            :key="task.task_id"
            class="recent-task-item"
            @click="navigateToTask(task)"
          >
            <div class="task-info">
              <span class="task-file">{{ task.filename }}</span>
              <span class="task-time">{{ formatTaskTime(task.start_time) }}</span>
            </div>
            <el-tag :type="getTaskStatusType(task.status)" size="mini">
              {{ task.status }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 使用提示 -->
      <div class="usage-tips">
        <el-divider content-position="left">使用提示</el-divider>
        <div class="tip-list">
          <div class="tip-item">
            <el-icon><InfoFilled /></el-icon>
            <span>分析过程大约需要30-60秒，请保持网络连接</span>
          </div>
          <div class="tip-item">
            <el-icon><WarningFilled /></el-icon>
            <span>分析期间请不要关闭浏览器或刷新页面</span>
          </div>
          <div class="tip-item">
            <el-icon><CircleCheckFilled /></el-icon>
            <span>完成后可在结果页面查看35种专业图表和AI分析</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 执行确认对话框 -->
    <el-dialog 
      v-model="showConfirmDialog" 
      title="确认开始分析" 
      width="500px"
      :before-close="handleDialogClose"
      :close-on-click-modal="false"
    >
      <div class="confirm-content">
        <div class="confirm-summary">
          <h4>分析摘要:</h4>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="数据文件">{{ filename }}</el-descriptions-item>
            <el-descriptions-item label="数据行数">{{ dataStats?.total_rows || 0 }} 行</el-descriptions-item>
            <el-descriptions-item label="目标力值">{{ analysisParams?.targetForces }}</el-descriptions-item>
            <el-descriptions-item label="容差设置">±{{ analysisParams?.absoluteTolerance }}N ({{ analysisParams?.percentageTolerance }}%)</el-descriptions-item>
            <el-descriptions-item label="预计时长">{{ estimatedDuration }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <el-alert
          title="执行说明"
          type="info"
          show-icon
          :closable="false"
          style="margin: 16px 0;"
        >
          <ul style="margin: 0; padding-left: 20px;">
            <li>将执行完整的R统计分析，生成35种专业图表</li>
            <li>分析过程中系统将实时更新进度</li>
            <li>完成后{{ options.autoNavigate ? '自动' : '手动' }}跳转到结果页面</li>
            <li>所有数据和结果将保存在系统中</li>
          </ul>
        </el-alert>
        
        <div class="confirm-options">
          <el-checkbox v-model="options.generateAI">
            同时生成DeepSeek AI智能分析报告
          </el-checkbox>
          <div class="option-desc">AI分析将提供专业的数据解读和改进建议</div>
        </div>

        <div v-if="warnings.length > 0" class="warnings-section">
          <h4>注意事项:</h4>
          <el-alert
            v-for="warning in warnings"
            :key="warning"
            :title="warning"
            type="warning"
            show-icon
            :closable="false"
            style="margin-bottom: 8px;"
          />
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showConfirmDialog = false" :disabled="creating">
            取消
          </el-button>
          <el-button type="primary" @click="confirmExecute" :loading="creating">
            {{ creating ? '创建任务中...' : '确认开始分析' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  VideoPlay, 
  CircleCheck, 
  CircleClose, 
  Warning, 
  ArrowUp, 
  ArrowDown,
  InfoFilled,
  WarningFilled,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import { useAnalysisStore } from '@/stores/analysis'
import { analysisAPI } from '@/api'
import { getFullApiURL } from '@/config'

const props = defineProps({
  filename: String,
  analysisParams: Object,
  dataStats: Object,
  fileValidation: Object,
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['analysis-started', 'task-created'])

const router = useRouter()
const analysisStore = useAnalysisStore()

// 响应式状态
const executing = ref(false)
const creating = ref(false)
const showConfirmDialog = ref(false)
const showAdvanced = ref('')
const currentStep = ref(0)
const systemHealth = ref(null)
const healthCheckInterval = ref(null)

// 高级选项
const options = ref({
  autoNavigate: true,
  emailNotify: false,
  priority: 'normal',
  generateAI: true,
  enableExperimental: false
})

// 最近任务
const recentTasks = ref([])

// 执行条件检查
const checks = ref({
  file: { status: 'pending', message: '检查文件状态...' },
  params: { status: 'pending', message: '检查参数配置...' },
  data: { status: 'pending', message: '检查数据质量...' },
  service: { status: 'pending', message: '检查服务状态...' }
})

// 计算属性
const parsedTargetForces = computed(() => {
  if (!props.analysisParams?.targetForces) return []
  return props.analysisParams.targetForces
    .split(',')
    .map(f => parseFloat(f.trim()))
    .filter(f => !isNaN(f) && f > 0)
})

const canExecute = computed(() => {
  return Object.values(checks.value).every(check => check.status === 'success') && 
         !props.disabled
})

const blockingReason = computed(() => {
  const failedChecks = Object.entries(checks.value)
    .filter(([key, check]) => check.status !== 'success')
    .map(([key, check]) => check.message)
  
  if (failedChecks.length === 0) return ''
  return `无法执行: ${failedChecks.join(', ')}`
})

const statusIcon = computed(() => {
  if (executing.value) return 'Loading'
  if (canExecute.value) return 'CircleCheck'
  return 'Warning'
})

const statusIconClass = computed(() => {
  if (executing.value) return 'status-running'
  if (canExecute.value) return 'status-ready'
  return 'status-warning'
})

const statusTitle = computed(() => {
  if (executing.value) return '正在执行分析'
  if (canExecute.value) return '就绪，可以开始分析'
  return '等待条件满足'
})

const statusDescription = computed(() => {
  if (executing.value) return '分析任务正在后台运行，请稍候...'
  if (canExecute.value) return '所有条件已满足，点击按钮开始分析'
  return '请完成必要的准备工作'
})

const validationStatus = computed(() => {
  if (canExecute.value) {
    return { type: 'success', message: '准备就绪' }
  }
  return { type: 'warning', message: '等待中' }
})

const estimatedDuration = computed(() => {
  const baseTime = 30
  const dataRows = props.dataStats?.total_rows || 0
  const forceCount = parsedTargetForces.value.length
  const precisionMultiplier = getPrecisionMultiplier()
  
  const estimated = baseTime + (dataRows / 10) + (forceCount * 5) * precisionMultiplier
  return `约 ${Math.ceil(estimated)} 秒`
})

const predictedCharts = computed(() => {
  return 35 // 固定35个图表
})

const predictedQuality = computed(() => {
  const absToler = props.analysisParams?.absoluteTolerance || 1
  const percToler = props.analysisParams?.percentageTolerance || 10
  
  if (percToler <= 3 && absToler <= 0.5) return '优秀'
  if (percToler <= 5 && absToler <= 1.0) return '良好'
  if (percToler <= 10 && absToler <= 2.0) return '合格'
  return '待优化'
})

const warnings = computed(() => {
  const warns = []
  
  if (props.dataStats?.total_rows > 1000) {
    warns.push('数据量较大，分析时间可能延长')
  }
  
  if (parsedTargetForces.value.length > 5) {
    warns.push('目标力值较多，将生成更多图表')
  }
  
  if (props.analysisParams?.precision === 'ultra') {
    warns.push('超高精度模式将显著增加计算时间')
  }
  
  return warns
})

// 方法
function getCheckItemClass(check) {
  return {
    'check-success': check.status === 'success',
    'check-error': check.status === 'error',
    'check-warning': check.status === 'warning',
    'check-pending': check.status === 'pending'
  }
}

function getCheckIcon(check) {
  switch (check.status) {
    case 'success': return 'CircleCheck'
    case 'error': return 'CircleClose'
    case 'warning': return 'Warning'
    default: return 'Loading'
  }
}

function getHealthTagType(status) {
  switch (status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'unhealthy': return 'danger'
    default: return 'info'
  }
}

function getPrecisionTagType() {
  switch (props.analysisParams?.precision) {
    case 'ultra': return 'danger'
    case 'high': return 'warning'
    default: return 'success'
  }
}

function getPrecisionText() {
  switch (props.analysisParams?.precision) {
    case 'ultra': return '超高精度'
    case 'high': return '高精度'
    default: return '标准精度'
  }
}

function getPrecisionMultiplier() {
  switch (props.analysisParams?.precision) {
    case 'ultra': return 2.0
    case 'high': return 1.5
    default: return 1.0
  }
}

function getQualityTagType() {
  switch (predictedQuality.value) {
    case '优秀': return 'success'
    case '良好': return 'primary'
    case '合格': return 'warning'
    default: return 'danger'
  }
}

function getTaskStatusType(status) {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'warning'
    default: return 'info'
  }
}

function getButtonText() {
  if (creating.value) return '创建任务中...'
  if (executing.value) return '分析进行中...'
  if (!canExecute.value) return '等待条件满足'
  return '开始分析'
}

async function checkAllConditions() {
  // 检查文件
  if (props.filename) {
    checks.value.file = { status: 'success', message: `文件已上传: ${props.filename}` }
  } else {
    checks.value.file = { status: 'error', message: '请先上传CSV文件' }
  }

  // 检查参数
  if (props.analysisParams && parsedTargetForces.value.length > 0) {
    checks.value.params = { status: 'success', message: `参数已配置: ${parsedTargetForces.value.length}个目标力值` }
  } else {
    checks.value.params = { status: 'error', message: '请配置分析参数' }
  }

  // 检查数据质量
  if (props.fileValidation?.valid) {
    checks.value.data = { status: 'success', message: '数据验证通过' }
  } else if (props.fileValidation?.valid === false) {
    checks.value.data = { status: 'error', message: '数据验证失败' }
  } else {
    checks.value.data = { status: 'warning', message: '等待数据验证' }
  }

  // 检查服务状态
  await checkServiceHealth()
}

async function checkServiceHealth() {
  try {
    const startTime = Date.now()
    
    // 检查后端健康状态
    const response = await fetch(getFullApiURL('/health'))
    const latency = Date.now() - startTime
    
    if (response.ok) {
      systemHealth.value = {
        status: 'healthy',
        latency,
        version: 'unknown'
      }
      checks.value.service = { status: 'success', message: '后端服务正常' }
    } else {
      throw new Error('Service unhealthy')
    }
  } catch (error) {
    systemHealth.value = {
      status: 'unhealthy',
      latency: 0,
      version: 'unknown'
    }
    checks.value.service = { status: 'error', message: '后端服务不可用' }
  }
}

function showExecuteDialog() {
  if (!canExecute.value) {
    ElMessage.warning('请先满足所有执行条件')
    return
  }
  showConfirmDialog.value = true
}

async function confirmExecute() {
  if (!canExecute.value) return

  try {
    creating.value = true
    
    // 构建分析参数
    const analysisRequestParams = {
      filename: props.filename,
      target_forces: parsedTargetForces.value,
      absolute_tolerance: props.analysisParams.absoluteTolerance,
      percentage_tolerance: props.analysisParams.percentageTolerance,
      precision: props.analysisParams.precision || 'standard',
      outlier_detection: props.analysisParams.outlierDetection || true,
      confidence_level: props.analysisParams.confidenceLevel || 95,
      priority: options.value.priority,
      auto_ai_analysis: options.value.generateAI,
      enable_experimental: options.value.enableExperimental
    }

    // 创建分析任务
    const task = await analysisStore.startAnalysis(analysisRequestParams)
    
    showConfirmDialog.value = false
    
    ElNotification({
      title: '分析任务已创建',
      message: `任务ID: ${task.task_id}`,
      type: 'success',
      duration: 3000
    })

    emit('analysis-started', task)
    emit('task-created', task)

    // 保存到最近任务
    saveToRecentTasks(task)

    // 跳转到任务状态页面
    if (options.value.autoNavigate) {
      router.push(`/task/${task.task_id}`)
    } else {
      ElMessage.success('任务已创建，可在任务管理页面查看进度')
    }

  } catch (error) {
    ElMessage.error(`分析任务创建失败: ${error.message || '未知错误'}`)
  } finally {
    creating.value = false
  }
}

function handleDialogClose() {
  if (!creating.value) {
    showConfirmDialog.value = false
  }
}

function navigateToTask(task) {
  router.push(`/task/${task.task_id}`)
}

function formatTaskTime(timeString) {
  return new Date(timeString).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function saveToRecentTasks(task) {
  const taskInfo = {
    task_id: task.task_id,
    filename: props.filename,
    start_time: new Date().toISOString(),
    status: 'pending'
  }
  
  recentTasks.value.unshift(taskInfo)
  
  // 只保留最近5个
  if (recentTasks.value.length > 5) {
    recentTasks.value = recentTasks.value.slice(0, 5)
  }
  
  // 保存到localStorage
  try {
    localStorage.setItem('recentAnalysisTasks', JSON.stringify(recentTasks.value))
  } catch (error) {
    console.error('保存最近任务失败:', error)
  }
}

function loadRecentTasks() {
  try {
    const stored = localStorage.getItem('recentAnalysisTasks')
    if (stored) {
      recentTasks.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('加载最近任务失败:', error)
  }
}

function startHealthCheck() {
  // 立即检查一次
  checkServiceHealth()
  
  // 每30秒检查一次服务健康状态
  healthCheckInterval.value = setInterval(checkServiceHealth, 30000)
}

function stopHealthCheck() {
  if (healthCheckInterval.value) {
    clearInterval(healthCheckInterval.value)
    healthCheckInterval.value = null
  }
}

// 监听属性变化
watch([
  () => props.filename,
  () => props.analysisParams,
  () => props.fileValidation
], () => {
  checkAllConditions()
}, { deep: true })

// 生命周期
onMounted(() => {
  loadRecentTasks()
  startHealthCheck()
  checkAllConditions()
})

onUnmounted(() => {
  stopHealthCheck()
})
</script>

<style scoped>
.execute-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-status {
  margin-left: auto;
}

.execute-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 条件检查 */
.preconditions-check {
  margin-bottom: 20px;
}

.check-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-light);
  transition: all 0.2s;
}

.check-item.check-success {
  background-color: var(--el-color-success-light-9);
  border-color: var(--el-color-success-light-5);
  color: var(--el-color-success);
}

.check-item.check-error {
  background-color: var(--el-color-error-light-9);
  border-color: var(--el-color-error-light-5);
  color: var(--el-color-error);
}

.check-item.check-warning {
  background-color: var(--el-color-warning-light-9);
  border-color: var(--el-color-warning-light-5);
  color: var(--el-color-warning);
}

.check-item.check-pending {
  background-color: var(--el-bg-color-page);
  border-color: var(--el-border-color);
  color: var(--el-text-color-regular);
}

.check-label {
  min-width: 80px;
  font-weight: 600;
}

.check-desc {
  flex: 1;
  font-size: 14px;
}

/* 状态信息 */
.status-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, var(--el-bg-color-page) 0%, var(--el-color-primary-light-9) 100%);
  border-radius: 8px;
}

.status-icon {
  font-size: 32px;
}

.status-icon.status-ready {
  color: var(--el-color-success);
}

.status-icon.status-warning {
  color: var(--el-color-warning);
}

.status-icon.status-running {
  color: var(--el-color-primary);
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-text {
  flex: 1;
}

.status-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.status-desc {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.system-health {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 分析摘要 */
.analysis-summary {
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.quality-preview {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.quality-preview h4 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.quality-preview p {
  margin: 0;
  line-height: 1.6;
}

/* 执行按钮 */
.action-section {
  text-align: center;
  margin: 20px 0;
}

.execute-btn {
  width: 200px;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
}

.blocking-reason {
  margin-top: 16px;
}

/* 步骤预览 */
.steps-preview {
  margin: 20px 0;
}

/* 高级选项 */
.advanced-section {
  margin: 20px 0;
}

.advanced-options {
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
}

.option-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

/* 最近任务 */
.recent-tasks {
  margin: 20px 0;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.recent-task-item:hover {
  background-color: var(--el-bg-color-page);
  border-color: var(--el-color-primary);
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-file {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.task-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 使用提示 */
.usage-tips {
  margin: 20px 0;
}

.tip-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

/* 确认对话框 */
.confirm-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.confirm-summary h4 {
  margin: 0 0 12px 0;
  color: var(--el-text-color-primary);
}

.confirm-options {
  padding: 12px;
  background-color: var(--el-bg-color-page);
  border-radius: 6px;
}

.option-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.warnings-section h4 {
  margin: 0 0 12px 0;
  color: var(--el-text-color-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 
<template>
  <div class="task-status-indicator">
    <el-tag
      :type="statusConfig.type"
      :effect="effect"
      size="large"
      class="status-tag"
    >
      <el-icon class="status-icon" :class="{ 'is-loading': status === 'running' }">
        <component :is="statusConfig.icon" />
      </el-icon>
      <span class="status-text">{{ statusConfig.text }}</span>
    </el-tag>
    
    <!-- 时间信息 -->
    <div v-if="showTime" class="time-info">
      <span v-if="startTime" class="start-time">
        开始时间: {{ formatTime(startTime) }}
      </span>
      <span v-if="endTime && status === 'completed'" class="end-time">
        完成时间: {{ formatTime(endTime) }}
      </span>
      <span v-if="duration" class="duration">
        耗时: {{ formatDuration(duration) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Clock, Loading, CircleCheck, CircleClose, WarningFilled } from '@element-plus/icons-vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['pending', 'running', 'completed', 'failed'].includes(value)
  },
  effect: {
    type: String,
    default: 'dark'
  },
  showTime: {
    type: Boolean,
    default: false
  },
  startTime: {
    type: String,
    default: null
  },
  endTime: {
    type: String,
    default: null
  },
  duration: {
    type: Number,
    default: null
  }
})

const statusConfig = computed(() => {
  const configs = {
    pending: {
      type: 'info',
      icon: Clock,
      text: '等待中'
    },
    running: {
      type: 'warning',
      icon: Loading,
      text: '运行中'
    },
    completed: {
      type: 'success',
      icon: CircleCheck,
      text: '已完成'
    },
    failed: {
      type: 'danger',
      icon: CircleClose,
      text: '失败'
    }
  }
  
  return configs[props.status] || configs.pending
})

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return timeStr
  }
}

const formatDuration = (seconds) => {
  if (!seconds) return ''
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
}
</script>

<style scoped>
.task-status-indicator {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
}

.status-icon {
  font-size: 16px;
}

.status-icon.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.status-text {
  margin-left: 4px;
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.time-info span {
  display: block;
}
</style> 
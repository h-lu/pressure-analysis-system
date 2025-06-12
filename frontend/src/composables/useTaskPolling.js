import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'
import { analysisAPI } from '@/api'

export function useTaskPolling(taskId) {
  const router = useRouter()
  const currentTask = ref(null)
  const polling = ref(false)
  const error = ref(null)
  
  let pollTimer = null
  let retryCount = 0
  const maxRetries = 3

  const startPolling = () => {
    if (polling.value || !taskId) return
    
    polling.value = true
    retryCount = 0
    error.value = null
    
    const poll = async () => {
      try {
        const task = await analysisAPI.getTaskStatus(taskId)
        currentTask.value = task
        error.value = null
        retryCount = 0
        
        // 根据状态调整轮询间隔
        const interval = task.status === 'running' ? 2000 : 5000
        
        if (['completed', 'failed'].includes(task.status)) {
          stopPolling()
          
          if (task.status === 'completed') {
            // 任务完成，发送通知并跳转到结果页面
            ElNotification({
              title: '分析完成',
              message: '数据分析已成功完成！点击查看结果',
              type: 'success',
              duration: 5000,
              onClick: () => {
                router.push(`/results/${taskId}`)
              }
            })
            
            // 自动跳转到结果页面（延迟3秒）
            setTimeout(() => {
              router.push(`/results/${taskId}`)
            }, 3000)
          } else if (task.status === 'failed') {
            // 任务失败通知
            ElNotification({
              title: '分析失败',
              message: task.error || '任务执行过程中出现错误',
              type: 'error',
              duration: 0
            })
          }
        } else {
          // 继续轮询
          pollTimer = setTimeout(poll, interval)
        }
        
      } catch (err) {
        console.error('轮询失败:', err)
        error.value = err
        retryCount++
        
        if (retryCount < maxRetries) {
          // 重试，使用递增的延迟时间
          const retryDelay = Math.min(10000 * retryCount, 30000)
          console.log(`轮询失败，${retryDelay/1000}秒后重试 (${retryCount}/${maxRetries})`)
          pollTimer = setTimeout(poll, retryDelay)
        } else {
          // 达到最大重试次数，停止轮询
          stopPolling()
          ElNotification({
            title: '连接异常',
            message: '无法获取任务状态，请检查网络连接或刷新页面重试',
            type: 'error',
            duration: 0
          })
        }
      }
    }
    
    // 立即执行第一次轮询
    poll()
  }
  
  const stopPolling = () => {
    if (pollTimer) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
    polling.value = false
  }
  
  const restartPolling = () => {
    stopPolling()
    startPolling()
  }
  
  const forceRefresh = async () => {
    if (!taskId) return
    
    try {
      const task = await analysisAPI.getTaskStatus(taskId)
      currentTask.value = task
      error.value = null
      
      // 如果任务还在运行且当前没有轮询，则重新开始轮询
      if (['pending', 'running'].includes(task.status) && !polling.value) {
        startPolling()
      }
      
      return task
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  // 组件卸载时清理定时器
  onUnmounted(() => {
    stopPolling()
  })

  return {
    currentTask,
    polling,
    error,
    startPolling,
    stopPolling,
    restartPolling,
    forceRefresh
  }
} 
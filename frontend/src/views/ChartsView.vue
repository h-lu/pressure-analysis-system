<template>
  <div class="charts-view">
    <el-page-header @back="onBack" :content="`图表展示 - ${taskId}`" />
    
    <div class="charts-content">
      <el-card>
        <h3>35个专业图表</h3>
        <p>任务ID: {{ taskId }}</p>
        <p>此页面将展示所有35个分析图表</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  }
})

const router = useRouter()

const onBack = () => {
  router.push(`/results/${props.taskId}`)
}
</script>

<style scoped>
.charts-view {
  max-width: 1400px;
  margin: 0 auto;
}

.charts-content {
  margin-top: 20px;
}
</style> 
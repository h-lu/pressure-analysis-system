<template>
  <div class="sidebar-menu" :class="{ 'mobile-menu': mobile, 'collapsed-menu': collapsed }">
    <el-menu
      :default-active="$route.path"
      router
      class="sidebar-menu-el"
      :collapse="menuConfig.collapse"
      :collapse-transition="menuConfig.collapseTransition"
      :unique-opened="menuConfig.uniqueOpened"
      :mode="menuConfig.mode"
      @select="handleMenuSelect"
    >
      <el-menu-item index="/analysis">
        <el-icon><Document /></el-icon>
        <template #title>数据分析</template>
      </el-menu-item>
      
      <el-menu-item index="/tasks">
        <el-icon><List /></el-icon>
        <template #title>任务管理</template>
      </el-menu-item>
      
      <el-menu-item index="/history">
        <el-icon><Clock /></el-icon>
        <template #title>历史记录</template>
      </el-menu-item>
      
      <el-menu-item index="/files">
        <el-icon><Folder /></el-icon>
        <template #title>文件管理</template>
      </el-menu-item>
      
      <el-sub-menu index="charts">
        <template #title>
          <el-icon><PieChart /></el-icon>
          <span>图表展示</span>
        </template>
        <el-menu-item 
          v-if="currentTask" 
          :index="`/charts/${currentTask.task_id}`"
        >
          <el-icon><TrendCharts /></el-icon>
          <template #title>所有图表 (35张)</template>
        </el-menu-item>
        <el-menu-item v-else disabled>
          <el-icon><TrendCharts /></el-icon>
          <template #title>暂无可用图表</template>
        </el-menu-item>
      </el-sub-menu>
      
      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <template #title>系统设置</template>
      </el-menu-item>
    </el-menu>
    
    <!-- 折叠按钮 (仅桌面端显示) -->
    <div 
      v-if="!mobile" 
      class="collapse-btn" 
      @click="toggleCollapse"
      :class="{ 'collapsed': collapsed }"
    >
      <el-icon>
        <component :is="collapsed ? 'Expand' : 'Fold'" />
      </el-icon>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  },
  mobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['menu-click', 'toggle-collapse'])

const analysisStore = useAnalysisStore()
const localCollapsed = ref(false)

const currentTask = computed(() => analysisStore.currentTask)

// 计算菜单配置
const menuConfig = computed(() => {
  return {
    collapse: props.collapsed && !props.mobile,
    collapseTransition: false,
    uniqueOpened: props.mobile,
    mode: 'vertical'
  }
})

// 处理菜单点击
const handleMenuSelect = (index, indexPath) => {
  if (props.mobile) {
    emit('menu-click', index)
  }
}

const toggleCollapse = () => {
  if (props.mobile) return
  
  localCollapsed.value = !localCollapsed.value
  emit('toggle-collapse', localCollapsed.value)
}
</script>

<style scoped>
.sidebar-menu {
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color-page);
}

.sidebar-menu-el {
  border-right: none;
  flex: 1;
  background-color: transparent;
}

.sidebar-menu-el:not(.el-menu--collapse) {
  width: 220px;
}

/* 移动端菜单样式 */
.mobile-menu {
  width: 100%;
  height: 100%;
}

.mobile-menu .sidebar-menu-el {
  width: 100%;
}

.mobile-menu .sidebar-menu-el .el-menu-item,
.mobile-menu .sidebar-menu-el .el-sub-menu .el-sub-menu__title {
  height: 56px;
  line-height: 56px;
  font-size: 16px;
}

/* 折叠状态样式 */
.collapsed-menu .sidebar-menu-el {
  width: 60px;
}

.collapse-btn {
  padding: 12px;
  text-align: center;
  cursor: pointer;
  border-top: 1px solid var(--el-border-color-light);
  color: var(--el-text-color-regular);
  transition: all 0.3s;
  background-color: var(--el-bg-color-page);
}

.collapse-btn:hover {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.collapse-btn.collapsed {
  width: 60px;
}

/* 菜单项样式优化 */
.sidebar-menu-el .el-menu-item,
.sidebar-menu-el .el-sub-menu .el-sub-menu__title {
  height: 48px;
  line-height: 48px;
  border-radius: 6px;
  margin: 2px 6px;
  transition: all 0.3s;
}

.sidebar-menu-el .el-menu-item:hover,
.sidebar-menu-el .el-sub-menu .el-sub-menu__title:hover {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.sidebar-menu-el .el-menu-item.is-active {
  background-color: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  font-weight: 600;
}

.sidebar-menu-el .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 0;
  height: 100%;
  width: 3px;
  background-color: var(--el-color-primary);
  border-radius: 2px;
}

/* 子菜单样式 */
.sidebar-menu-el .el-sub-menu .el-menu-item {
  margin: 1px 12px 1px 24px;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
}

/* 图标样式 */
.sidebar-menu-el .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* 折叠状态下的样式调整 */
.sidebar-menu-el.el-menu--collapse .el-menu-item,
.sidebar-menu-el.el-menu--collapse .el-sub-menu .el-sub-menu__title {
  margin: 2px 4px;
  text-align: center;
}

.sidebar-menu-el.el-menu--collapse .el-icon {
  margin-right: 0;
}

/* 移动端触摸优化 */
@media (hover: none) and (pointer: coarse) {
  .mobile-menu .sidebar-menu-el .el-menu-item,
  .mobile-menu .sidebar-menu-el .el-sub-menu .el-sub-menu__title {
    height: 60px;
    line-height: 60px;
    font-size: 18px;
  }
  
  .mobile-menu .sidebar-menu-el .el-icon {
    font-size: 20px;
  }
}

/* 响应式断点 */
@media (max-width: 1024px) {
  .sidebar-menu-el .el-menu-item,
  .sidebar-menu-el .el-sub-menu .el-sub-menu__title {
    height: 44px;
    line-height: 44px;
  }
}

@media (max-width: 768px) {
  .collapse-btn {
    display: none;
  }
}

@media (max-width: 480px) {
  .mobile-menu .sidebar-menu-el .el-menu-item,
  .mobile-menu .sidebar-menu-el .el-sub-menu .el-sub-menu__title {
    padding: 0 16px;
    font-size: 16px;
  }
}
</style> 
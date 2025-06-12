<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 页面标题映射
const pageTitleMap = {
  '/analysis': '数据分析',
  '/tasks': '任务管理', 
  '/history': '历史记录',
  '/files': '文件管理',
  '/settings': '系统设置'
}

const currentPageTitle = computed(() => {
  return pageTitleMap[route.path] || '数据分析'
})
</script>

<template>
  <el-container class="main-layout">
    <!-- 顶部导航栏 -->
    <el-header class="main-header" height="60px">
      <div class="header-left">
        <h1 class="system-title">压力采集数据分析系统</h1>
      </div>
      <div class="header-right">
        <el-button text class="header-btn">主题切换</el-button>
        <span class="divider">|</span>
        <el-button text class="header-btn">用户设置</el-button>
      </div>
    </el-header>
    
    <el-container>
      <!-- 侧边栏 -->
      <el-aside class="main-sidebar" width="200px">
        <div class="sidebar-content">
          <!-- 导航菜单 -->
          <div class="sidebar-menu">
            <router-link to="/analysis" class="menu-item active">
              <span class="menu-icon">📊</span>
              <span class="menu-text">数据分析</span>
            </router-link>
            <router-link to="/tasks" class="menu-item">
              <span class="menu-icon">📋</span>
              <span class="menu-text">任务管理</span>
            </router-link>
            <router-link to="/history" class="menu-item">
              <span class="menu-icon">📚</span>
              <span class="menu-text">历史记录</span>
            </router-link>
            <router-link to="/files" class="menu-item">
              <span class="menu-icon">📁</span>
              <span class="menu-text">文件管理</span>
            </router-link>
            <router-link to="/settings" class="menu-item">
              <span class="menu-icon">⚙️</span>
              <span class="menu-text">系统设置</span>
            </router-link>
          </div>
          
          <!-- 系统状态区域 -->
          <div class="system-status">
            <div class="status-title">系统状态</div>
            <div class="status-item">
              <span class="status-indicator online"></span>
              <span class="status-text">服务正常</span>
            </div>
            <div class="status-detail">API: 连接正常</div>
          </div>
        </div>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <!-- 面包屑导航 -->
        <div class="breadcrumb-nav">
          <span class="breadcrumb-text">首页 > {{ currentPageTitle }}</span>
        </div>
        
        <!-- 页面标题 -->
        <h2 class="page-title">{{ currentPageTitle }}</h2>
        
        <!-- 路由视图 -->
        <div class="content-area">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.main-layout {
  height: 100vh;
  background-color: #f5f7fa;
}

/* 顶部导航栏 */
.main-header {
  background-color: #409EFF;
  border-bottom: 1px solid #366db3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left .system-title {
  color: white;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-btn {
  color: white !important;
  font-size: 14px;
  padding: 8px 12px;
}

.header-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.divider {
  color: white;
  margin: 0 4px;
}

/* 侧边栏 */
.main-sidebar {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  height: calc(100vh - 60px);
}

.sidebar-content {
  padding: 10px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 10px;
  border-radius: 4px;
  text-decoration: none;
  color: #606266;
  font-size: 14px;
  transition: all 0.3s;
  gap: 8px;
}

.menu-item:hover {
  background-color: #f0f0f0;
}

.menu-item.active {
  background-color: #409EFF;
  color: white;
}

.menu-icon {
  font-size: 16px;
  width: 20px;
}

.menu-text {
  flex: 1;
}

/* 系统状态区域 */
.system-status {
  background-color: #f9f9f9;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px 10px;
  margin-top: 20px;
}

.status-title {
  color: #909399;
  font-size: 12px;
  margin-bottom: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.online {
  background-color: #67C23A;
}

.status-text {
  color: #606266;
  font-size: 12px;
}

.status-detail {
  color: #909399;
  font-size: 10px;
  margin-top: 5px;
}

/* 主内容区 */
.main-content {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  padding: 0;
}

.breadcrumb-nav {
  background-color: #fafbfc;
  padding: 10px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.breadcrumb-text {
  color: #909399;
  font-size: 12px;
}

.page-title {
  color: #303133;
  font-size: 20px;
  font-weight: bold;
  margin: 20px 20px 0 20px;
}

.content-area {
  padding: 20px;
  min-height: calc(100vh - 160px);
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin: 20px;
  position: relative;
}

.content-area::before {
  content: '主要内容区域';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #c0c4cc;
  font-size: 16px;
  text-align: center;
}

.content-area::after {
  content: '根据选中的页面显示对应内容';
  position: absolute;
  top: calc(50% + 25px);
  left: 50%;
  transform: translate(-50%, -50%);
  color: #c0c4cc;
  font-size: 14px;
  text-align: center;
}
</style>

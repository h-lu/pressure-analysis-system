<template>
  <el-container class="app-container">
    <!-- 简单的顶部导航栏 -->
    <el-header class="app-header" height="60px">
      <div class="header-left">
        <h1 class="app-title">
          <el-icon><DataAnalysis /></el-icon>
          <span>压力采集数据分析系统</span>
        </h1>
      </div>
      <div class="header-right">
        <el-button text>
          <el-icon><Moon /></el-icon>
          <span>主题切换</span>
        </el-button>
        <el-button text>
          <el-icon><User /></el-icon>
          <span>用户设置</span>
        </el-button>
      </div>
    </el-header>
    
    <el-container class="content-container">
      <!-- 侧边栏 -->
      <el-aside class="app-sidebar" width="220px">
        <div class="sidebar-content">
          <h3>导航菜单</h3>
          <ul>
            <li><router-link to="/analysis">数据分析</router-link></li>
            <li><router-link to="/tasks">任务管理</router-link></li>
            <li><router-link to="/settings">系统设置</router-link></li>
          </ul>
        </div>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
// 简单导入
import { DataAnalysis, Moon, User } from '@element-plus/icons-vue'
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100vw;
  background-color: var(--el-bg-color);
  overflow: hidden;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.content-container {
  flex: 1;
  display: flex;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.app-sidebar {
  background-color: var(--el-bg-color-page);
  border-right: 1px solid var(--el-border-color);
  flex-shrink: 0;
  overflow-y: auto;
}

.sidebar-content {
  padding: 20px;
  height: 100%;
}

.sidebar-content h3 {
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
  font-size: 14px;
  font-weight: 600;
}

.sidebar-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-content li {
  margin-bottom: 4px;
}

.sidebar-content a {
  display: block;
  padding: 12px 16px;
  color: var(--el-text-color-regular);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 14px;
}

.sidebar-content a:hover {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.sidebar-content a.router-link-active {
  background-color: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  font-weight: 600;
}

.app-main {
  flex: 1;
  padding: 20px;
  background-color: var(--el-bg-color);
  overflow-y: auto;
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }
  
  .app-title {
    font-size: 16px;
  }
  
  .header-right {
    gap: 8px;
  }
  
  .sidebar-content {
    padding: 12px;
  }
  
  .app-main {
    padding: 12px;
  }
}
</style> 
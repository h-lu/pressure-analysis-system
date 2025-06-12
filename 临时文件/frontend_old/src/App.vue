<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>压力采集数据分析系统</h1>
          <el-menu
            :default-active="$route.path"
            mode="horizontal"
            router
            class="header-menu"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/upload">数据上传</el-menu-item>
            <el-menu-item index="/analysis">数据分析</el-menu-item>
            <el-menu-item index="/reports">分析报告</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
}

.header-menu {
  background-color: transparent;
  border: none;
}

.header-menu .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
}

.header-menu .el-menu-item:hover,
.header-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.1);
  border-bottom-color: white;
  color: white;
}

.el-main {
  padding: 20px;
  min-height: calc(100vh - 60px);
}
</style> 
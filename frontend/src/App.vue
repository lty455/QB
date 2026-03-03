<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <h1>🌐 知识图谱平台</h1>
        <span class="nav-subtitle">网站数据源管理系统</span>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">网站列表</router-link>
        <router-link to="/about" class="nav-link">关于</router-link>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="footer">
      <p>© 2024 知识图谱平台 | 后端API: http://localhost:5000</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f0f2f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏样式 */
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.nav-brand h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.nav-subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 16px;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

/* 主要内容 */
.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 页脚 */
.footer {
  background-color: #fafafa;
  padding: 15px;
  text-align: center;
  border-top: 1px solid #e8e8e8;
  color: #909399;
  font-size: 14px;
  margin-top: 20px;
}
</style>
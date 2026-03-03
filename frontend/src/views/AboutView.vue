<template>
  <div class="about">
    <h1>关于知识图谱平台</h1>
    
    <el-card>
      <h2>项目概述</h2>
      <p>这是一个从500+个网站数据源爬取数据，构建知识图谱并进行可视化展示的研究生项目。</p>
      
      <h3>项目功能</h3>
      <ul>
        <li>📊 网站数据源管理</li>
        <li>🕷️ 分布式网络爬虫</li>
        <li>🧹 数据清洗与标注</li>
        <li>🗺️ 知识图谱可视化</li>
        <li>💬 基于图的RAG对话系统</li>
      </ul>
      
      <h3>技术栈</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card>
            <h4>前端</h4>
            <p>Vue 3 + Element Plus</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <h4>后端</h4>
            <p>Python Flask</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <h4>数据处理</h4>
            <p>Scrapy / BeautifulSoup</p>
          </el-card>
        </el-col>
      </el-row>
      
      <h3>使用说明</h3>
      <ol>
        <li>确保后端服务已启动 (http://localhost:5000)</li>
        <li>点击"加载网站数据"按钮获取数据</li>
        <li>可以搜索和筛选网站</li>
        <li>点击网址链接可以访问对应网站</li>
      </ol>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>

<style scoped>
.about {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #303133;
  margin-bottom: 30px;
}

h2 {
  color: #409EFF;
  margin: 20px 0 15px;
}

h3 {
  color: #606266;
  margin: 25px 0 15px;
}

h4 {
  color: #67C23A;
  margin-bottom: 10px;
}

ul, ol {
  margin-left: 20px;
  margin-bottom: 20px;
}

li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.el-row {
  margin-bottom: 20px;
}
</style>
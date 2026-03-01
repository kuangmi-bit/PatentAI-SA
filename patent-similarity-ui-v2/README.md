# PatentAI Frontend

React 前端应用，提供专利相似度分析的用户界面。

## 技术栈

- **框架**: React 18
- **构建工具**: Vite 5
- **路由**: React Router 6
- **样式**: CSS-in-JS (自定义 Design System)

## 项目结构

```
src/
├── App.jsx           # 主应用组件，包含所有页面
├── api.js            # API 客户端封装
├── api/
│   └── client.js     # 备用 API 客户端
├── hooks/
│   └── useApi.js     # API 调用 Hook
├── index.css         # 全局样式
└── main.jsx          # 应用入口
```

## 页面说明

### 1. Dashboard (首页)
- 统计概览卡片
- 快捷入口
- 最近任务列表

### 2. TaskList (分析任务)
- 任务列表（卡片/表格视图）
- 任务筛选和搜索
- 批量操作
- 创建新任务

### 3. TaskDetail (任务详情)
- 任务基本信息
- 目标专利信息
- 比对库配置
- 分析结果摘要
- 执行阶段详情
- 日志查看

### 4. NewTask (新建任务)
- 三步向导：上传专利 -> 选择库 -> 确认提交
- 文件上传和解析
- 库选择

### 5. LibraryManagement (专利库管理)
- 库列表展示
- 创建新库
- 导入专利
- 查看库详情

### 6. LibraryDetail (库详情)
- 库统计信息
- 专利列表
- 删除专利

## 组件说明

### Design Tokens
统一的设计变量定义：
```javascript
const DesignTokens = {
  colors: {
    primary: '#1e3a5f',
    success: '#059669',
    error: '#dc2626',
    warning: '#d97706',
    // ...
  },
  fonts: {
    display: '"Playfair Display", serif',
    body: '"Inter", -apple-system, sans-serif',
    mono: '"JetBrains Mono", monospace',
  },
  // ...
}
```

### 通用组件

**Button**
```jsx
<Button variant="primary" size="sm" onClick={handleClick}>
  按钮文字
</Button>
```
- variant: primary/secondary/accent/ghost
- size: sm/md/lg

**Card**
```jsx
<Card hover>
  内容
</Card>
```

**Modal**
```jsx
<Modal isOpen={show} onClose={handleClose} title="标题">
  内容
</Modal>
```

**StatusBadge**
```jsx
<StatusBadge status="completed" />
```
- status: pending/running/completed/failed

## API 调用

使用封装的 `api.js`：

```javascript
import api from './api.js'

// 获取任务列表
const tasks = await api.tasks.list()

// 创建任务
const task = await api.tasks.create({
  name: '任务名称',
  library_id: '库ID'
})

// 上传文件
const result = await api.upload.file(file)
```

## 开发指南

### 添加新页面

1. 在 `App.jsx` 创建组件
2. 添加路由配置
3. 添加到导航菜单

### 添加新 API

在 `api.js` 中添加：
```javascript
export const api = {
  // ... 现有 API
  
  newFeature: {
    list: () => fetchApi('/new-feature'),
    create: (data) => fetchApi('/new-feature', { 
      method: 'POST', 
      body: JSON.stringify(data) 
    }),
  }
}
```

## 环境变量

创建 `.env` 文件：
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 构建部署

```bash
# 开发
npm run dev

# 构建
npm run build

# 预览
npm run preview
```

## 浏览器兼容

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 已知问题

1. **大文件上传**: 超过 50MB 的文件可能导致内存问题
2. **长时间任务**: 任务执行期间页面需要保持打开
3. **移动端适配**: 部分页面在移动端显示不够优化

## 优化计划

- [ ] 添加 TypeScript 支持
- [ ] 状态管理 (Zustand/Redux)
- [ ] 组件单元测试
- [ ] PWA 支持
- [ ] 移动端适配优化

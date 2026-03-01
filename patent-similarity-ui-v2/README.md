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
├── App.jsx           # 主应用组件，包含所有页面和组件
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
- 统计概览卡片（任务数、专利数、存储空间）
- 快捷入口
- 最近任务列表

### 2. TaskList (分析任务)
- 任务列表（卡片/表格视图）
- 任务筛选和搜索
- 批量操作
- 创建新任务

### 3. TaskDetail (任务详情)
- 任务基本信息和状态
- 目标专利信息（不入库专利也可显示）
- 比对库配置
- **分析结果展示**:
  - Top 20 相似专利列表
  - 可展开的专利详情卡片
  - 四维度评分细节（技术领域、技术问题、技术方案、权利要求）
  - 相似内容高亮显示
  - 专利全文查看（摘要、权利要求书）
- 执行阶段详情

### 4. NewTask (新建任务)
- 多步骤向导：上传专利 → 提交目标专利 → 选择库 → 启动分析
- **目标专利不入库**：上传的专利仅用于分析，不保存到专利库，但**持久化到数据库**
- 支持草稿状态多次修改
- 文件上传和解析
- 库选择

### 5. LibraryManagement (专利库管理)
- 库列表展示（卡片网格）
- **创建新库**
- **重命名库**：点击"重命名"按钮修改库名称和描述
- **删除库**：点击"删除"按钮，确认后删除库及所有专利
- 导入专利（支持单文件、文件夹、压缩包）
- 实时统计（专利数、存储空间）

### 6. LibraryDetail (库详情)
- 库统计信息
- 专利列表
- 删除专利

## 主要组件说明

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

### 业务组件

**SimilarPatentCard**
相似专利详情卡片，支持展开/收起：
```jsx
<SimilarPatentCard result={similarityResult} index={0} />
```
- 头部显示：排名、标题、申请号、相似度、风险等级
- 展开后三标签页：
  - **评分详情**：四维度评分条和理由
  - **相似高亮**：匹配的文本片段高亮
  - **专利内容**：摘要和权利要求书

**LibraryPatentUpload**
专利库导入组件：
```jsx
<LibraryPatentUpload 
  library={library}
  onUpload={handleUpload}
  onClose={handleClose}
/>
```
- 三种导入模式：单文件、文件夹、压缩包
- 批量导入状态监控

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

// 提交任务（目标专利不入库）
await api.tasks.submit(task.id, {
  target_patent_info: patentInfo  // 直接传入专利信息
})

// 上传文件
const result = await api.upload.file(file)

// 批量导入压缩包
const status = await api.batchImport.uploadArchive(libraryId, archiveFile)

// 专利库管理
await api.libraries.update(libraryId, { name: '新名称' })  // 重命名
await api.libraries.delete(libraryId)  // 删除
```

## 核心功能使用流程

### 1. 创建分析任务（目标专利不入库）

```
1. 点击"新建分析任务"
2. 上传目标专利文件（PDF）
3. 系统自动解析专利信息
4. 提交目标专利（持久化到数据库，任务为草稿状态）
5. 选择比对专利库
6. 启动分析任务
7. 目标专利仅用于本次分析，不会加入专利库，但数据持久化保存
```

### 2. 查看分析结果

```
1. 进入任务详情页
2. 查看"分析结果摘要"卡片
3. 点击 Top 20 相似专利中的任意一个
4. 展开后查看：
   - 评分详情：四个维度的详细评分和理由
   - 相似高亮：匹配的文本片段
   - 专利内容：摘要和权利要求书
```

### 3. 批量导入专利

```
1. 进入专利库管理
2. 选择目标专利库
3. 点击"导入专利"
4. 选择导入方式：
   - 单文件：选择多个专利文件
   - 文件夹：选择包含专利文件的文件夹
   - 压缩包：上传 ZIP/TAR/TAR.GZ/TAR.BZ2 文件
5. 系统自动处理并显示进度
```

### 4. 管理专利库

```
重命名：
1. 在专利库卡片上点击"重命名"
2. 修改名称和描述
3. 点击"保存"

删除：
1. 在专利库卡片上点击"删除"
2. 确认对话框显示库中专利数量
3. 确认后删除库及所有专利
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

**注意**：文件夹选择功能（webkitdirectory）需要 Chrome/Edge 浏览器

## 已知问题

1. **大文件上传**: 超过 50MB 的文件可能导致内存问题
2. **长时间任务**: 任务执行期间页面需要保持打开
3. **移动端适配**: 部分页面在移动端显示不够优化
4. **文件夹选择**: 仅支持 Chrome/Edge 浏览器

## 更新日志

### v0.2.0 (2024-03-15)
- **目标专利持久化**：目标专利数据保存到数据库，支持后端重启后查看
- 任务多步骤创建流程：上传 → 提交专利 → 选库 → 启动
- 目标专利不入库分析功能
- Top 20 相似专利可展开详情
- 四维度评分细节展示
- 相似内容高亮显示
- 批量导入 V2（支持压缩包、文件夹）
- 专利库重命名和删除功能
- 存储空间实时统计

### v0.1.0 (2024-03-01)
- 基础功能实现
- 专利上传和解析
- 相似度分析
- 报告生成

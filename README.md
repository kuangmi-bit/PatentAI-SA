# PatentAI - 专利相似度分析系统

基于 AI 的专利相似度分析平台，支持专利上传、智能解析、相似度检索和报告生成。

## 功能特性

- **专利管理**: 支持 PDF、DOCX、TXT 格式专利文件上传和解析
- **智能分析**: 基于智谱 AI 的专利文本分析和特征提取
- **相似度检索**: 向量数据库支持的语义相似度检索
- **报告生成**: 自动生成 HTML 格式的相似度分析报告
- **任务管理**: 异步任务处理，支持任务状态跟踪

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.10+)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **向量数据库**: ChromaDB
- **AI 服务**: 智谱 AI (Zhipu AI)
- **任务处理**: 异步处理

### 前端
- **框架**: React 18
- **构建工具**: Vite
- **样式**: 自定义 Design System
- **路由**: React Router

## 项目结构

```
.
├── patent-similarity/
│   ├── backend/              # FastAPI 后端
│   │   ├── app/
│   │   │   ├── api/          # API 路由
│   │   │   ├── core/         # 配置和日志
│   │   │   ├── db/           # 数据库模型
│   │   │   ├── models/       # Pydantic 模型
│   │   │   └── services/     # 业务逻辑
│   │   └── init_database.py  # 数据库初始化脚本
│   └── docker-compose.yml    # Docker 编排
├── patent-similarity-ui-v2/  # React 前端
│   ├── src/
│   │   ├── App.jsx           # 主应用组件
│   │   ├── api.js            # API 客户端
│   │   └── ...
│   └── vite.config.js
└── README.md
```

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/kuangmi-bit/PatentAI-SA.git
cd PatentAI-SA
```

### 2. 后端启动

```bash
cd patent-similarity/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 ZHIPU_API_KEY

# 初始化数据库（首次运行）
python init_database.py

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 前端启动

```bash
cd patent-similarity-ui-v2

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端: http://localhost:3001
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 配置说明

### 后端配置 (.env)

```env
# API Configuration
APP_NAME="PatentAI Backend"
APP_VERSION="0.1.0"
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3001

# Zhipu AI (智谱AI) - 必填
ZHIPU_API_KEY=your_api_key_here
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPU_MODEL=glm-4
ZHIPU_EMBEDDING_MODEL=embedding-3

# File Upload
MAX_FILE_SIZE=52428800
UPLOAD_DIR=./uploads
ALLOWED_EXTENSIONS=.pdf,.docx,.txt

# Database
DATABASE_URL=sqlite+aiosqlite:///./patentai.db
```

## API 接口

### 任务管理
- `GET /tasks` - 获取任务列表
- `POST /tasks` - 创建任务
- `GET /tasks/{id}` - 获取任务详情
- `POST /tasks/{id}/submit` - 提交任务
- `POST /tasks/{id}/cancel` - 取消任务
- `DELETE /tasks/{id}` - 删除任务

### 专利库管理
- `GET /libraries` - 获取专利库列表
- `POST /libraries` - 创建专利库
- `GET /libraries/{id}` - 获取专利库详情
- `DELETE /libraries/{id}` - 删除专利库

### 文件上传
- `POST /upload/patent` - 上传专利文件
- `POST /upload/parse/{file_id}` - 解析专利文件
- `POST /upload/save` - 保存专利到库

## 开发指南

### 代码规范
- 后端: PEP 8
- 前端: ESLint + Prettier

### 提交规范
```
feat: 新功能
fix: 修复
docs: 文档
style: 格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 部署

### Docker 部署

```bash
cd patent-similarity
docker-compose up -d
```

### 生产环境注意事项
1. 修改 `.env` 中的 `DEBUG=false`
2. 使用 PostgreSQL 替代 SQLite
3. 配置 HTTPS
4. 设置适当的 CORS 域名

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系开发团队。

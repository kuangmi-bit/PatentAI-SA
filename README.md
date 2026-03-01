# PatentAI - 专利相似度分析系统

基于 AI 的专利相似度分析平台，支持专利上传、智能解析、相似度检索和报告生成。

## 功能特性

### 核心功能
- **专利管理**: 支持 PDF、DOCX、TXT 格式专利文件上传和解析
- **智能分析**: 基于智谱 AI 的专利文本分析和特征提取
- **相似度检索**: 向量数据库支持的语义相似度检索
- **报告生成**: 自动生成 HTML 格式的相似度分析报告

### 新增功能 (v0.2.0)
- **目标专利不入库分析**: 上传的目标专利仅用于分析，不保存到专利库
- **Top 20 相似专利详情**: 可展开查看每个相似专利的详细信息
  - 四维度评分（技术领域、技术问题、技术方案、权利要求）
  - 相似内容高亮显示
  - 专利全文查看（摘要、权利要求书）
- **批量导入 V2**: 支持文件夹选择、压缩包导入（ZIP/TAR/TAR.GZ/TAR.BZ2）
- **专利库管理增强**: 支持重命名、删除，实时显示存储空间

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.10+)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **向量数据库**: ChromaDB
- **AI 服务**: 智谱 AI (Zhipu AI)
- **任务处理**: 异步处理 + 后台任务

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
│   │   │   │   ├── batch_import_v2.py  # 批量导入V2
│   │   │   │   ├── libraries.py        # 专利库管理
│   │   │   │   ├── tasks.py            # 任务管理
│   │   │   │   └── upload.py           # 文件上传
│   │   │   ├── core/         # 配置和日志
│   │   │   ├── db/           # 数据库模型
│   │   │   ├── models/       # Pydantic 模型
│   │   │   └── services/     # 业务逻辑
│   │   │       ├── async_batch_import.py  # 异步批量导入
│   │   │       └── task_processor.py      # 任务处理器
│   │   └── init_database.py  # 数据库初始化脚本
│   └── docker-compose.yml    # Docker 编排
├── patent-similarity-ui-v2/  # React 前端
│   ├── src/
│   │   ├── App.jsx           # 主应用组件
│   │   │   ├── SimilarPatentCard      # 相似专利详情卡片
│   │   │   ├── LibraryPatentUpload    # 批量导入组件
│   │   │   └── LibraryManagement      # 专利库管理
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
- Chrome/Edge 浏览器（支持文件夹选择）

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

## 使用指南

### 1. 创建分析任务（目标专利不入库）

```
1. 点击"新建分析任务"
2. 上传目标专利文件（PDF）
3. 系统自动解析专利信息
4. 选择比对专利库
5. 提交任务
6. 目标专利仅用于本次分析，不会加入专利库
```

### 2. 查看相似度分析结果

```
1. 进入任务详情页
2. 查看"分析结果摘要"
3. 点击 Top 20 相似专利中的任意一个展开详情
4. 查看三标签页：
   - 评分详情：四维度详细评分和理由
   - 相似高亮：匹配的文本片段
   - 专利内容：摘要和权利要求书
```

### 3. 批量导入专利到库

```
1. 进入"专利库管理"
2. 选择目标专利库，点击"导入专利"
3. 选择导入方式：
   - 单文件：选择多个专利文件
   - 文件夹：选择包含专利文件的文件夹（Chrome/Edge）
   - 压缩包：上传 ZIP/TAR/TAR.GZ/TAR.BZ2
4. 等待处理完成
```

### 4. 管理专利库

```
重命名：
1. 在专利库卡片点击"重命名"
2. 修改名称和描述
3. 保存

删除：
1. 在专利库卡片点击"删除"
2. 确认对话框显示库中专利数量
3. 确认后删除库及所有专利（不可恢复）
```

## 配置说明

### 后端配置 (.env)

```env
# API Configuration
APP_NAME="PatentAI Backend"
APP_VERSION="0.2.0"
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
- `POST /tasks/{id}/submit` - 提交任务（支持 target_patent_info 不入库）
- `POST /tasks/{id}/cancel` - 取消任务
- `DELETE /tasks/{id}` - 删除任务

### 专利库管理
- `GET /libraries` - 获取专利库列表
- `POST /libraries` - 创建专利库
- `GET /libraries/{id}` - 获取专利库详情
- `PATCH /libraries/{id}` - 更新专利库（重命名）
- `DELETE /libraries/{id}` - 删除专利库

### 批量导入 V2
- `POST /batch/v2/import/archive/{library_id}` - 上传压缩包导入
- `GET /batch/v2/import/status/{import_id}` - 查询导入进度
- `GET /batch/v2/import/active` - 获取活动导入任务

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
5. 配置定时任务清理临时文件

## 更新日志

### v0.2.0 (2024-03-01)
- ✨ 目标专利不入库分析功能
- ✨ Top 20 相似专利可展开详情
- ✨ 四维度评分细节（技术领域、技术问题、技术方案、权利要求）
- ✨ 相似内容高亮显示
- ✨ 批量导入 V2（支持压缩包、文件夹）
- ✨ 专利库重命名和删除功能
- ✨ 存储空间实时统计

### v0.1.0 (2024-03-01)
- 🎉 基础功能实现
- 专利上传和解析
- 相似度分析
- 报告生成

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系开发团队。

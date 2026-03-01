# PatentAI Backend

FastAPI 后端服务，提供专利相似度分析的 RESTful API。

## 目录结构

```
backend/
├── app/
│   ├── api/              # API 路由层
│   │   ├── batch.py      # 批量导入
│   │   ├── batch_import_v2.py  # 批量导入V2（支持压缩包）
│   │   ├── health.py     # 健康检查
│   │   ├── libraries.py  # 专利库管理
│   │   ├── patents.py    # 专利管理
│   │   ├── tasks.py      # 任务管理
│   │   └── upload.py     # 文件上传
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   └── logging.py    # 日志配置
│   ├── db/               # 数据库
│   │   ├── database.py   # 数据库连接
│   │   └── models.py     # SQLAlchemy 模型
│   ├── models/           # Pydantic 模型
│   │   └── schemas.py    # 数据验证模型
│   ├── services/         # 业务逻辑
│   │   ├── async_batch_import.py  # 异步批量导入
│   │   ├── batch_import.py
│   │   ├── db_service.py
│   │   ├── kimi_client.py
│   │   ├── pdf_extractor.py
│   │   ├── report_generator.py
│   │   ├── task_processor.py
│   │   ├── vector_store.py
│   │   └── zhipu_client.py
│   └── main.py           # 应用入口
├── init_database.py      # 数据库初始化脚本
├── requirements.txt      # 依赖列表
└── Dockerfile           # Docker 构建
```

## 核心模块说明

### 1. API 层 (app/api/)

处理 HTTP 请求，进行参数验证，调用 Service 层。

**任务管理 (tasks.py)**
- 任务 CRUD 操作
- 任务提交/取消（支持非库内目标专利）
- 任务结果查询（包含 Top 20 相似专利详情）
- **目标专利持久化**：提交的目标专利信息保存到数据库，不依赖内存缓存

**专利库管理 (libraries.py)**
- 专利库 CRUD
- 专利库重命名和删除
- 库统计信息（专利数、存储空间）

**批量导入 (batch_import_v2.py)**
- 支持 ZIP/TAR/TAR.GZ/TAR.BZ2 压缩包
- 异步后台处理
- 进度轮询接口

**文件上传 (upload.py)**
- 文件上传和验证
- 专利解析
- 保存到库

### 2. Service 层 (app/services/)

业务逻辑实现。

**Task Processor (task_processor.py)**
```python
# 任务处理流程
1. 获取目标专利（支持库内专利或临时专利信息）
2. 特征提取和向量化
3. 相似度检索（粗排）
4. 重排序（精排）
5. 生成详细分析结果（含评分维度、高亮片段）
6. 生成报告
```

**Async Batch Import (async_batch_import.py)**
- 异步批量导入服务
- 支持压缩文件自动解压
- 实时进度更新
- 后台任务处理

**Zhipu Client (zhipu_client.py)**
- 智谱 AI API 封装
- 文本嵌入生成
- 相似度分析

**PDF Extractor (pdf_extractor.py)**
- PDF 文本提取
- 专利字段解析

**Report Generator (report_generator.py)**
- HTML 报告生成
- 图表渲染

### 3. 数据模型

**Task 模型**
```python
id: str                    # 任务ID
name: str                  # 任务名称
status: str                # 状态: pending/running/completed/failed
progress: int              # 进度 0-100
library_id: str            # 比对库ID
target_patent_id: str      # 目标专利ID（库内专利）
result: dict               # 分析结果（包含 top_results 详细数据）
stages: list               # 执行阶段
error_message: str         # 错误信息
created_at: datetime       # 创建时间
completed_at: datetime     # 完成时间
```

**Patent 模型**
```python
id: str                    # 专利ID
title: str                 # 标题
application_no: str        # 申请号
publication_no: str        # 公开号
ipc: str                   # IPC分类
abstract: str              # 摘要
claims: list               # 权利要求（JSON数组）
description: str           # 说明书
file_path: str             # 文件路径
file_size: int             # 文件大小（字节）
embedding: vector          # 特征向量
```

**TargetPatent 模型**（任务目标专利，不入库）
```python
id: str                    # 目标专利ID
task_id: str               # 关联任务ID（唯一）
title: str                 # 标题
application_no: str        # 申请号
publication_no: str        # 公开号
ipc: str                   # IPC分类
abstract: str              # 摘要
claims: list               # 权利要求（JSON数组）
description: str           # 说明书
file_path: str             # 文件路径
file_name: str             # 文件名
file_size: int             # 文件大小
embedding: vector          # 特征向量
extraction_quality: int    # 解析质量评分
created_at: datetime       # 创建时间
updated_at: datetime       # 更新时间
```

**Library 模型**
```python
id: str                    # 库ID
name: str                  # 库名称
description: str           # 描述
patent_count: int          # 专利数量
size_mb: float             # 存储大小（MB）
created_at: datetime       # 创建时间
updated_at: datetime       # 更新时间
```

**SimilarityResult 模型**
```python
id: str                    # 结果ID
task_id: str               # 任务ID
target_patent_id: str      # 目标专利ID
comparison_patent_id: str  # 比对专利ID
similarity_score: float    # 相似度分数
risk_level: str            # 风险等级
matched_features: list     # 匹配特征
analysis: str              # 分析文本
```

## 主要功能特性

### 1. 目标专利不入库分析
- 支持上传目标专利文件进行分析
- 目标专利信息**持久化存储**到 `target_patents` 表，不保存到专利库
- 支持后端重启后任务数据不丢失
- 任务可随时修改、删除，不受内存状态限制

### 2. 详细相似度分析结果
- Top 20 相似专利展示
- 四维度评分（技术领域、技术问题、技术方案、权利要求）
- 相似内容高亮显示
- 专利全文查看（摘要、权利要求）

### 3. 批量导入
- 支持文件夹选择导入
- 支持压缩包导入（ZIP/TAR/TAR.GZ/TAR.BZ2）
- 异步后台处理，支持进度轮询
- 自动过滤非专利文件

### 4. 专利库管理
- 创建、重命名、删除专利库
- 实时统计专利数量和存储空间
- 删除库时自动清理所有关联专利

## API 使用示例

### 创建分析任务（目标专利不入库）

```python
# 1. 创建任务（草稿状态）
task = await api.tasks.create({
    "name": "目标专利分析",
    "library_id": "temp"  # 临时库ID
})

# 2. 上传并解析目标专利
upload_result = await api.upload.file(pdf_file)
parse_result = await api.upload.parse(upload_result.file_id)

# 3. 提交目标专利（持久化到数据库，仍为草稿状态）
await api.tasks.submit(task.id, {
    "target_patent_info": parse_result.patent_info
})

# 4. 选择比对库
await api.tasks.update(task.id, {
    "library_id": "lib_xxx"
})

# 5. 启动分析（状态变为 queued）
await api.tasks.submit(task.id, {})
```

### 批量导入压缩包

```python
# 上传压缩包
result = await api.batchImport.uploadArchive(library_id, archive_file)
import_id = result.import_id

# 轮询进度
while True:
    status = await api.batchImport.checkStatus(import_id)
    if status.status in ["completed", "failed"]:
        break
    await asyncio.sleep(15)
```

### 专利库管理

```python
# 重命名
await api.libraries.update(library_id, {
    "name": "新名称",
    "description": "新描述"
})

# 删除（会删除库中所有专利）
await api.libraries.delete(library_id)
```

## 数据库初始化

```bash
# 首次部署时运行
python init_database.py
```

## 开发指南

### 添加新 API

1. 在 `app/api/` 创建路由文件
2. 在 `app/main.py` 注册路由
3. 在 `app/models/schemas.py` 定义模型

示例：
```python
# app/api/example.py
from fastapi import APIRouter
from app.models.schemas import ExampleRequest, ExampleResponse

router = APIRouter(prefix="/example", tags=["example"])

@router.post("", response_model=ExampleResponse)
async def create_example(request: ExampleRequest):
    # 业务逻辑
    return ExampleResponse(...)
```

### 添加新服务

1. 在 `app/services/` 创建服务文件
2. 实现业务逻辑
3. 在 API 层调用

## 测试

```bash
# 运行测试
pytest

# 运行特定测试
pytest test_full_pipeline.py
```

## 性能优化

### 数据库优化
- 添加索引: `patent.library_id`, `task.status`
- 使用连接池

### 缓存策略
- 专利向量缓存
- 任务结果缓存
- 临时专利信息缓存（任务处理器）

### 异步处理
- 文件上传异步
- 批量导入异步
- 报告生成异步

## 常见问题

### 1. 数据库锁定
SQLite 并发问题，生产环境建议使用 PostgreSQL。

### 2. 内存不足
大文件处理时可能内存不足，建议：
- 使用流式读取
- 限制文件大小
- 分页处理

### 3. API 超时
长时间任务使用异步处理，客户端轮询状态。

## 更新日志

### v0.2.0 (2024-03-15)
- **目标专利持久化存储**：新增 TargetPatentModel 表，目标专利数据持久化到数据库
- 任务生命周期管理优化：支持多步骤创建流程，草稿状态可多次修改
- 目标专利不入库分析功能
- Top 20 相似专利详情展示（可展开）
- 四维度评分细节（技术领域、技术问题、技术方案、权利要求）
- 相似内容高亮显示
- 批量导入 V2（支持压缩包、文件夹）
- 专利库重命名和删除功能
- 存储空间统计

### v0.1.0 (2024-03-01)
- 基础功能实现
- 专利上传和解析
- 相似度分析
- 报告生成

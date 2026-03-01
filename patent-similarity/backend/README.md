# PatentAI Backend

FastAPI 后端服务，提供专利相似度分析的 RESTful API。

## 目录结构

```
backend/
├── app/
│   ├── api/              # API 路由层
│   │   ├── batch.py      # 批量导入
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
- 任务提交/取消
- 任务结果查询

**专利库管理 (libraries.py)**
- 专利库 CRUD
- 库统计信息

**文件上传 (upload.py)**
- 文件上传和验证
- 专利解析
- 保存到库

### 2. Service 层 (app/services/)

业务逻辑实现。

**Task Processor (task_processor.py)**
```python
# 任务处理流程
1. 解析目标专利
2. 特征提取和向量化
3. 相似度检索（粗排）
4. 重排序（精排）
5. 生成报告
```

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
target_patent_id: str      # 目标专利ID
result: dict               # 分析结果
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
claims: str                # 权利要求
description: str           # 说明书
embedding: vector          # 特征向量
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

### 异步处理
- 文件上传异步
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

### v0.1.0 (2024-03-01)
- 基础功能实现
- 专利上传和解析
- 相似度分析
- 报告生成

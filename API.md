# PatentAI API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **Content-Type**: `application/json`

## 认证

目前版本暂未实现认证，后续将添加 JWT Token 认证。

## 任务管理

### 获取任务列表

```http
GET /tasks
```

**Query Parameters:**
- `status` (可选): 筛选状态 (pending/running/completed/failed)
- `library_id` (可选): 筛选库
- `search` (可选): 搜索关键词
- `skip` (可选): 跳过数量，默认 0
- `limit` (可选): 返回数量，默认 20

**Response:**
```json
{
  "total": 100,
  "items": [
    {
      "id": "task_id",
      "name": "任务名称",
      "status": "completed",
      "progress": 100,
      "created_at": "2024-03-01T08:00:00",
      "library_id": "lib_id",
      "target_patent": { ... }
    }
  ]
}
```

### 创建任务

```http
POST /tasks
```

**Request Body:**
```json
{
  "name": "任务名称",
  "library_id": "库ID"
}
```

**Response:**
```json
{
  "id": "task_id",
  "name": "任务名称",
  "status": "draft",
  "progress": 0,
  "library_id": "库ID",
  "created_at": "2024-03-01T08:00:00"
}
```

### 获取任务详情

```http
GET /tasks/{task_id}
```

**Response:**
```json
{
  "id": "task_id",
  "name": "任务名称",
  "status": "completed",
  "progress": 100,
  "library_id": "lib_id",
  "target_patent": {
    "title": "专利标题",
    "application_no": "申请号",
    "publication_no": "公开号",
    "ipc": "IPC分类",
    "applicant": "申请人",
    "inventors": ["发明人1"],
    "abstract": "摘要",
    "claims": ["权利要求1"],
    "description": "说明书",
    "extraction_quality": 95
  },
  "stages": [...],
  "result": { ... },
  "created_at": "2024-03-01T08:00:00",
  "completed_at": "2024-03-01T08:05:00"
}
```

**说明:**
- `target_patent` 从数据库加载，支持后端重启后查看
- 目标专利信息持久化存储，不随内存缓存丢失

### 提交任务（支持目标专利持久化）

```http
POST /tasks/{task_id}/submit
```

**Request Body:**
```json
{
  "target_patent_info": {
    "title": "专利标题",
    "application_no": "申请号",
    "publication_no": "公开号",
    "ipc": "IPC分类",
    "applicant": "申请人",
    "inventors": ["发明人1", "发明人2"],
    "abstract": "摘要",
    "claims": ["权利要求1", "权利要求2"],
    "description": "说明书",
    "extraction_quality": 95
  }
}
```

**说明:**
- 提供 `target_patent_info`：将目标专利持久化到数据库，任务保持 draft 状态
- 不提供 `target_patent_info`：启动分析任务，状态变为 queued/running

**Response:** 任务对象

### 取消任务

```http
POST /tasks/{task_id}/cancel
```

**Response:** 任务对象

### 删除任务

```http
DELETE /tasks/{task_id}
```

**Response:** 204 No Content

## 专利库管理

### 获取库列表

```http
GET /libraries
```

**Response:**
```json
[
  {
    "id": "lib_id",
    "name": "库名称",
    "description": "描述",
    "patent_count": 100,
    "size_mb": 50.5,
    "created_at": "2024-03-01T08:00:00"
  }
]
```

### 创建库

```http
POST /libraries
```

**Request Body:**
```json
{
  "name": "库名称",
  "description": "描述"
}
```

### 获取库详情

```http
GET /libraries/{library_id}
```

### 删除库

```http
DELETE /libraries/{library_id}
```

## 专利管理

### 获取专利列表

```http
GET /patents?library_id={library_id}
```

**Query Parameters:**
- `library_id` (可选): 筛选库

**Response:**
```json
[
  {
    "id": "patent_id",
    "title": "专利标题",
    "application_no": "申请号",
    "publication_no": "公开号",
    "ipc": "IPC分类",
    "abstract": "摘要",
    "library_id": "库ID",
    "created_at": "2024-03-01T08:00:00"
  }
]
```

### 删除专利

```http
DELETE /patents/{patent_id}
```

## 文件上传

### 上传文件

```http
POST /upload/patent
Content-Type: multipart/form-data
```

**Request Body:**
- `file`: 文件 (PDF/DOCX/TXT)

**Response:**
```json
{
  "file_id": "file_id",
  "file_name": "文件名.pdf",
  "file_size": 1024000,
  "file_path": "./uploads/file_id.pdf",
  "uploaded_at": "2024-03-01T08:00:00"
}
```

### 解析文件

```http
POST /upload/parse/{file_id}
```

**Response:**
```json
{
  "file_id": "file_id",
  "patent_info": {
    "title": "专利标题",
    "application_no": "申请号",
    "publication_no": "公开号",
    "ipc": "IPC分类",
    "abstract": "摘要",
    "claims": ["权利要求1", "权利要求2"],
    "description": "说明书"
  },
  "quality_score": 95,
  "parsing_time": 2.5
}
```

### 保存到库

```http
POST /upload/save
```

**Request Body:**
```json
{
  "file_id": "file_id",
  "library_id": "库ID",
  "patent_info": {
    "title": "专利标题",
    "application_no": "申请号",
    "publication_no": "公开号",
    "ipc": "IPC分类",
    "abstract": "摘要",
    "claims": ["权利要求1"],
    "description": "说明书"
  },
  "quality_score": 95
}
```

## 批量导入

### JSON 批量导入

```http
POST /batch/import/json/{library_id}
```

**Request Body:**
```json
{
  "patents": [
    {
      "title": "专利1",
      "application_no": "CN202310000001"
    }
  ],
  "generate_embeddings": true
}
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 验证错误 |
| 500 | 服务器内部错误 |

## 错误响应格式

```json
{
  "detail": "错误信息"
}
```

## 限流

目前版本暂未实现限流，后续将添加：
- 每分钟 100 次请求
- 上传文件大小限制 50MB

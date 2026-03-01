# 更新日志

所有 notable 的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 用户认证系统（计划中）
- 任务批量操作（计划中）
- 报告导出 PDF 功能（计划中）

## [0.2.0] - 2024-03-15

### Added
- **目标专利持久化存储**
  - 新增 `TargetPatentModel` 数据库表，独立存储任务的目标专利信息
  - 目标专利数据持久化到数据库，不再依赖内存缓存
  - 支持后端重启后任务数据不丢失
  - 任务可随时修改、删除，不受内存状态限制

- **任务生命周期管理优化**
  - 支持多步骤任务创建流程（创建 → 提交目标专利 → 选择库 → 启动分析）
  - 任务草稿状态支持多次修改
  - 目标专利与库选择解耦，可独立操作

- **API 增强**
  - `POST /tasks/{id}/submit` 支持持久化目标专利信息
  - `GET /tasks/{id}` 自动从数据库加载目标专利详情
  - 新增 `extraction_quality` 字段记录专利解析质量

### Changed
- 目标专利存储方式从内存缓存改为数据库持久化
- `task_to_response` 函数改为异步，支持数据库查询

### Technical Details
- 数据库：新增 `target_patents` 表，与 `tasks` 表一对一关联
- 服务层：新增 `TargetPatentService` 提供 CRUD 操作
- 约束：`task_id` 字段唯一约束，确保一个任务只有一个目标专利

## [0.1.0] - 2024-03-01

### Added
- 基础架构搭建
  - FastAPI 后端框架
  - React + Vite 前端框架
  - SQLite 数据库
  - ChromaDB 向量数据库

- 专利管理功能
  - 专利库 CRUD
  - 专利文件上传（PDF/DOCX/TXT）
  - 专利解析和信息提取
  - 批量导入专利

- 相似度分析功能
  - 基于智谱 AI 的文本嵌入
  - 向量相似度检索
  - 重排序优化
  - 相似度分析报告生成

- 任务管理功能
  - 分析任务创建和提交
  - 异步任务处理
  - 任务状态跟踪
  - 执行日志查看

- 前端界面
  - 响应式布局设计
  - 任务列表/详情页面
  - 专利库管理页面
  - 新建分析向导
  - 分析结果展示

- 部署支持
  - Docker 容器化
  - Docker Compose 编排
  - 环境变量配置

### Technical Details
- 后端：Python 3.10+, FastAPI, SQLAlchemy 2.0
- 前端：React 18, Vite 5, React Router 6
- AI：智谱 AI (GLM-4, Embedding-3)
- 数据库：SQLite (开发), PostgreSQL ready (生产)

[Unreleased]: https://github.com/kuangmi-bit/PatentAI-SA/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kuangmi-bit/PatentAI-SA/releases/tag/v0.1.0

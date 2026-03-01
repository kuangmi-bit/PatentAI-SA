# 开发规范

## Git 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链

### 示例

```bash
# 新功能
feat(tasks): add batch delete task API

# 修复
fix(upload): resolve PDF parsing error for large files

# 文档
docs(api): update task management API documentation

# 重构
refactor(services): extract common AI client logic
```

## 代码规范

### Python (后端)

遵循 PEP 8 规范：

```python
# 命名规范
class TaskService:          # 类名: 大驼峰
    def create_task(self):  # 方法: 小写下划线
        pass

def process_task():         # 函数: 小写下划线
    pass

task_id = "xxx"            # 变量: 小写下划线
MAX_RETRY = 3              # 常量: 大写下划线

# 文档字符串
def create_task(name: str, library_id: str) -> Task:
    """
    创建分析任务
    
    Args:
        name: 任务名称
        library_id: 专利库ID
        
    Returns:
        创建的任务对象
        
    Raises:
        HTTPException: 当库不存在时
    """
    pass
```

### JavaScript/React (前端)

```javascript
// 组件命名: 大驼峰
function TaskDetail() {
  // 状态: 小驼峰
  const [taskList, setTaskList] = useState([])
  
  // 函数: 小驼峰
  const handleSubmit = async () => {
    // ...
  }
  
  return (
    // JSX...
  )
}

// 常量: 大写下划线
const API_BASE_URL = 'http://localhost:8000'
const MAX_FILE_SIZE = 50 * 1024 * 1024
```

## 目录结构规范

```
backend/
├── app/
│   ├── api/          # 路由层
│   ├── core/         # 核心配置
│   ├── db/           # 数据库
│   ├── models/       # 数据模型
│   └── services/     # 业务逻辑
├── tests/            # 测试文件
└── scripts/          # 工具脚本

frontend/
├── src/
│   ├── components/   # 通用组件
│   ├── pages/        # 页面组件
│   ├── hooks/        # 自定义 Hooks
│   ├── utils/        # 工具函数
│   └── api/          # API 封装
└── public/           # 静态资源
```

## 分支管理

采用 Git Flow 简化版：

```
main        # 生产分支
  ↑
develop     # 开发分支
  ↑
feature/*   # 功能分支
  ↑
fix/*       # 修复分支
```

### 工作流程

1. 从 `develop` 创建功能分支
2. 开发完成后提交 PR 到 `develop`
3. 测试通过后合并到 `main`

## 代码审查清单

### 后端

- [ ] 错误处理完善
- [ ] 日志记录适当
- [ ] 数据库连接正确关闭
- [ ] 敏感信息不泄露
- [ ] API 响应格式一致

### 前端

- [ ] 组件复用性
- [ ] 状态管理清晰
- [ ] 错误边界处理
- [ ] 加载状态显示
- [ ] 响应式布局

## 测试要求

### 单元测试

```python
# 后端示例
def test_create_task():
    task = TaskService.create_task("测试任务", "lib_id")
    assert task.name == "测试任务"
    assert task.status == "pending"
```

```javascript
// 前端示例
test('TaskList renders correctly', () => {
  render(<TaskList />)
  expect(screen.getByText('分析任务')).toBeInTheDocument()
})
```

### 集成测试

- API 端到端测试
- 关键业务流程测试

## 文档更新

修改代码时同步更新：

- [ ] API 文档 (API.md)
- [ ] 部署文档 (DEPLOY.md)
- [ ] 代码注释
- [ ] CHANGELOG.md

## 版本发布

遵循 [Semantic Versioning](https://semver.org/)：

```
主版本.次版本.修订号
1.0.0
```

- 主版本: 不兼容的 API 修改
- 次版本: 向下兼容的功能新增
- 修订号: 向下兼容的问题修复

## 安全问题

发现安全问题请：
1. 不要公开讨论
2. 发送邮件至维护者
3. 等待修复后公开

## 联系方式

- Issue: GitHub Issues
- Email: 维护者邮箱

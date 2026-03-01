# PatentAI 部署指南

## 部署方式

### 方式一：Docker Compose（推荐）

#### 1. 环境准备

- Docker 20.10+
- Docker Compose 2.0+

#### 2. 部署步骤

```bash
# 1. 克隆代码
git clone https://github.com/kuangmi-bit/PatentAI-SA.git
cd PatentAI-SA/patent-similarity

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，设置 ZHIPU_API_KEY

# 3. 启动服务
docker-compose up -d

# 4. 初始化数据库
docker-compose exec backend python init_database.py

# 5. 查看日志
docker-compose logs -f
```

#### 3. 访问服务

- 前端: http://localhost:3001
- 后端 API: http://localhost:8000

### 方式二：手动部署

#### 后端部署

```bash
# 1. 进入后端目录
cd patent-similarity/backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 初始化数据库（首次）
python init_database.py

# 6. 启动服务
# 开发模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 前端部署

```bash
# 1. 进入前端目录
cd patent-similarity-ui-v2

# 2. 安装依赖
npm install

# 3. 开发模式
npm run dev

# 4. 生产构建
npm run build

# 5. 预览生产构建
npm run preview
```

### 方式三：生产环境部署

#### 使用 Nginx 反向代理

```nginx
# /etc/nginx/sites-available/patentai
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /var/www/patentai/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 使用 systemd 管理服务

```ini
# /etc/systemd/system/patentai-backend.service
[Unit]
Description=PatentAI Backend
After=network.target

[Service]
Type=simple
User=patentai
WorkingDirectory=/opt/patentai/backend
Environment=PATH=/opt/patentai/backend/venv/bin
ExecStart=/opt/patentai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl enable patentai-backend
sudo systemctl start patentai-backend
sudo systemctl status patentai-backend
```

## 数据库迁移

### 从 SQLite 迁移到 PostgreSQL

```bash
# 1. 安装依赖
pip install psycopg2-binary

# 2. 修改 .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/patentai

# 3. 重新初始化数据库
python init_database.py
```

## SSL/HTTPS 配置

### 使用 Let's Encrypt

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 监控与日志

### 日志位置

- 后端日志: `backend/logs/`
- Nginx 日志: `/var/log/nginx/`
- Docker 日志: `docker-compose logs`

### 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health

# 完整健康检查
curl http://localhost:8000/health/detail
```

## 备份策略

### 数据库备份

```bash
# SQLite 备份
cp patentai.db patentai.db.backup.$(date +%Y%m%d)

# PostgreSQL 备份
pg_dump patentai > patentai_backup_$(date +%Y%m%d).sql
```

### 文件备份

```bash
# 上传文件备份
tar -czvf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# 报告备份
tar -czvf reports_backup_$(date +%Y%m%d).tar.gz reports/
```

## 故障排查

### 服务无法启动

```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 查看日志
docker-compose logs backend
tail -f backend/logs/app.log
```

### 数据库连接失败

```bash
# 检查数据库文件权限
ls -la patentai.db

# 测试连接
python -c "from app.db.database import init_db; init_db()"
```

### 内存不足

```bash
# 查看内存使用
free -h

# 限制 Docker 内存
docker-compose up -d --memory=2g
```

## 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 3. 更新前端
cd ../patent-similarity-ui-v2
npm install
npm run build

# 4. 重启服务
sudo systemctl restart patentai-backend
```

## 安全建议

1. **修改默认配置**
   - 更改默认端口
   - 使用强密码
   - 启用 HTTPS

2. **访问控制**
   - 配置防火墙
   - 限制 IP 访问
   - 添加身份认证

3. **数据保护**
   - 定期备份
   - 加密敏感数据
   - 日志脱敏

# APM 平台部署手册

## 环境要求

### 1. 硬件要求

| 规格 | CPU | 内存 | 磁盘 | 说明 |
|------|-----|------|------|------|------|
| 小规模 | 8 核 | 16GB | 500GB | 支持 1000 日活 |
| 中规模 | 16 核 | 32GB | 1TB | 支持 10000 日活 |
| 大规模 | 32 核 | 64GB | 2TB | 支持 50000+ 日活 |

### 2. 软件要求

| 组件 | 版本 | 说明 |
|------|------|------|
| 操作系统 | CentOS 7.9+ / Ubuntu 20.04+ | 64 位 |
| Docker | 20.10+ | 容器运行时 |
| Docker Compose | 2.0+ | 编排工具 |
| MySQL | 5.7+ | 数据库 |
| Redis | 6.0+ | 缓存 |

### 3. 网络要求

- 开放端口：80, 443, 22, 3306, 6379
- 网络互通：内网可达
- DNS：配置正向解析

---

## 部署步骤

### Step 1: 环境检查

```bash
# 检查系统版本
cat /etc/os-release

# 检查 CPU/内存
free -h
nproc

# 检查磁盘
df -h

# 检查 Docker
docker --version
docker-compose --version

# 检查网络
ping -c 2 apm.example.com
```

### Step 2: 创建目录

```bash
# 创建安装目录
mkdir -p /opt/apm/{data,logs,config}

# 创建数据目录
mkdir -p /opt/apm/data/{mysql,redis,es}
```

### Step 3: 配置文件

```bash
# 复制配置模板
cp config/env.example config/.env

# 编辑配置文件
vi config/.env
```

配置项说明：
```
# MySQL 配置
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=apm
MYSQL_USER=apm
MYSQL_PASSWORD=apm_password

# Redis 配置
REDIS_PASSWORD=redis_password

# 应用配置
APP_ENV=production
APP_PORT=8080
```

### Step 4: 启动服务

```bash
cd /opt/apm

# 拉取镜像
docker-compose pull

# 启动服务
docker-compose up -d

# 检查状态
docker-compose ps
```

### Step 5: 验证部署

```bash
# 检查容器状态
docker-compose ps

# 检查日志
docker-compose logs -f

# 检查端口
netstat -tlnp | grep -E '80|8080|3306|6379'

# 访问测试
curl http://localhost:8080/health
```

---

## Docker Compose 配置

### 1. docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:5.7
    container_name: apm-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - ./data/mysql:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - apm-network

  redis:
    image: redis:6.0
    container_name: apm-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    networks:
      - apm-network

  app:
    image: apm-app:latest
    container_name: apm-app
    restart: always
    depends_on:
      - mysql
      - redis
    environment:
      MYSQL_HOST: mysql
      REDIS_HOST: redis
    ports:
      - "8080:8080"
    networks:
      - apm-network

  nginx:
    image: nginx:alpine
    container_name: apm-nginx
    restart: always
    depends_on:
      - app
    volumes:
      - ./config/nginx.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
      - "443:443"
    networks:
      - apm-network

networks:
  apm-network:
    driver: bridge
```

### 2. nginx.conf

```nginx
upstream backend {
    server app:8080;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## K8S 部署（可选）

### 1. Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apm-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: apm-app
  template:
    metadata:
      labels:
        app: apm-app
    spec:
      containers:
      - name: apm-app
        image: apm-app:latest
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "1"
            memory: "2Gi"
```

### 2. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: apm-app
spec:
  selector:
    app: apm-app
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 3. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: apm-ingress
spec:
  rules:
  - host: apm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: apm-app
            port:
              number: 80
```

---

## 日常运维

### 1. 启动/停止

```bash
# 启动
docker-compose start

# 停止
docker-compose stop

# 重启
docker-compose restart
```

### 2. 查看日志

```bash
# 所有日志
docker-compose logs -f

# 指定服务
docker-compose logs -f app

# 最近 100 行
docker-compose logs --tail=100 app
```

### 3. 数据备份

```bash
# MySQL 备份
docker exec apm-mysql mysqldump -u apm -p apm > backup_$(date +%Y%m%d).sql

# Redis 备份
docker exec apm-redis redis-cli -a password SAVE
```

### 4. 版本升级

```bash
# 拉取新镜像
docker-compose pull

# 重新启动
docker-compose up -d

# 回滚（如需）
docker-compose rollback
```

---

## 健康检查

### 1. 接口检查

```bash
# 应用健康检查
curl http://localhost:8080/health

# 数据库检查
docker exec apm-mysql mysqladmin ping -u root -p

# Redis 检查
docker exec apm-redis redis-cli -a password ping
```

### 2. 脚本检查

```bash
#!/bin/bash
# health_check.sh

# 检查应用
if curl -s http://localhost:8080/health > /dev/null; then
    echo "APP: OK"
else
    echo "APP: FAIL"
fi

# 检查 MySQL
if docker exec apm-mysql mysqladmin ping -u root -p${MYSQL_ROOT_PASSWORD} > /dev/null 2>&1; then
    echo "MySQL: OK"
else
    echo "MySQL: FAIL"
fi

# 检查 Redis
if docker exec apm-redis redis-cli -a ${REDIS_PASSWORD} ping > /dev/null 2>&1; then
    echo "Redis: OK"
else
    echo "Redis: FAIL"
fi
```

---

## 常见问题

### Q1: 启动失败？
**A**: 检查日志 `docker-compose logs`，确认端口是否被占用，配置文件是否正确。

### Q2: 无法访问？
**A**: 检查防火墙 `firewall-cmd --list-ports`，检查安全组规则。

### Q3: 性能差？
**A**: 检查资源使用，调整 Docker 资源配置，增加内存/CPU。

### Q4: 数据丢失风险？
**A**: 确认数据目录挂载是否正确，定期备份。
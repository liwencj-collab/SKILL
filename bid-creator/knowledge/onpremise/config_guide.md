# 私有化部署配置清单

## 系统配置参数

### 1. JVM 参数

```bash
# 标准配置
-Xms4g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:+UseCGroupMemoryLimitForHeap

# 高性能配置
-Xms8g -Xmx8g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:+ParallelRefProcEnabled
-XX:-OopsNGedenPeriod=0
```

### 2. 数据库配置

```sql
-- MySQL 优化配置
max_connections = 2000
innodb_buffer_pool_size = 8G
innodb_log_file_size = 1G
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT

-- 连接池配置
min-idle = 10
max-idle = 50
max-active = 100
```

### 3. Redis 配置

```conf
# 内存配置
maxmemory 8gb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1
save 300 10
save 60 10000

# 集群配置
cluster-enabled yes
cluster-node-timeout 15000
```

### 4. Nginx 配置

```nginx
# 负载均衡配置
upstream backend {
    server 10.1.1.1:8080;
    server 10.1.1.2:8080;
    server 10.1.1.3:8080;
}

# 超时配置
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

### 5. Elasticsearch 配置

```yaml
# 集群配置
cluster.name: apm-cluster
node.name: node-1
path.data: /data/es
path.logs: /logs/es

# 内存配置
indices.memory	index_buffer_size: 30%
indices.queries.cache.size: 20%
```

---

## 端口配置

### 1. 组件端口

| 组件 | 端口 | 说明 |
|------|------|------|
| Nginx | 80/443 | HTTP/HTTPS |
| Gateway | 8080 | API 网关 |
| Web | 8081 | Web 服务 |
| Admin | 8082 | 管理后台 |
| MySQL | 3306 | 数据库 |
| Redis | 6379 | 缓存 |
| ES | 9200/9300 | 搜索/通信 |
| Kafka | 9092 | 消息 |
| Zookeeper | 2181 | 注册中心 |

### 2. 运维端口

| 组件 | 端口 | 说明 |
|------|------|------|
| Prometheus | 9090 | 监控 |
| Grafana | 3000 | 可视化 |
| Portainer | 9000 | 容器管理 |
| Jenkins | 8080 | CI/CD |

---

## 安全配置

### 1. 防火墙规则

```bash
# 只开放必要端口
-A INPUT -p tcp --dport 80 -j ACCEPT
-A INPUT -p tcp --dport 443 -j ACCEPT
-A INPUT -p tcp --dport 22 -j ACCEPT
-A INPUT -j DROP
```

### 2. SSL 证书配置

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/server.crt;
    ssl_certificate_key /etc/ssl/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256;
}
```

### 3. 敏感数据配置

- 数据库密码：强密码策略
- API Key：定期轮换
- 密钥：分开存储
- 日志：脱敏处理
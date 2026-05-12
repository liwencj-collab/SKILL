# 平台悟空架构图和应急预案

本文档包含平台悟空的架构图和应急预案，作为 `SKILL.md` 的补充。

## 目录

- [架构图](#架构图)
- [应急预案](#应急预案)
- [故障排查流程](#故障排查流程)
- [常用命令速查](#常用命令速查)

---

## 架构图

### 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        用户访问                             │
└─────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      负载均衡层                            │
│                   (Nginx / SLB)                           │
└─────────────────────┬───────────────────────────────────────┘
                     │
         ┌──────────┴──────────┐
         ▼                     ▼
┌───────────────┐      ┌───────────────┐
│   Web集群1   │      │   Web集群2   │
└───────┬───────┘      └───────┬───────┘
        │                    │
        ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      应用服务层                            │
│              (Kubernetes 集群)                           │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│  │ API 1  │  │ API 2  │  │ API 3  │  │ API 4  │        │
│  └────────┘  └────────┘  └────────┘  └────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层                               │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│    │  MySQL   │  │ Redis   │  │  ES     │          │
│    │ 主从集群 │  │ 集群   │  │ 集群    │          │
│    └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### K8s 集群架构

```
┌────────────────────────────────────────────���────────────────┐
│                    K8s 控制平面                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ kube-   │  │ kube-   │  │ etcd    │              │
│  │ apiserver│  │ controller│ │ 集群   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────┼───────────────────────────────────────┐
│                    ▼                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Node 1  │  │ Node 2  │  │ Node 3  │  ...         │
│  │(master)│  │(worker) │  │(worker) │              │
│  └────────┘  └────────┘  └────────┘              │
└─────────────────────────────────────────────────────┘
```

### 网络架构

```
┌─────────────────────────────────────────────────────────────┐
│                      外网                                │
└─────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   防火墙 / WAF                          │
└─────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  负载均衡器 (SLB)                        │
└─────────────────────┬───────────────────────────────────────┘
                     │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Node 1 │ │ Node 2 │ │ Node 3│
    │ Ingress│ │ Ingress│ │ Ingress│
    └────────┘ └────────┘ └────────┘
```

---

## 应急预案

### 1. 服务不可用应急预案

#### 1.1 Web服务无法访问

**触发条件**：用户报告网站打不开、返回502/504错误

**排查步骤**：
```
1. 确认问题范围
   - 是全部用户还是部分用户？
   - 是移动端还是PC端？
   - 有没有特定时间段？

2. 检查基础设施
   $ ping <服务器IP>           # 网络连通性
   $ curl -v <URL>           # 确认返回状态码
   $ telnet <IP> 80         # 端口连通性

3. 检查服务状态
   $ systemctl status nginx   # Nginx状态
   $ systemctl status <应用>  # 应用服务状态

4. 检查后端服务
   $ docker ps              # 容器状态
   $ kubectl get pods       # Pod状态

5. 检查日志
   $ journalctl -u nginx -n 50
   $ kubectl logs <pod>
```

**恢复操作**：
```
# 重启Nginx
$ systemctl restart nginx

# 重启应用
$ kubectl rollout restart deployment/<应用名>

# 回滚版本
$ kubectl rollout undo deployment/<应用名>
```

#### 1.2 API服务异常

**触发条件**：API返回错误、响应慢、超时

**排查步骤**：
```
1. 检查API状态
   $ kubectl get pods -n <命名空间>
   $ kubectl describe pod <pod名>

2. 检查资源使用
   $ kubectl top pods
   $ kubectl top nodes

3. 检查日志
   $ kubectl logs <pod> --tail=100

4. 检查健康检查
   $ kubectl describe pod <pod> | grep -A 10 "Liveness"

5. 检查后端依赖
   $ kubectl exec -it <pod> -- ping <依赖服务>
   $ kubectl exec -it <pod> -- nslookup <服务名>
```

### 2. 数据库应急预案

#### 2.1 MySQL无法连接

**触发条件**：应用报数据库连接错误

**排查步骤**：
```
1. 检查MySQL状态
   $ systemctl status mysql
   $ docker ps | grep mysql

2. 检查连接数
   $ mysql -u root -p -e "show processlist;"

3. 检查慢查询
   $ mysql -u root -p -e "show full processlist;"

4. 检查锁
   $ mysql -u root -p -e "show engine innodb status;"
```

**恢复操作**：
```
# 重启MySQL
$ systemctl restart mysql

# 杀掉阻塞连接
$ mysql -u root -p -e "KILL <connection_id>;"
```

#### 2.2 Redis无法连接

**触发条件**：缓存服务不可用

**排查步骤**：
```
1. 检查Redis状态
   $ redis-cli ping
   $ redis-cli info

2. 检查内存
   $ redis-cli info memory

3. 检查连接数
   $ redis-cli info clients
```

### 3. Kubernetes应急预案

#### 3.1 Pod一直重启

**触发步骤**：
```
1. 查看Pod状态
   $ kubectl get pods -n <命名空间>

2. 查看事件
   $ kubectl describe pod <pod名>

3. 查看之前日志
   $ kubectl logs --previous <pod名>

4. 检查资源限制
   $ kubectl get pod <pod名> -o jsonpath='{.spec.containers[*].resources}'
```

#### 3.2 Node节点不可用

**触发步骤**：
```
1. 检查Node状态
   $ kubectl get nodes

2. 检查Node详情
   $ kubectl describe node <node名>

3. 驱逐Pod
   $ kubectl drain <node名> --ignore-daemonsets --delete-emptydir
```

#### 3.3 PVC无法挂载

**触发步骤**：
```
1. 检查PVC状态
   $ kubectl get pvc

2. 检查PV
   $ kubectl get pv

3. 检查存储后端
   $ kubectl describe pv <pv名>
```

### 4. 网络应急预案

#### 4.1 服务无法访问

**排查命令**：
```
# 网络连通性
$ ping <IP>
$ curl -v <URL>
$ telnet <IP> <端口>

# DNS解析
$ nslookup <域名>
$ dig <域名>

# 路由检查
$ traceroute <IP>
$ mtr <IP>

# 端口检查
$ netstat -tlnp
$ ss -tlnp
```

#### 4.2 DNS解析失败

**排查命令**：
```
$ cat /etc/resolv.conf
$ nslookup <域名>
$ dig <域名>
$ systemd-resolve --status
```

---

## 故障排查流程

### 通用流程

```
┌─────────────┐
│  1. 收集   │  ← 问题现象、时间、错误信息
└──────┬──────┘
       ▼
┌─────────────┐
│  2. 定位  │  ← 服务状态、资源、网络
└──────┬──────┘
       ▼
┌─────────────┐
│  3. 分析  │  ← 日志、配置、依赖
└──────┬──────┘
       ▼
┌─────────────┐
│  4. 解决  │  ← 重启、回滚���修���
└──────┬──────┘
       ▼
┌─────────────┐
│  5. 验证  │  ← 确认问题已解决
└─────────────┘
```

---

## 常用命令速查

### 服务管理

| 命令 | 说明 |
|------|------|
| `systemctl status <服务>` | 查看服务状态 |
| `systemctl restart <服务>` | 重启服务 |
| `journalctl -u <服务> -f` | 查看实时日志 |
| `netstat -tlnp` | 查看端口 |

### Docker

| 命令 | 说明 |
|------|------|
| `docker ps -a` | 查看所有容器 |
| `docker logs -f <容器>` | 查看容器日志 |
| `docker exec -it <容器> /bin/bash` | 进入容器 |
| `docker stats` | 查看资源使用 |

### Kubernetes

| 命令 | 说明 |
|------|------|
| `kubectl get pods` | 查看Pod |
| `kubectl get pods -n <ns>` | 查看指定命名空间 |
| `kubectl describe pod <pod>` | Pod详情 |
| `kubectl logs <pod>` | 查看日志 |
| `kubectl logs -f <pod>` | 实时日志 |
| `kubectl exec -it <pod> -- /bin/bash` | 进入容器 |
| `kubectl get nodes` | 查看节点 |
| `kubectl get svc` | 查看服务 |
| `kubectl get ingress` | 查看入口 |
| `kubectl get pvc` | 查看存储 |
| `kubectl top pods` | 资源使用 |
| `kubectl rollout status deployment/<name>` | 部署状态 |
| `kubectl rollout undo deployment/<name>` | 回滚 |

### 日志分析

| 命令 | 说明 |
|------|------|
| `tail -f <日志>` | 实时日志 |
| `grep -i error <日志>` | 搜索错误 |
| `grep -A 5 "关键字" <日志>` | 上下文 |
| `sed -n '/时间/,/时间/p' <日志>` | 时间段 |

### 网络

| 命令 | 说明 |
|------|------|
| `ping <IP>` | 连通性 |
| `curl -v <URL>` | HTTP检查 |
| `nslookup <域名>` | DNS检查 |
| `traceroute <IP>` | 路由追踪 |
# APM 专业术语表

## 监控领域术语

| 术语 | 英文 | 说明 |
|------|------|------|
| APM | Application Performance Management | 应用性能管理 |
| RUM | Real User Monitoring | 真实用户监控 |
| SPA | Single Page Application | 单页面应用 |
| TTFB | Time To First Byte | 首字节时间 |
| TTI | Time To Interactive | 可交互时间 |
| FCP | First Contentful Paint | 首次内容绘制 |
| LCP | Largest Contentful Paint | 最大内容绘制 |
| CLS | Cumulative Layout Shift | 累计布局偏移 |
| FID | First Input Delay | 首次输入延迟 |
| FPS | Frames Per Second | 帧率 |
| DNS | Domain Name System | 域名系统 |
| TCP | Transmission Control Protocol | 传输控制协议 |
| SSL/TLS | Secure Sockets Layer | 安全套接层 |
| CDN | Content Delivery Network | 内容分发网络 |
| API | Application Programming Interface | 应用程序接口 |
| SDK | Software Development Kit | 软件开发包 |
| Agent | Agent | 探针/代理 |

---

## 性能指标术语

| 术语 | 英文 | 说明 |
|------|------|------|
| RT | Response Time | 响应时间 |
| QPS | Queries Per Second | 每秒请求数 |
| TPS | Transactions Per Second | 每秒事务数 |
| ApDex | Application Performance Index | 应用性能指数 |
| SLA | Service Level Agreement | 服务等级协议 |
| RTO | Recovery Time Objective | 恢复时间目标 |
| RPO | Recovery Point Objective | 恢复点目标 |
| MTBF | Mean Time Between Failures | 平均故障间隔时间 |
| MTTR | Mean Time To Recover | 平均恢复时间 |
| P50 | 50th Percentile | 50 百分位 |
| P90 | 90th Percentile | 90 百分位 |
| P95 | 95th Percentile | 95 百分位 |
| P99 | 99th Percentile | 99 百分位 |
| P999 | 99.9th Percentile | 99.9 百分位 |

---

## 技术架构术语

| 术语 | 英文 | 说明 |
|------|------|------|
| JVM | Java Virtual Machine | Java 虚拟机 |
| GC | Garbage Collection | 垃圾回收 |
| OOM | Out Of Memory | 内存溢出 |
| Thread Pool | Thread Pool | 线程池 |
| Connection Pool | Connection Pool | 连接池 |
| Load Balancing | Load Balancing | 负载均衡 |
| HA | High Availability | 高可用 |
| Cluster | Cluster | 集群 |
| Primary-Replica | Primary-Replica | 主从 |
| Sharding | Sharding | 分片 |
| Replication | Replication | 复制 |
| Failover | Failover | 故障转移 |
| Circuit Breaker | Circuit Breaker | 熔断器 |
| Rate Limiting | Rate Limiting | 限流 |
| Cache | Cache | 缓存 |
| CDN | Content Delivery Network | 内容分发网络 |

---

## 项目管理术语

| 术语 | 英文 | 说明 |
|------|------|------|
| PM | Project Manager | 项目经理 |
| TL | Team Leader | 技术负责人/团队负责人 |
| DEV | Developer | 开发工程师 |
| QA | Quality Assurance | 测试工程师 |
| OPS | Operations | 运维工程师 |
| UAT | User Acceptance Testing | 用户验收测试 |
| SIT | System Integration Testing | 系统集成测试 |
| DEV | Development Environment | 开发环境 |
| TEST | Test Environment | 测试环境 |
| UAT | User Acceptance Test Environment | 用户验收测试环境 |
| PROD | Production Environment | 生产环境 |

---

## 问题诊断术语

| 术语 | 英文 | 说明 |
|------|------|------|
| Trace | Trace | 调用链追踪 |
| Span | Span | 调用单元 |
| Log | Log | 日志 |
| Stack Trace | Stack Trace | 堆栈追踪 |
| Heap Dump | Heap Dump | 堆转储 |
| Thread Dump | Thread Dump | 线程转储 |
| Slow Query | Slow Query | 慢查询 |
| Deadlock | Deadlock | 死锁 |
| Timeout | Timeout | 超时 |
| Retry | Retry | 重试 |
| Fallback | Fallback | 降级 |
| Circuit Open | Circuit Open | 熔断开启 |

---

## 常用计算公式

### ApDex 计算

```
ApDex = (T + 0.5×F) / N
其中：
- T = 满意请求数（响应时间 < 阈值）
- F = 容忍请求数（响应时间 > 阈值 且 < 4×阈值）
- N = 总请求数
```

### SLA 计算

```
SLA = (1 - 失败请求数 / 总请求数) × 100%
通常以月为单位计算
```

### 响应时间百分位

将所有响应时间从小到大排序：
- P50：第 50% 的位置
- P90：第 90% 的位置
- P99：第 99% 的位置
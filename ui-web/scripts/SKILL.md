---
name: apm-monitor
description: 应用性能监控（APM）工具，支持Web仪表板和CLI查询
---

# APM - 应用性能监控

应用性能监控工具，提供Web仪表板和CLI命令行查询，支持真实Prometheus数据采集或模拟测试。

## 快速开始

### Web仪表板

直接在浏览器中打开：
```
assets/apm-dashboard.html
```

### CLI命令行

```bash
# 查看帮助
python scripts/apm-cli.py --help

# 查看状态
python scripts/apm-cli.py status

# 查看告警
python scripts/apm-cli.py alerts

# 导出数据
python scripts/apm-cli.py export --format csv --output metrics.csv
```

---

## 功能

### CLI命令

| 命令 | 说明 |
|------|------|
| `status` | 查看状态概览 |
| `trend` | 查看指标趋势 |
| `alerts` | 检查告警 |
| `json` | 输出JSON格式 |
| `export` | 导出数据 |

### 指标类型

- **response_time**: 响应时间（ms）
- **request_count**: 请求量
- **error_rate**: 错误率（%）
- **throughput**: 吞吐量（req/s）

### 时间范围

- `1m` - 最近1分钟
- `5m` - 最近5分钟
- `15m` - 最近15分钟
- `1h` - 最近1小时
- `6h` - 最近6小时
- `24h` - 最近24小时

---

## 配置

### Prometheus连接

```bash
# 环境变量
export PROMETHEUS_URL="http://localhost:9090"

# 命令行参数
python scripts/apm-cli.py --prometheus http://localhost:9090 status
```

### 指标名称

修改 `scripts/prometheus.py` 中的指标名称配置以匹配你的自定义指标。

---

## 依赖

```bash
# 可选：requests库用于真实Prometheus查询
pip install requests
```

---

## 输出目录

- Web输出：`/assets/apm-dashboard.html`
- 导出数据：`/output/`（需创建）

---

## 示例

```bash
# 查看最近5分钟的状态
python scripts/apm-cli.py status --duration 5m

# 查看响应时间趋势
python scripts/apm-cli.py trend --metric response_time --duration 15m

# 导出JSON数据
python scripts/apm-cli.py json --duration 1h > apm_data.json

# 导出CSV
python scripts/apm-cli.py export --format csv --output metrics.csv
```
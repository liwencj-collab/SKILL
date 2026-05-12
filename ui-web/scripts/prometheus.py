#!/usr/bin/env python3
"""
APM数据采集模块 - 支持模拟数据和真实Prometheus查询
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

try:
    import requests
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class APMCollector:
    """APM指标采集器"""

    def __init__(self, prometheus_url: Optional[str] = None, use_mock: bool = True):
        self.prometheus_url = prometheus_url or os.environ.get("PROMETHEUS_URL")
        self.use_mock = use_mock or not self.prometheus_url

        if not self.use_mock and PROMETHEUS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({"Accept": "application/json"})
        else:
            self.session = None

    def _generate_mock_data(
        self,
        metric_name: str,
        duration_minutes: int = 60,
        interval_seconds: int = 30
    ) -> List[Dict[str, Any]]:
        """生成模拟数据"""
        data_points = []
        now = datetime.now()
        num_points = (duration_minutes * 60) // interval_seconds

        # 根据指标类型生成不同的模拟数据
        base_values = {
            "response_time": 150,      # 基础响应时间（ms）
            "request_count": 1000,     # 基础请求数
            "error_rate": 1.5,         # 基础错误率（%）
            "throughput": 50,           # 基础吞吐量（req/s）
        }

        if metric_name not in base_values:
            metric_name = "response_time"

        base = base_values[metric_name]

        for i in range(num_points):
            timestamp = int((now - timedelta(minutes=duration_minutes, seconds=i*interval_seconds)).timestamp() * 1000)

            # 添加随机波动
            if metric_name == "response_time":
                value = base + random.uniform(-50, 100)
                value = max(10, value)  # 最小10ms
            elif metric_name == "request_count":
                value = base // num_points + random.randint(-200, 300)
                value = max(0, value)
            elif metric_name == "error_rate":
                value = base + random.uniform(-1, 1.5)
                value = max(0, min(value, 10))  # 0-10%
            else:  # throughput
                value = base + random.uniform(-15, 20)
                value = max(0, value)

            data_points.append({
                "timestamp": timestamp,
                "value": round(value, 2)
            })

        return data_points

    def _query_prometheus(self, query: str) -> List[Dict[str, Any]]:
        """查询Prometheus API"""
        if not self.prometheus_url:
            raise ValueError("Prometheus URL not configured")

        url = f"{self.prometheus_url.rstrip('/')}/api/v1/query"
        params = {"query": query}

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("status") != "success":
            raise ValueError(f"Prometheus query failed: {data}")

        results = data.get("data", {}).get("result", [])
        return [
            {
                "timestamp": int(float(r.get("value", [0, 0])[0]) * 1000),
                "value": float(r.get("value", [0, 0])[1])
            }
            for r in results
        ]

    def get_metrics(
        self,
        metric_names: List[str],
        duration: str = "1h"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """获取指标数据

        Args:
            metric_names: 指标名称列表
            duration: 时间范围 (1m, 5m, 15m, 1h, 6h, 24h)

        Returns:
            指标数据字典 {metric_name: [data_points]}
        """
        # 解析时间范围
        duration_map = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "6h": 360,
            "24h": 1440
        }
        duration_minutes = duration_map.get(duration, 60)

        results = {}

        for metric_name in metric_names:
            if self.use_mock:
                results[metric_name] = self._generate_mock_data(
                    metric_name,
                    duration_minutes=duration_minutes
                )
            else:
                try:
                    results[metric_name] = self._query_prometheus(metric_name)
                except Exception as e:
                    print(f"Warning: Failed to query {metric_name}: {e}", file=sys.stderr)
                    results[metric_name] = []

        return results

    def get_summary(self, duration: str = "1h") -> Dict[str, Any]:
        """获取性能摘要"""
        metrics = self.get_metrics(
            ["response_time", "request_count", "error_rate", "throughput"],
            duration=duration
        )

        summary = {
            "timestamp": int(time.time() * 1000),
            "metrics": {}
        }

        for name, data in metrics.items():
            if not data:
                continue

            values = [d["value"] for d in data]
            current = values[-1] if values else 0

            if name == "response_time":
                summary["metrics"][name] = {
                    "current": round(current, 2),
                    "avg": round(sum(values) / len(values), 2),
                    "max": round(max(values), 2),
                    "min": round(min(values), 2),
                    "unit": "ms"
                }
            elif name == "request_count":
                summary["metrics"][name] = {
                    "current": int(current),
                    "total": int(sum(values)),
                    "unit": "requests"
                }
            elif name == "error_rate":
                summary["metrics"][name] = {
                    "current": round(current, 2),
                    "avg": round(sum(values) / len(values), 2),
                    "unit": "%"
                }
            elif name == "throughput":
                summary["metrics"][name] = {
                    "current": round(current, 2),
                    "avg": round(sum(values) / len(values), 2),
                    "unit": "req/s"
                }

        # 健康状态
        response_time = summary["metrics"].get("response_time", {})
        error_rate = summary["metrics"].get("error_rate", {})

        status = "healthy"
        if error_rate.get("current", 0) > 5 or response_time.get("current", 0) > 500:
            status = "critical"
        elif error_rate.get("current", 0) > 2 or response_time.get("current", 0) > 300:
            status = "warning"

        summary["status"] = status

        return summary


def main():
    parser = argparse.ArgumentParser(description="APM数据采集 CLI")
    parser.add_argument("--prometheus", type=str, help="Prometheus URL")
    parser.add_argument("--metrics", type=str, default="response_time,request_count,error_rate,throughput",
                        help="指标名称，逗号分隔")
    parser.add_argument("--duration", type=str, default="1h",
                        help="时间范围 (1m, 5m, 15m, 1h, 6h, 24h)")
    parser.add_argument("--output", type=str, choices=["json", "summary"], default="summary",
                        help="输出格式")
    parser.add_argument("--mock", action="store_true", default=True,
                        help="使用模拟数据")

    args = parser.parse_args()

    collector = APMCollector(prometheus_url=args.prometheus, use_mock=args.mock)

    metric_names = [m.strip() for m in args.metrics.split(",")]

    if args.output == "json":
        results = collector.get_metrics(metric_names, duration=args.duration)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        summary = collector.get_summary(duration=args.duration)
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
APM CLI - 应用性能监控命令行工具
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from prometheus import APMCollector


class APMCLI:
    """APM命令行工具"""

    def __init__(self, collector: APMCollector):
        self.collector = collector

    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    def print_status(self, summary: dict):
        """打印状态概览"""
        metrics = summary.get("metrics", {})
        status = summary.get("status", "unknown")

        status_emoji = {
            "healthy": "🟢",
            "warning": "🟡",
            "critical": "🔴"
        }

        print(f"\n{status_emoji.get(status, '⚪')} 应用状态: {status.upper()}")
        print(f"更新时间: {datetime.fromtimestamp(summary.get('timestamp', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 响应时间
        if "response_time" in metrics:
            rt = metrics["response_time"]
            print(f"📊 响应时间")
            print(f"   当前: {rt['current']:.2f} {rt['unit']}")
            print(f"   平均: {rt['avg']:.2f} {rt['unit']}")
            print(f"   最大: {rt['max']:.2f} {rt['unit']}")
            print(f"   最小: {rt['min']:.2f} {rt['unit']}")
            print()

        # 请求量
        if "request_count" in metrics:
            rc = metrics["request_count"]
            print(f"📨 请求量")
            print(f"   当前: {rc['current']:,} {rc['unit']}")
            print(f"   总计: {rc['total']:,} {rc['unit']}")
            print()

        # 错误率
        if "error_rate" in metrics:
            er = metrics["error_rate"]
            status_icon = "⚠️" if er["current"] > 2 else "✅"
            print(f"{status_icon} 错误率")
            print(f"   当前: {er['current']:.2f} {er['unit']}")
            print(f"   平均: {er['avg']:.2f} {er['unit']}")
            print()

        # 吞吐量
        if "throughput" in metrics:
            tp = metrics["throughput"]
            print(f"⚡ 吞吐量")
            print(f"   当前: {tp['current']:.2f} {tp['unit']}")
            print(f"   平均: {tp['avg']:.2f} {tp['unit']}")
            print()

    def print_trend(self, metrics: dict, metric_name: str):
        """打印趋势图表"""
        if metric_name not in metrics:
            return

        data = metrics[metric_name]
        if not data:
            return

        values = [d["value"] for d in data[-10:]]  # 最近10个点

        print(f"\n📈 {metric_name} 趋势 (最近10个数据点)")
        print("-" * 40)

        # 简单的ASCII条形图
        max_val = max(values) if max(values) > 0 else 1
        for i, v in enumerate(values):
            bar_len = int((v / max_val) * 30)
            bar = "█" * bar_len
            print(f"  {i+1:2d}: {bar} {v:.2f}")

    def check_alerts(self, summary: dict) -> list:
        """检查告警"""
        alerts = []
        metrics = summary.get("metrics", {})

        # 响应时间告警
        rt = metrics.get("response_time", {})
        current_rt = rt.get("current", 0)
        if current_rt > 500:
            alerts.append(("critical", f"响应时间过高: {current_rt:.2f}ms"))
        elif current_rt > 300:
            alerts.append(("warning", f"响应时间偏高: {current_rt:.2f}ms"))

        # 错误率告警
        er = metrics.get("error_rate", {})
        current_er = er.get("current", 0)
        if current_er > 5:
            alerts.append(("critical", f"错误率过高: {current_er:.2f}%"))
        elif current_er > 2:
            alerts.append(("warning", f"错误率偏高: {current_er:.2f}%"))

        return alerts

    def print_alerts(self, alerts: list):
        """打印告警"""
        if not alerts:
            print("\n✅ 无告警")
            return

        for level, message in alerts:
            icon = "🔴" if level == "critical" else "🟡"
            print(f"{icon} {message.upper()}: {message}")

    def export_json(self, summary: dict, filename: str):
        """导出JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"已导出到: {filename}")

    def export_csv(self, metrics: dict, filename: str):
        """导出CSV"""
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "metric", "value"])

            for metric_name, data in metrics.items():
                if not data:
                    continue
                for point in data:
                    timestamp = datetime.fromtimestamp(point["timestamp"]/1000).strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([timestamp, metric_name, point["value"]])

        print(f"已导出到: {filename}")

    def run(self, args):
        """运行CLI命令"""
        # 获取摘要数据
        summary = self.collector.get_summary(duration=args.duration)

        if args.command == "status":
            self.print_header("应用性能监控")
            self.print_status(summary)

        elif args.command == "trend":
            metric_name = args.metric
            metrics = self.collector.get_metrics([metric_name], duration=args.duration)
            self.print_header(f"{metric_name} 趋势")
            self.print_trend(metrics, metric_name)

        elif args.command == "alerts":
            self.print_header("告警检查")
            alerts = self.check_alerts(summary)
            self.print_alerts(alerts)

        elif args.command == "json":
            summary = self.collector.get_summary(duration=args.duration)
            print(json.dumps(summary, indent=2, ensure_ascii=False))

        elif args.command == "export":
            if args.format == "json":
                summary = self.collector.get_summary(duration=args.duration)
                self.export_json(summary, args.output)
            else:
                metrics = self.collector.get_metrics(
                    ["response_time", "request_count", "error_rate", "throughput"],
                    duration=args.duration
                )
                self.export_csv(metrics, args.output)


def main():
    parser = argparse.ArgumentParser(
        description="APM CLI - 应用性能监控命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s status                    查看状态概览
  %(prog)s trend --metric response_time  查看响应时间趋势
  %(prog)s alerts                    检查告警
  %(prog)s export --format csv --output metrics.csv  导出数据
        """
    )

    # 全局选项
    parser.add_argument("--prometheus", type=str, help="Prometheus URL")
    parser.add_argument("--duration", type=str, default="1h",
                        help="时间范围 (1m, 5m, 15m, 1h, 6h, 24h)")
    parser.add_argument("--mock", action="store_true", default=True,
                        help="使用模拟数据")

    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # status命令
    subparsers.add_parser("status", help="查看状态概览")

    # trend命令
    trend_parser = subparsers.add_parser("trend", help="查看趋势")
    trend_parser.add_argument("--metric", type=str, default="response_time",
                            help="指标名称")

    # alerts命令
    subparsers.add_parser("alerts", help="检查告警")

    # json命令
    subparsers.add_parser("json", help="输出JSON格式")

    # export命令
    export_parser = subparsers.add_parser("export", help="导出数据")
    export_parser.add_argument("--format", type=str, choices=["json", "csv"],
                                default="csv", help="导出格式")
    export_parser.add_argument("--output", type=str, default="metrics.csv",
                                help="输出文件")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 创建采集器
    collector = APMCollector(
        prometheus_url=args.prometheus,
        use_mock=args.mock
    )

    # 运行CLI
    cli = APMCLI(collector)
    cli.run(args)


if __name__ == "__main__":
    main()
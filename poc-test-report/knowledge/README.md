# 经验库

本文档是POC测试报告的经验库，用于存放历史报告模板和分析结果。

## 使用说明

- 将历史报告模板（PPT/PDF）放到对应目录下
- 运行 `scripts/analyze_template.py` 分析模板结构
- 分析结果会自动保存到 `templates/` 目录
- 生成新报告时调用保存的模板配置

## 目录结构

```
knowledge/
├── pentest/         # 渗透测试报告模板
│   └── templates/  # 分析后的模板配置
├── functional/    # 功能测试报告模板
│   └── templates/
├── performance/   # 性能测试报告模板
│   └── templates/
└── templates/    # 通用模板配置（JSON格式）
```

## 模板配置格式

```json
{
  "name": "模板名称",
  "version": "1.0",
  "layout": {
    "page_size": "A4",
    "orientation": "landscape",
    "margins": {"top": 20, "bottom": 20, "left": 30, "right": 30}
  },
  "title": {
    "level1": {"font_size": 24, "color": "#000000", "bold": true},
    "level2": {"font_size": 18, "color": "#333333", "bold": true},
    "level3": {"font_size": 14, "color": "#666666", "bold": false}
  },
  "table": {
    "header_bg": "#1e3a8a",
    "header_color": "#ffffff",
    "row_even": "#f3f4f6",
    "row_odd": "#ffffff"
  },
  "risk_colors": {
    "high": "#dc2626",
    "medium": "#f59e0b",
    "low": "#10b981"
  }
}
```
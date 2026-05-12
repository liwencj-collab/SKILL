#!/usr/bin/env python3
"""
生成技术/商务偏离表
根据招标要求生成偏离表，检查是否有偏离项。
"""

import json
import sys
from typing import Dict, Any, List

try:
    from docx import Document
    from docx.shared import Inches, Pt, Cm
except ImportError:
    print("请安装 python-docx: pip install python-docx")
    sys.exit(1)


def load_requirements(file_path: str) -> Dict[str, Any]:
    """加载招标要求"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_deviation(requirement: str, response: str) -> Dict[str, Any]:
    """分析偏离情况"""
    if not response:
        return {
            "requirement": requirement,
            "response": "",
            "deviation": "未响应",
            "deviation_type": "未偏离"
        }

    # 简单关键词匹配检测
    req_keywords = set(requirement.lower().split())
    resp_keywords = set(response.lower().split()) if response else set()

    matching = req_keywords & resp_keywords
    match_ratio = len(matching) / len(req_keywords) if req_keywords else 0

    if match_ratio >= 0.7:
        deviation_type = "完全响应"
        deviation = "无偏离"
    elif match_ratio >= 0.4:
        deviation_type = "部分偏离"
        deviation = "部分偏离"
    else:
        deviation_type = "偏离"
        deviation = "偏离"

    return {
        "requirement": requirement,
        "response": response,
        "deviation": deviation,
        "deviation_type": deviation_type
    }


def generate_technical_deviation_table(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成技术偏离表"""
    technical_deviations = []

    for req in requirements.get("technical_requirements", []):
        deviation = analyze_deviation(req, "")
        deviation["section"] = "技术要求"
        technical_deviations.append(deviation)

    return technical_deviations


def generate_business_deviation_table(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成商务偏离表"""
    business_deviations = []

    for req in requirements.get("business_requirements", []):
        deviation = analyze_deviation(req, "")
        deviation["section"] = "商务要求"
        business_deviations.append(deviation)

    return business_deviations


def generate_after_sales_deviation_table(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成售后偏离表"""
    after_sales_deviations = []

    for req in requirements.get("after_sales_requirements", []):
        deviation = analyze_deviation(req, "")
        deviation["section"] = "售后要求"
        after_sales_deviations.append(deviation)

    return after_sales_deviations


def create_deviation_docx(output_file: str, deviation_data: Dict[str, Any]) -> None:
    """创建偏离表 Word 文档"""
    doc = Document()

    # 添加标题
    title = doc.add_heading('技术/商务偏离表', 0)

    # 添加技术偏离表
    doc.add_heading('一、技术偏离表', 1)
    tech_table = doc.add_table(rows=1, cols=4)
    tech_table.style = 'Table Grid'

    # 表头
    headers = ["序号", "招标要求", "响应说明", "偏离情况"]
    for i, header in enumerate(headers):
        tech_table.rows[0].cells[i].text = header

    # 数据行
    for idx, item in enumerate(deviation_data.get("technical", [])):
        row = tech_table.add_row()
        row.cells[0].text = str(idx + 1)
        row.cells[1].text = item.get("requirement", "")
        row.cells[2].text = item.get("response", "")
        row.cells[3].text = item.get("deviation", "")

    # 添加商务偏离表
    doc.add_heading('二、商务偏离表', 1)
    biz_table = doc.add_table(rows=1, cols=4)
    biz_table.style = 'Table Grid'

    for i, header in enumerate(headers):
        biz_table.rows[0].cells[i].text = header

    for idx, item in enumerate(deviation_data.get("business", [])):
        row = biz_table.add_row()
        row.cells[0].text = str(idx + 1)
        row.cells[1].text = item.get("requirement", "")
        row.cells[2].text = item.get("response", "")
        row.cells[3].text = item.get("deviation", "")

    # 添加售后偏离表
    doc.add_heading('三、售后偏离表', 1)
    after_table = doc.add_table(rows=1, cols=4)
    after_table.style = 'Table Grid'

    for i, header in enumerate(headers):
        after_table.rows[0].cells[i].text = header

    for idx, item in enumerate(deviation_data.get("after_sales", [])):
        row = after_table.add_row()
        row.cells[0].text = str(idx + 1)
        row.cells[1].text = item.get("requirement", "")
        row.cells[2].text = item.get("response", "")
        row.cells[3].text = item.get("deviation", "")

    doc.save(output_file)
    print(f"偏离表已生成: {output_file}")


def main():
    if len(sys.argv) < 3:
        print("用法: python generate_deviation.py <招标要求.json> <输出文件>")
        sys.exit(1)

    requirements_file = sys.argv[1]
    output_file = sys.argv[2]

    requirements = load_requirements(requirements_file)

    deviation_data = {
        "technical": generate_technical_deviation_table(requirements),
        "business": generate_business_deviation_table(requirements),
        "after_sales": generate_after_sales_deviation_table(requirements)
    }

    # 检查是否有偏离
    total = len(deviation_data["technical"]) + len(deviation_data["business"]) + len(deviation_data["after_sales"])
    deviations = sum(1 for d in deviation_data["technical"] + deviation_data["business"] + deviation_data["after_sales"] if d.get("deviation") != "无偏离")

    save_data = {
        "summary": {
            "total": total,
            "deviations": deviations,
            "match_rate": f"{(total - deviations) / total * 100:.1f}%" if total > 0 else "N/A"
        },
        "data": deviation_data
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"偏离表已生成: {output_file}")
    print(f"统计: 共 {total} 项，偏离 {deviations} 项，匹配率 {save_data['summary']['match_rate']}")

    return save_data


if __name__ == "__main__":
    main()
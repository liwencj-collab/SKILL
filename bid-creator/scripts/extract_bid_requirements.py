#!/usr/bin/env python3
"""
提取招标文件要点
从 PDF 或 Word 文档中提取招标要求、评分标准、技术/商务要求等关键信息。
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import PyPDF2
except ImportError:
    print("请安装 PyPDF2: pip install PyPDF2")
    sys.exit(1)

try:
    from docx import Document
except ImportError:
    print("请安装 python-docx: pip install python-docx")
    sys.exit(1)


def extract_from_pdf(file_path: str) -> Dict[str, Any]:
    """从 PDF 提取文本"""
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def extract_from_docx(file_path: str) -> Dict[str, Any]:
    """从 Word 文档提取文本"""
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text += cell.text + "\n"
    return text


def parse_bid_requirements(text: str) -> Dict[str, Any]:
    """解析招标要求文本"""
    result = {
        "project_name": "",
        "basic_info": {},
        "technical_requirements": [],
        "business_requirements": [],
        "after_sales_requirements": [],
        "scoring_criteria": [],
        "other_requirements": []
    }

    lines = text.split('\n')

    # 提取项目名称
    for line in lines[:10]:
        if any(keyword in line for keyword in ["项目名称", "项目名称：", "项目编号"]):
            result["project_name"] = line.strip()
            break

    # 提取技术要求
    tech_keywords = ["技术要求", "技术需求", "功能要求", "系统要求", "技术参数"]
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in tech_keywords):
            # 提取接下来的内容作为技术要求
            j = i + 1
            while j < len(lines) and lines[j].strip():
                if any(end_keyword in lines[j] for end_keyword in ["商务要求", "售后要求", "评分标准"]):
                    break
                if lines[j].strip():
                    result["technical_requirements"].append(lines[j].strip())
                j += 1

    # 提取商务要求
    biz_keywords = ["商务要求", "资质要求", "企业资质"]
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in biz_keywords):
            j = i + 1
            while j < len(lines) and lines[j].strip():
                if any(end_keyword in lines[j] for end_keyword in ["技术要求", "售后要求", "评分标准"]):
                    break
                if lines[j].strip():
                    result["business_requirements"].append(lines[j].strip())
                j += 1

    # 提取售后要求
    after_keywords = ["售后服务", "售后要求", "维保", "质保"]
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in after_keywords):
            j = i + 1
            while j < len(lines) and lines[j].strip():
                if any(end_keyword in lines[j] for end_keyword in ["技术要求", "商务要求"]):
                    break
                if lines[j].strip():
                    result["after_sales_requirements"].append(lines[j].strip())
                j += 1

    # 提取评分标准
    scoring_keywords = ["评分标准", "打分", "评审", "评分办法"]
    current_section = []
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in scoring_keywords):
            j = i + 1
            while j < len(lines) and lines[j].strip():
                if lines[j].strip() and len(lines[j].strip()) > 5:
                    current_section.append(lines[j].strip())
                j += 1
            if current_section:
                result["scoring_criteria"].extend(current_section[:20])  # 限制数量

    return result


def extract_title_template(file_path: str) -> Dict[str, Any]:
    """从 Word 文档提取标题模板结构"""
    doc = Document(file_path)
    titles = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if para.style.name.startswith('Heading'):
            titles.append({
                "level": para.style.name,
                "text": text
            })

    return {"titles": titles}


def main():
    if len(sys.argv) < 3:
        print("用法: python extract_bid_requirements.py <招标文件> <输出文件>")
        print("或:  python extract_bid_requirements.py --template <标题模板> <输出文件>")
        sys.exit(1)

    if sys.argv[1] == "--template":
        template_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else "title_template.json"
        result = extract_title_template(template_file)
    else:
        bid_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "bid_requirements.json"

        # 根据文件扩展名选择解析方式
        ext = Path(bid_file).suffix.lower()
        if ext == '.pdf':
            text = extract_from_pdf(bid_file)
        elif ext in ['.docx', '.doc']:
            text = extract_from_docx(bid_file)
        else:
            print(f"不支持的文件格式: {ext}")
            sys.exit(1)

        result = parse_bid_requirements(text)

    # 输出结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"已提取内容并保存到: {output_file}")
    return result


if __name__ == "__main__":
    main()
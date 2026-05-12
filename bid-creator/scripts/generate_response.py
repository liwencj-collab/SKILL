#!/usr/bin/env python3
"""
生成投标响应内容
根据招标要求和用户提供的技术/商务内容，生成完整的响应描述。
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    from docx import Document
except ImportError:
    print("请安装 python-docx: pip install python-docx")
    sys.exit(1)


def load_requirements(file_path: str) -> Dict[str, Any]:
    """加载招标要求"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(file_path: str) -> Dict[str, Any]:
    """加载模板文件"""
    doc = Document(file_path)
    content = []

    for para in doc.paragraphs:
        if para.text.strip():
            content.append(para.text.strip())

    return {"content": content}


def map_template_to_sections(template: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
    """将模板内容映射到响应章节"""
    sections = {}

    template_text = "\n".join(template.get("content", []))

    # 映射技术要求
    for tech_req in requirements.get("technical_requirements", []):
        sections[f"技术响应_{tech_req[:50]}"] = {
            "requirement": tech_req,
            "response": "",
            "proof": ""
        }

    # 映射商务要求
    for biz_req in requirements.get("business_requirements", []):
        sections[f"商务响应_{biz_req[:50]}"] = {
            "requirement": biz_req,
            "response": "",
            "proof": ""
        }

    # 映射售后要求
    for after_req in requirements.get("after_sales_requirements", []):
        sections[f"售后响应_{after_req[:50]}"] = {
            "requirement": after_req,
            "response": "",
            "proof": ""
        }

    return sections


def generate_response_content(
    requirements: Dict[str, Any],
    user_content: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成响应内容结构"""
    response = {
        "project_name": requirements.get("project_name", ""),
        "sections": []
    }

    # 生成技术方案章节
    tech_sections = []
    for tech_req in requirements.get("technical_requirements", []):
        section = {
            "title": "技术响应",
            "requirement": tech_req,
            "response": user_content.get(tech_req, "") if user_content else "",
            "proof": ""
        }
        tech_sections.append(section)

    # 生成商务章节
    biz_sections = []
    for biz_req in requirements.get("business_requirements", []):
        section = {
            "title": "商务响应",
            "requirement": biz_req,
            "response": user_content.get(biz_req, "") if user_content else "",
            "proof": ""
        }
        biz_sections.append(section)

    # 生成售后章节
    after_sections = []
    for after_req in requirements.get("after_sales_requirements", []):
        section = {
            "title": "售后响应",
            "requirement": after_req,
            "response": user_content.get(after_req, "") if user_content else "",
            "proof": ""
        }
        after_sections.append(section)

    response["sections"] = tech_sections + biz_sections + after_sections
    return response


def generate_scoring_response(
    scoring_criteria: List[str],
    response_content: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """生成打分表响应"""
    scoring_responses = []

    for criteria in scoring_criteria:
        # 提取分值
        score_match = []
        if any(char.isdigit() for char in criteria):
            for i, char in enumerate(criteria):
                if char.isdigit():
                    score_match.append(char)

        response = {
            "criteria": criteria,
            "requirement": criteria,
            "response": "",
            "score": "".join(score_match[:2]) if score_match else "",
            "proof": ""
        }
        scoring_responses.append(response)

    return scoring_responses


def main():
    if len(sys.argv) < 3:
        print("用法: python generate_response.py <招标要求.json> <输出文件> [--content <用户内容>]")
        sys.exit(1)

    requirements_file = sys.argv[1]
    output_file = sys.argv[2]

    requirements = load_requirements(requirements_file)

    # 生成响应内容
    response = generate_response_content(requirements)

    # 生成打分表响应
    scoring_responses = generate_scoring_response(
        requirements.get("scoring_criteria", []),
        response
    )
    response["scoring"] = scoring_responses

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)

    print(f"响应内容已生成: {output_file}")
    return response


if __name__ == "__main__":
    main()
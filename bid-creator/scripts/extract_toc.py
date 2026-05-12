#!/usr/bin/env python3
import pdfplumber
import re

pdf_path = "/Users/qujinyu/Downloads/qiuzhi-skill-creator/bid-creator/招案2025-3326邮惠万家银行2025年移动应用性能监控系统工程采购项目（发售稿）0813.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # 技术规范书从第97页开始，商务规范书从第72页开始
    # 先看看目录确定页码
    print("=== 查找技术规范书和商务规范书 ===\n")

    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and ("第四章" in text or "第五章" in text or "技术规范书" in text or "商务规范书" in text):
            print(f"第{i+1}页: {text[:300]}")
            print("-"*30)
            if i > 10:
                break
#!/usr/bin/env python3
import pdfplumber
import sys

pdf_path = "/Users/qujinyu/Downloads/qiuzhi-skill-creator/bid-creator/招案2025-3326邮惠万家银行2025年移动应用性能监控系统工程采购项目（发售稿）0813.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"总页数: {len(pdf.pages)}")
    print("\n" + "="*50)

    # 提取前几页的文本
    for i, page in enumerate(pdf.pages[:5], 1):
        text = page.extract_text()
        if text:
            print(f"\n--- 第 {i} 页 ---")
            print(text[:2000] if len(text) > 2000 else text)
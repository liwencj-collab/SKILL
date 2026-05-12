#!/usr/bin/env python3
import pdfplumber

pdf_path = "/Users/qujinyu/Downloads/qiuzhi-skill-creator/bid-creator/招案2025-3326邮惠万家银行2025年移动应用性能监控系统工程采购项目（发售稿）0813.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print("="*60)
    print("【第五章 技术规范书】- 摘要（第97-110页）")
    print("="*60)

    # 提取第97-110页的内容
    for page_num in range(96, 115):  # 97-115页
        if page_num < len(pdf.pages):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if text:
                print(f"\n--- 第{page_num+1}页 ---")
                # 只打印非空行
                lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 5]
                for line in lines[:30]:  # 每页最多30行
                    print(line[:150])
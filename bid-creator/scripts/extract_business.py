#!/usr/bin/env python3
import pdfplumber

pdf_path = "/Users/qujinyu/Downloads/qiuzhi-skill-creator/bid-creator/招案2025-3326邮惠万家银行2025年移动应用性能监控系统工程采购项目（发售稿）0813.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # 根据目录，第四章商务规范书约在第72页，第五章技术规范书约在第97页
    # 提取第72-100页（商务规范书）和第97-140页（技术规范书）的内容

    print("="*60)
    print("【第四章 商务规范书】- 摘要")
    print("="*60)

    for page_num in range(71, 100):  # 72-100页
        if page_num < len(pdf.pages):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if text:
                # 只打印包含关键内容的部分
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10 and not line.startswith(' '):
                        print(line[:200])
        print(f"\n--- 第{page_num+1}页 ---\n")
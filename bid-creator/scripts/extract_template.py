#!/usr/bin/env python3
import pdfplumber

pdf_path = "/Users/qujinyu/Downloads/qiuzhi-skill-creator/bid-creator/标题模版.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"总页数: {len(pdf.pages)}")
    print("="*60)

    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            print(f"\n--- 第 {i+1} 页 ---")
            print(text)
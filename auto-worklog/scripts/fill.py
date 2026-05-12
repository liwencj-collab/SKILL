#!/usr/bin/env python3
"""自动填工时脚本"""

from playwright.sync_api import sync_playwright
import os
import datetime

# === 配置 ===
WORKLOG_URL = ""  # 工时系统网址，需要用户提供
USERNAME = ""    # 账号
PASSWORD = ""    # 密码

def main():
    if not WORKLOG_URL:
        print("请先配置工时系统网址和账号密码")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("打开工时系统...")
        page.goto(WORKLOG_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # 登录
        print("登录...")
        try:
            page.fill("input[placeholder*='用户名'], input[name*='user']", USERNAME)
            page.fill("input[type='password']", PASSWORD)
            page.click("button[type='submit'], button:has-text('登录')")
        except Exception as e:
            print(f"登录失败: {e}")

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # 截图
        desktop = os.path.expanduser("~/Desktop")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        page.screenshot(path=os.path.join(desktop, f"工时确认-{date_str}.png"), full_page=True)
        print(f"截图已保存")

        browser.close()

if __name__ == "__main__":
    main()
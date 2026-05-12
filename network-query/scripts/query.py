#!/usr/bin/env python3
"""直接截图当前页面"""

from playwright.sync_api import sync_playwright
import os
import datetime

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 直接访问Network控制台
        print("直接访问Network控制台...")
        page.goto("https://saas.tingyun.com")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        print("请在浏览器中手动登录并导航到使用量查询页面...")
        page.wait_for_timeout(120000)  # 等待2分钟让用户操作

        # 截图
        desktop = os.path.expanduser("~/Desktop")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        screenshot_path = os.path.join(desktop, f"network-剩余量-{date_str}.png")

        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n截图已保存到: {screenshot_path}")

        # 获取页面内容
        text = page.inner_text("body")
        print(f"\n页面内容:\n{text}")

        browser.close()
        print("\n完成！")

if __name__ == "__main__":
    main()
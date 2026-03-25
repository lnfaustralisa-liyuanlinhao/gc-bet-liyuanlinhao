import os
import json
import time
from playwright.sync_api import sync_playwright

def get_live_odds(url):
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 访问比赛页面
        page.goto(url, wait_until="networkidle")
        # 强制等待5秒，确保动态赔率加载出来
        time.sleep(5) 
        
        # 提取数据（这里先写一个通用的提取逻辑）
        results = {}
        # 查找所有的赔率按钮（TAB常用的类名是 .price-button 或类似）
        buttons = page.query_selector_all('button[data-automation-id^="price-button"]')
        
        for i, btn in enumerate(buttons):
            try:
                price = btn.inner_text().strip()
                if price and "$" not in price: # 确保抓到的是数字
                    results[str(i+1)] = float(price)
            except:
                continue
                
        browser.close()
        return results
    def compare_and_save(current_odds):
    # 1. 加载上次的赔率
    if os.path.exists(ODDS_HISTORY_FILE):
        with open(ODDS_HISTORY_FILE, "r") as f:
            old_odds = json.load(f)
    else:
        old_odds = {}

    # 2. 对比
    for runner, price in current_odds.items():
        if runner in old_odds:
            old_price = old_odds[runner]
            # 计算跌幅百分比
            drop_pct = (old_price - price) / old_price
            
            if drop_pct >= 0.10: # 如果跌幅超过 10%
                print(f"🔥 发现异动！{runner}号 赔率从 {old_price} 掉到 {price}！")
                # 这里之后我们会加 Telegram 提醒

    # 3. 保存本次赔率，留给下次对比
    with open(ODDS_HISTORY_FILE, "w") as f:
        json.dump(current_odds, f)
        if __name__ == "__main__":
    # 这里换成你想要监控的具体比赛 URL
    target_url = "https://www.tab.com.au/racing/next-to-go/greyhounds" 
    
    print("开始扫描...")
    live_data = get_live_odds(target_url)
    if live_data:
        compare_and_save(live_data)
        print("扫描完成并已记录。")
    else:
        print("未能获取到数据，请检查 URL 或网络。")

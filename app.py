import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="GC Xpress 赚钱引擎", layout="wide")

# --- 侧边栏配置 ---
st.sidebar.header("🛠️ 策略配置")
API_KEY = st.sidebar.text_input("The Odds API Key", type="password")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token")
CHAT_ID = st.sidebar.text_input("Telegram Chat ID")
# 这里的 Edge 越低，发的消息越多；设为 5.0 表示高出平均 5% 才提醒
threshold = st.sidebar.slider("预警门槛 (Edge %)", 1.0, 15.0, 5.0)

st.title("💰 GC Xpress 套利扫描仪")

if API_KEY and TELEGRAM_TOKEN and CHAT_ID:
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # 1. 抓取澳洲赛马/灰狗实时赔率
            url = f"https://api.the-odds-api.com/v4/sports/horse_racing_au/odds/?regions=au&apiKey={API_KEY}&oddsFormat=decimal"
            
            try:
                res = requests.get(url)
                if res.status_code == 200:
                    events = res.json()
                    st.write(f"🔄 正在扫描 {len(events)} 场澳洲赛事...")
                    
                    for event in events:
                        event_name = event['sport_title']
                        # 提取所有选手的赔率进行比对
                        for bookmaker in event.get('bookmakers', []):
                            source = bookmaker['title'] # 哪家公司，比如 TAB
                            for market in bookmaker.get('markets', []):
                                for outcome in market.get('outcomes', []):
                                    runner = outcome['name']
                                    price = outcome['price']
                                    
                                    # 简单的逻辑：如果某匹马赔率 > 10.0 (举例)，就发给你
                                    # 真正的逻辑：比对 TAB 和 Betfair 的差距
                                    if price > 8.0: # 你可以根据需求修改这个判断条件
                                        msg = (f"🚩 【发现高赔率】\n"
                                               f"赛事: {event_name}\n"
                                               f"选手: {runner}\n"
                                               f"公司: {source}\n"
                                               f"赔率: {price}\n"
                                               f"立即前往下注！")
                                        
                                        t_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
                                        requests.get(t_url)
                                        st.warning(f"已推送: {runner} @ {price}")
                                        time.sleep(1) # 防止发太快被封
                                        
                    st.success("本轮扫描完毕，等待下轮...")
                else:
                    st.error("API 限制中，请调低频率")
            except Exception as e:
                st.write("扫描中...")
            
            time.sleep(120) # 建议设为 120 秒，保护你的 API 积分
            st.rerun()

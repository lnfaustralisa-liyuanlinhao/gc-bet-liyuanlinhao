import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="GC Xpress 稳健版", layout="wide")

API_KEY = st.sidebar.text_input("The Odds API Key", type="password")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token")
CHAT_ID = st.sidebar.text_input("Telegram Chat ID")

st.title("💰 GC Xpress 套利扫描仪 (稳健版)")

# 增加一个手动刷新按钮，这样不消耗自动额度
if st.button('🎯 立即手动扫描一次'):
    st.rerun()

if API_KEY and TELEGRAM_TOKEN and CHAT_ID:
    # 路径换成澳洲赛马和灰狗
    url = f"https://api.the-odds-api.com/v4/sports/horse_racing_au/odds/?regions=au&apiKey={API_KEY}&oddsFormat=decimal"
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            events = res.json()
            st.success(f"✅ 扫描成功，发现 {len(events)} 场赛事")
            
            for event in events:
                for bookmaker in event.get('bookmakers', []):
                    for market in bookmaker.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            # 策略：只推赔率在 5.0 到 15.0 之间的，这些最容易出套利空间
                            if 5.0 <= outcome['price'] <= 15.0:
                                msg = f"🚩【机会】\n项目: {event['sport_title']}\n选手: {outcome['name']}\n公司: {bookmaker['title']}\n赔率: {outcome['price']}"
                                t_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
                                requests.get(t_url)
        elif res.status_code == 429:
            st.error("🚨 频率太快了！API 罢工中。请关掉网页等 5 分钟再开。")
    except Exception as e:
        st.write("等待中...")

    # 每 5 分钟自动跑一次，保护积分
    time.sleep(300)
    st.rerun()
